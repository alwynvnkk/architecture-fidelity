#!/usr/bin/env python3
"""Maintain Architecture Fidelity's repository-side project ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


SCHEMA_VERSION = 1
DEFAULT_LEDGER = Path(".architecture-fidelity/ledger.json")
FINDING_STATUSES = {"open", "accepted", "planned", "resolved", "dismissed", "reopened"}
SEVERITIES = {"high", "medium", "low", "opportunity"}
LANDMARK_KINDS = {
    "canonical-owner",
    "dependency-rule",
    "extension-seam",
    "domain-vocabulary",
    "approved-analogue",
}


class LedgerError(ValueError):
    """Raised when a ledger or delta violates the contract."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_git(root: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise LedgerError(detail)
    return result.stdout.strip()


def repository_root(start: Path) -> Path:
    return Path(run_git(start, "rev-parse", "--show-toplevel")).resolve()


def ledger_path(root: Path, override: str | None) -> Path:
    candidate = Path(override) if override else DEFAULT_LEDGER
    return candidate if candidate.is_absolute() else root / candidate


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise LedgerError(f"ledger not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise LedgerError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise LedgerError("ledger root must be an object")
    return value


def write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, sort_keys=False) + "\n"
    handle, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as temporary:
            temporary.write(payload)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.chmod(temporary_name, 0o644)
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def require_object(value: Any, location: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise LedgerError(f"{location} must be an object")
    return value


def require_list(value: Any, location: str) -> list[Any]:
    if not isinstance(value, list):
        raise LedgerError(f"{location} must be an array")
    return value


def require_text(value: Any, location: str, *, optional: bool = False) -> str | None:
    if optional and value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise LedgerError(f"{location} must be a non-empty string")
    return value


def validate_commit(value: Any, location: str) -> None:
    require_text(value, location, optional=True)


def validate_anchor(anchor: Any, location: str) -> None:
    item = require_object(anchor, location)
    raw_path = require_text(item.get("path"), f"{location}.path")
    assert raw_path is not None
    path = PurePosixPath(raw_path)
    if (
        raw_path == "."
        or "\\" in raw_path
        or path.is_absolute()
        or ".." in path.parts
        or raw_path.startswith("./")
    ):
        raise LedgerError(f"{location}.path must be a normalized repository-relative path")
    require_text(item.get("symbol"), f"{location}.symbol", optional=True)


def validate_landmark(item: Any, location: str) -> None:
    landmark = require_object(item, location)
    require_text(landmark.get("id"), f"{location}.id")
    kind = require_text(landmark.get("kind"), f"{location}.kind")
    if kind not in LANDMARK_KINDS:
        raise LedgerError(f"{location}.kind must be one of {sorted(LANDMARK_KINDS)}")
    require_text(landmark.get("statement"), f"{location}.statement")
    anchors = require_list(landmark.get("anchors"), f"{location}.anchors")
    if not anchors:
        raise LedgerError(f"{location}.anchors must contain at least one anchor")
    for index, anchor in enumerate(anchors):
        validate_anchor(anchor, f"{location}.anchors[{index}]")
    validate_commit(landmark.get("first_seen_commit"), f"{location}.first_seen_commit")
    validate_commit(landmark.get("last_verified_commit"), f"{location}.last_verified_commit")


def validate_finding(item: Any, location: str) -> None:
    finding = require_object(item, location)
    require_text(finding.get("id"), f"{location}.id")
    fingerprint = require_text(finding.get("fingerprint"), f"{location}.fingerprint")
    if fingerprint is None or len(fingerprint) != 64 or any(char not in "0123456789abcdef" for char in fingerprint):
        raise LedgerError(f"{location}.fingerprint must be a lowercase SHA-256 hex digest")
    status = require_text(finding.get("status"), f"{location}.status")
    if status not in FINDING_STATUSES:
        raise LedgerError(f"{location}.status must be one of {sorted(FINDING_STATUSES)}")
    severity = require_text(finding.get("severity"), f"{location}.severity")
    if severity not in SEVERITIES:
        raise LedgerError(f"{location}.severity must be one of {sorted(SEVERITIES)}")
    for field in ("category", "summary", "invariant", "impact", "correction"):
        require_text(finding.get(field), f"{location}.{field}")
    anchors = require_list(finding.get("anchors"), f"{location}.anchors")
    if not anchors:
        raise LedgerError(f"{location}.anchors must contain at least one anchor")
    for index, anchor in enumerate(anchors):
        validate_anchor(anchor, f"{location}.anchors[{index}]")
    validate_commit(finding.get("first_seen_commit"), f"{location}.first_seen_commit")
    validate_commit(finding.get("last_verified_commit"), f"{location}.last_verified_commit")
    events = require_list(finding.get("events", []), f"{location}.events")
    for index, event_value in enumerate(events):
        event = require_object(event_value, f"{location}.events[{index}]")
        event_status = require_text(event.get("status"), f"{location}.events[{index}].status")
        if event_status not in FINDING_STATUSES:
            raise LedgerError(
                f"{location}.events[{index}].status must be one of {sorted(FINDING_STATUSES)}"
            )
        require_text(event.get("at"), f"{location}.events[{index}].at")
        require_text(event.get("reason"), f"{location}.events[{index}].reason")
        validate_commit(event.get("commit"), f"{location}.events[{index}].commit")
    if status != "open" and not events:
        raise LedgerError(f"{location}.events must explain the current {status} status")
    if events and events[-1]["status"] != status:
        raise LedgerError(f"{location}.events[-1].status must match the current status")
    for field in ("owner", "external_ref"):
        require_text(finding.get(field), f"{location}.{field}", optional=True)


def validate_ledger(ledger: dict[str, Any]) -> None:
    if ledger.get("schema_version") != SCHEMA_VERSION:
        raise LedgerError(f"schema_version must be {SCHEMA_VERSION}")
    project = require_object(ledger.get("project"), "project")
    require_text(project.get("name"), "project.name")
    audit = require_object(ledger.get("audit"), "audit")
    validate_commit(audit.get("last_complete_commit"), "audit.last_complete_commit")
    require_text(audit.get("completed_at"), "audit.completed_at", optional=True)
    landmarks = require_list(ledger.get("landmarks"), "landmarks")
    findings = require_list(ledger.get("findings"), "findings")
    history = require_list(ledger.get("history"), "history")

    landmark_ids: set[str] = set()
    for index, landmark in enumerate(landmarks):
        validate_landmark(landmark, f"landmarks[{index}]")
        landmark_id = landmark["id"]
        if landmark_id in landmark_ids:
            raise LedgerError(f"duplicate landmark id: {landmark_id}")
        landmark_ids.add(landmark_id)

    finding_ids: set[str] = set()
    fingerprints: set[str] = set()
    for index, finding in enumerate(findings):
        validate_finding(finding, f"findings[{index}]")
        finding_id = finding["id"]
        fingerprint = finding["fingerprint"]
        if finding_id in finding_ids:
            raise LedgerError(f"duplicate finding id: {finding_id}")
        if fingerprint in fingerprints:
            raise LedgerError(f"duplicate finding fingerprint: {fingerprint}")
        finding_ids.add(finding_id)
        fingerprints.add(fingerprint)

    for index, event_value in enumerate(history):
        event = require_object(event_value, f"history[{index}]")
        require_text(event.get("completed_at"), f"history[{index}].completed_at")
        mode = require_text(event.get("mode"), f"history[{index}].mode")
        if mode not in {"full", "incremental"}:
            raise LedgerError(f"history[{index}].mode must be 'full' or 'incremental'")
        validate_commit(event.get("base_commit"), f"history[{index}].base_commit")
        validate_commit(event.get("commit"), f"history[{index}].commit")
        require_list(event.get("scope", []), f"history[{index}].scope")


def normalize(value: str) -> str:
    return " ".join(value.lower().split())


def finding_fingerprint(category: str, invariant: str, anchors: list[dict[str, Any]]) -> str:
    normalized_anchors = sorted(
        f"{anchor['path'].strip()}::{(anchor.get('symbol') or '').strip()}" for anchor in anchors
    )
    material = "\n".join([normalize(category), normalize(invariant), *normalized_anchors])
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def changed_files(root: Path, baseline: str) -> tuple[bool, list[str]]:
    available = subprocess.run(
        ["git", "cat-file", "-e", f"{baseline}^{{commit}}"],
        cwd=root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode == 0
    if not available:
        return False, []
    committed = run_git(root, "diff", "--name-only", f"{baseline}..HEAD", check=True).splitlines()
    working = run_git(root, "diff", "--name-only", "HEAD", check=True).splitlines()
    untracked = run_git(root, "ls-files", "--others", "--exclude-standard", check=True).splitlines()
    return True, sorted({path for path in [*committed, *working, *untracked] if path})


def anchor_is_changed(anchor: dict[str, Any], changed: set[str]) -> bool:
    path = anchor["path"].rstrip("/")
    return any(candidate == path or candidate.startswith(f"{path}/") for candidate in changed)


def audit_plan(root: Path, ledger: dict[str, Any]) -> dict[str, Any]:
    baseline = ledger["audit"]["last_complete_commit"]
    if baseline is None:
        return {
            "ledger_exists": True,
            "baseline": None,
            "baseline_available": None,
            "full_scan_required": True,
            "reason": "the ledger has no completed audit baseline",
            "changed_files": [],
            "landmarks_to_consult": [item["id"] for item in ledger["landmarks"]],
            "landmarks_to_revalidate": [item["id"] for item in ledger["landmarks"]],
            "findings_to_revalidate": [item["id"] for item in ledger["findings"]],
            "carried_findings": [],
        }

    available, paths = changed_files(root, baseline)
    if not available:
        return {
            "ledger_exists": True,
            "baseline": baseline,
            "baseline_available": False,
            "full_scan_required": True,
            "reason": "the recorded baseline is unavailable in this Git checkout",
            "changed_files": [],
            "landmarks_to_consult": [item["id"] for item in ledger["landmarks"]],
            "landmarks_to_revalidate": [item["id"] for item in ledger["landmarks"]],
            "findings_to_revalidate": [item["id"] for item in ledger["findings"]],
            "carried_findings": [],
        }

    changed = set(paths)
    landmarks = [
        item["id"]
        for item in ledger["landmarks"]
        if any(anchor_is_changed(anchor, changed) for anchor in item["anchors"])
    ]
    findings = [
        item["id"]
        for item in ledger["findings"]
        if any(anchor_is_changed(anchor, changed) for anchor in item["anchors"])
    ]
    carried = [
        item["id"]
        for item in ledger["findings"]
        if item["id"] not in findings and item["status"] in {"open", "accepted", "planned", "reopened"}
    ]
    return {
        "ledger_exists": True,
        "baseline": baseline,
        "baseline_available": True,
        "full_scan_required": False,
        "reason": None,
        "changed_files": paths,
        "landmarks_to_consult": [item["id"] for item in ledger["landmarks"]],
        "landmarks_to_revalidate": landmarks,
        "findings_to_revalidate": findings,
        "carried_findings": carried,
    }


def next_finding_id(findings: list[dict[str, Any]]) -> str:
    numbers = []
    for finding in findings:
        identifier = finding.get("id", "")
        if identifier.startswith("AF-") and identifier[3:].isdigit():
            numbers.append(int(identifier[3:]))
    return f"AF-{max(numbers, default=0) + 1:04d}"


def upsert_landmarks(ledger: dict[str, Any], values: list[Any]) -> None:
    by_id = {item["id"]: item for item in ledger["landmarks"]}
    for index, value in enumerate(values):
        landmark = require_object(value, f"delta.landmarks[{index}]")
        validate_landmark(landmark, f"delta.landmarks[{index}]")
        by_id[landmark["id"]] = landmark
    ledger["landmarks"] = list(by_id.values())


def upsert_findings(ledger: dict[str, Any], values: list[Any], now: str) -> list[str]:
    by_id = {item["id"]: item for item in ledger["findings"]}
    by_fingerprint = {item["fingerprint"]: item for item in ledger["findings"]}
    added: list[str] = []
    for index, value in enumerate(values):
        incoming = dict(require_object(value, f"delta.findings[{index}]"))
        anchors = require_list(incoming.get("anchors"), f"delta.findings[{index}].anchors")
        if not incoming.get("fingerprint"):
            incoming["fingerprint"] = finding_fingerprint(
                require_text(incoming.get("category"), f"delta.findings[{index}].category") or "",
                require_text(incoming.get("invariant"), f"delta.findings[{index}].invariant") or "",
                anchors,
            )
        id_match = by_id.get(incoming.get("id"))
        fingerprint_match = by_fingerprint.get(incoming["fingerprint"])
        if id_match and fingerprint_match and id_match["id"] != fingerprint_match["id"]:
            raise LedgerError(
                f"delta.findings[{index}] id and fingerprint refer to different existing findings"
            )
        if id_match and id_match["fingerprint"] != incoming["fingerprint"]:
            raise LedgerError(
                f"delta.findings[{index}] cannot change the fingerprint of {id_match['id']}"
            )
        existing = id_match or fingerprint_match
        transition_reason = incoming.pop("transition_reason", None)
        if existing:
            identifier = existing["id"]
            first_seen = existing["first_seen_commit"]
            events = list(existing.get("events", []))
            if incoming.get("status", existing["status"]) != existing["status"]:
                if not transition_reason:
                    raise LedgerError(
                        f"delta.findings[{index}].transition_reason is required when status changes"
                    )
                events.append(
                    {
                        "status": incoming.get("status"),
                        "at": now,
                        "commit": incoming.get("last_verified_commit"),
                        "reason": transition_reason,
                    }
                )
            incoming = {**existing, **incoming, "id": identifier, "first_seen_commit": first_seen, "events": events}
        else:
            identifier = incoming.get("id") or next_finding_id(list(by_id.values()))
            if identifier in by_id:
                raise LedgerError(f"delta.findings[{index}] duplicates finding id {identifier}")
            incoming["id"] = identifier
            incoming.setdefault("events", [])
            added.append(identifier)
        validate_finding(incoming, f"delta.findings[{index}]")
        by_id[identifier] = incoming
        by_fingerprint[incoming["fingerprint"]] = incoming
    ledger["findings"] = list(by_id.values())
    return added


def apply_delta(ledger: dict[str, Any], delta: dict[str, Any]) -> dict[str, Any]:
    now = delta.get("completed_at") or utc_now()
    previous_status = {item["id"]: item["status"] for item in ledger["findings"]}
    upsert_landmarks(ledger, require_list(delta.get("landmarks", []), "delta.landmarks"))
    added = upsert_findings(ledger, require_list(delta.get("findings", []), "delta.findings"), now)
    audit = require_object(delta.get("audit"), "delta.audit")
    mode = require_text(audit.get("mode"), "delta.audit.mode")
    if mode not in {"full", "incremental"}:
        raise LedgerError("delta.audit.mode must be 'full' or 'incremental'")
    commit = require_text(audit.get("commit"), "delta.audit.commit")
    base_commit = audit.get("base_commit")
    validate_commit(base_commit, "delta.audit.base_commit")
    scope = require_list(audit.get("scope", []), "delta.audit.scope")
    for index, path in enumerate(scope):
        require_text(path, f"delta.audit.scope[{index}]")
    # Status-derived lists are useful to humans; exact transition detail remains on each finding.
    resolved = [
        item["id"]
        for item in ledger["findings"]
        if item["status"] == "resolved" and previous_status.get(item["id"]) != "resolved"
    ]
    reopened = [
        item["id"]
        for item in ledger["findings"]
        if item["status"] == "reopened" and previous_status.get(item["id"]) != "reopened"
    ]
    ledger["audit"] = {"last_complete_commit": commit, "completed_at": now}
    ledger["history"].append(
        {
            "completed_at": now,
            "mode": mode,
            "base_commit": base_commit,
            "commit": commit,
            "scope": scope,
            "new_findings": added,
            "resolved_findings": resolved,
            "reopened_findings": reopened,
        }
    )
    ledger["history"] = ledger["history"][-20:]
    validate_ledger(ledger)
    return ledger


def empty_ledger(root: Path) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "project": {"name": root.name},
        "audit": {"last_complete_commit": None, "completed_at": None},
        "landmarks": [],
        "findings": [],
        "history": [],
    }


def command_init(args: argparse.Namespace) -> int:
    root = repository_root(Path(args.root).resolve())
    path = ledger_path(root, args.ledger)
    if path.exists():
        raise LedgerError(f"refusing to overwrite existing ledger: {path}")
    ledger = empty_ledger(root)
    validate_ledger(ledger)
    write_json_atomic(path, ledger)
    print(path.relative_to(root))
    return 0


def command_validate(args: argparse.Namespace) -> int:
    root = repository_root(Path(args.root).resolve())
    path = ledger_path(root, args.ledger)
    validate_ledger(load_json(path))
    print(f"valid: {path.relative_to(root)}")
    return 0


def command_plan(args: argparse.Namespace) -> int:
    root = repository_root(Path(args.root).resolve())
    path = ledger_path(root, args.ledger)
    if not path.exists():
        plan = {
            "ledger_exists": False,
            "baseline": None,
            "baseline_available": None,
            "full_scan_required": True,
            "reason": "no project ledger exists",
            "changed_files": [],
            "landmarks_to_consult": [],
            "landmarks_to_revalidate": [],
            "findings_to_revalidate": [],
            "carried_findings": [],
        }
    else:
        ledger = load_json(path)
        validate_ledger(ledger)
        plan = audit_plan(root, ledger)
    print(json.dumps(plan, indent=2))
    return 0


def command_fingerprint(args: argparse.Namespace) -> int:
    anchors = []
    for value in args.anchor:
        path, separator, symbol = value.partition("::")
        anchor = {"path": path}
        if separator and symbol:
            anchor["symbol"] = symbol
        validate_anchor(anchor, "anchor")
        anchors.append(anchor)
    print(finding_fingerprint(args.category, args.invariant, anchors))
    return 0


def command_apply(args: argparse.Namespace) -> int:
    root = repository_root(Path(args.root).resolve())
    path = ledger_path(root, args.ledger)
    # The first authorized audit of a repository creates the ledger, so memory
    # starts on the scan that has evidence rather than a separate setup step.
    created = not path.exists()
    ledger = empty_ledger(root) if created else load_json(path)
    validate_ledger(ledger)
    delta = load_json(Path(args.delta).resolve())
    updated = apply_delta(ledger, delta)
    write_json_atomic(path, updated)
    print(f"{'created' if created else 'updated'}: {path.relative_to(root)}")
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--root", default=".", help="path inside the target Git repository")
    result.add_argument("--ledger", help=f"ledger path (default: {DEFAULT_LEDGER})")
    commands = result.add_subparsers(dest="command", required=True)
    commands.add_parser("init", help="create an empty project ledger").set_defaults(handler=command_init)
    commands.add_parser("validate", help="validate the project ledger").set_defaults(handler=command_validate)
    commands.add_parser("plan", help="calculate the next incremental audit scope").set_defaults(handler=command_plan)

    fingerprint = commands.add_parser("fingerprint", help="create a stable finding fingerprint")
    fingerprint.add_argument("--category", required=True)
    fingerprint.add_argument("--invariant", required=True)
    fingerprint.add_argument(
        "--anchor",
        action="append",
        required=True,
        help="repository path, optionally followed by ::symbol; repeat for multiple anchors",
    )
    fingerprint.set_defaults(handler=command_fingerprint)

    apply = commands.add_parser(
        "apply-delta",
        help="merge an authorized audit delta, creating the ledger when absent",
    )
    apply.add_argument("--delta", required=True, help="path to the audit delta JSON")
    apply.set_defaults(handler=command_apply)
    return result


def main() -> int:
    try:
        args = parser().parse_args()
        return args.handler(args)
    except (LedgerError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
