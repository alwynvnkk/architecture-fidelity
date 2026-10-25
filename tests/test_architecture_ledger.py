from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).parents[1]
    / "skills"
    / "architecture-fidelity"
    / "scripts"
    / "architecture_ledger.py"
)
SPEC = importlib.util.spec_from_file_location("architecture_ledger", SCRIPT)
assert SPEC and SPEC.loader
ledger_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ledger_module)


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()


class ArchitectureLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.email", "test@example.com")
        git(self.root, "config", "user.name", "Test")
        (self.root / "src").mkdir()
        (self.root / "src/service.py").write_text("VALUE = 1\n", encoding="utf-8")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "initial")
        self.commit = git(self.root, "rev-parse", "HEAD")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def audit_delta(self, **audit: object) -> dict:
        base: dict = {
            "mode": "incremental",
            "base_commit": self.commit,
            "commit": self.commit,
            "scope": ["src/service.py"],
        }
        base.update(audit)
        return {"completed_at": "2026-08-30T13:00:00Z", "audit": base}

    def test_incremental_delta_does_not_claim_a_complete_audit(self) -> None:
        # audit_plan computes the next scope as baseline..HEAD, so a targeted
        # pass that moved the baseline would hide everything changed before it.
        ledger = self.ledger()
        ledger["audit"] = {"last_complete_commit": None, "completed_at": None}

        updated = ledger_module.apply_delta(ledger, self.audit_delta())

        self.assertIsNone(updated["audit"]["last_complete_commit"])
        self.assertFalse(updated["history"][-1]["complete"])

    def test_delta_advances_the_baseline_only_when_coverage_is_asserted(self) -> None:
        for audit in ({"complete": True}, {"mode": "full"}):
            with self.subTest(audit=audit):
                ledger = self.ledger()
                ledger["audit"] = {"last_complete_commit": None, "completed_at": None}

                updated = ledger_module.apply_delta(ledger, self.audit_delta(**audit))

                self.assertEqual(updated["audit"]["last_complete_commit"], self.commit)
                self.assertTrue(updated["history"][-1]["complete"])

        ledger = self.ledger()
        with self.assertRaises(ledger_module.LedgerError):
            ledger_module.apply_delta(ledger, self.audit_delta(complete="yes"))

    def ledger(self) -> dict:
        return {
            "schema_version": 1,
            "project": {"name": "example"},
            "audit": {"last_complete_commit": self.commit, "completed_at": "2026-08-30T12:00:00Z"},
            "landmarks": [
                {
                    "id": "owner-service",
                    "kind": "canonical-owner",
                    "statement": "The service owns the policy",
                    "anchors": [{"path": "src/service.py", "symbol": "VALUE"}],
                    "first_seen_commit": self.commit,
                    "last_verified_commit": self.commit,
                }
            ],
            "findings": [],
            "history": [],
        }

    def test_init_and_validate(self) -> None:
        path = self.root / ".architecture-fidelity/ledger.json"
        empty = {
            "schema_version": 1,
            "project": {"name": "example"},
            "audit": {"last_complete_commit": None, "completed_at": None},
            "landmarks": [],
            "findings": [],
            "history": [],
        }
        ledger_module.validate_ledger(empty)
        ledger_module.write_json_atomic(path, empty)
        self.assertEqual(json.loads(path.read_text())["schema_version"], 1)

    def test_plan_targets_changed_anchors(self) -> None:
        ledger = self.ledger()
        finding = {
            "id": "AF-0001",
            "fingerprint": ledger_module.finding_fingerprint(
                "boundary", "Domain stays transport-independent", [{"path": "src/service.py"}]
            ),
            "status": "resolved",
            "severity": "high",
            "category": "boundary",
            "summary": "Transport leaked into the domain",
            "invariant": "Domain stays transport-independent",
            "impact": "Core policy depends on transport",
            "correction": "Move the adapter outward",
            "anchors": [{"path": "src/service.py"}],
            "first_seen_commit": self.commit,
            "last_verified_commit": self.commit,
            "events": [
                {
                    "status": "resolved",
                    "at": "2026-08-30T12:00:00Z",
                    "commit": self.commit,
                    "reason": "The adapter was moved outward",
                }
            ],
        }
        ledger["findings"].append(finding)
        (self.root / "src/service.py").write_text("VALUE = 2\n", encoding="utf-8")

        plan = ledger_module.audit_plan(self.root, ledger)

        self.assertFalse(plan["full_scan_required"])
        self.assertEqual(plan["changed_files"], ["src/service.py"])
        self.assertEqual(plan["landmarks_to_consult"], ["owner-service"])
        self.assertEqual(plan["landmarks_to_revalidate"], ["owner-service"])
        self.assertEqual(plan["findings_to_revalidate"], ["AF-0001"])

    def test_delta_reuses_fingerprint_and_records_transition(self) -> None:
        ledger = self.ledger()
        anchors = [{"path": "src/service.py", "symbol": "VALUE"}]
        fingerprint = ledger_module.finding_fingerprint("domain-model", "Use a closed type", anchors)
        initial = {
            "id": "AF-0001",
            "fingerprint": fingerprint,
            "status": "open",
            "severity": "medium",
            "category": "domain-model",
            "summary": "Closed values use raw strings",
            "invariant": "Use a closed type",
            "impact": "Callers repeat validation",
            "correction": "Introduce the repository enum equivalent",
            "anchors": anchors,
            "first_seen_commit": self.commit,
            "last_verified_commit": self.commit,
            "events": [],
        }
        ledger["findings"].append(initial)
        delta = {
            "completed_at": "2026-08-30T13:00:00Z",
            "audit": {
                "mode": "incremental",
                "base_commit": self.commit,
                "commit": self.commit,
                "scope": ["src/service.py"],
            },
            "findings": [
                {
                    **initial,
                    "id": "AF-9999",
                    "status": "resolved",
                    "transition_reason": "The raw strings were replaced",
                }
            ],
        }

        updated = ledger_module.apply_delta(ledger, delta)

        self.assertEqual(len(updated["findings"]), 1)
        self.assertEqual(updated["findings"][0]["id"], "AF-0001")
        self.assertEqual(updated["findings"][0]["status"], "resolved")
        self.assertEqual(updated["findings"][0]["events"][0]["reason"], "The raw strings were replaced")

    def test_delta_rejects_reusing_an_id_for_a_different_finding(self) -> None:
        ledger = self.ledger()
        existing = {
            "id": "AF-0001",
            "fingerprint": ledger_module.finding_fingerprint(
                "domain-model", "Use a closed type", [{"path": "src/service.py"}]
            ),
            "status": "open",
            "severity": "medium",
            "category": "domain-model",
            "summary": "Closed values use raw strings",
            "invariant": "Use a closed type",
            "impact": "Callers repeat validation",
            "correction": "Introduce the repository enum equivalent",
            "anchors": [{"path": "src/service.py"}],
            "first_seen_commit": self.commit,
            "last_verified_commit": self.commit,
            "events": [],
        }
        ledger["findings"].append(existing)
        conflicting = {
            **existing,
            "fingerprint": ledger_module.finding_fingerprint(
                "dependency", "Core stays framework independent", [{"path": "src/service.py"}]
            ),
        }
        delta = {
            "audit": {
                "mode": "incremental",
                "base_commit": self.commit,
                "commit": self.commit,
                "scope": ["src/service.py"],
            },
            "findings": [conflicting],
        }

        with self.assertRaises(ledger_module.LedgerError):
            ledger_module.apply_delta(ledger, delta)

    def test_status_transition_requires_a_reason(self) -> None:
        ledger = self.ledger()
        finding = {
            "id": "AF-0001",
            "fingerprint": ledger_module.finding_fingerprint(
                "domain-model", "Use a closed type", [{"path": "src/service.py"}]
            ),
            "status": "open",
            "severity": "medium",
            "category": "domain-model",
            "summary": "Closed values use raw strings",
            "invariant": "Use a closed type",
            "impact": "Callers repeat validation",
            "correction": "Introduce the repository enum equivalent",
            "anchors": [{"path": "src/service.py"}],
            "first_seen_commit": self.commit,
            "last_verified_commit": self.commit,
            "events": [],
        }
        ledger["findings"].append(finding)
        delta = {
            "audit": {
                "mode": "incremental",
                "base_commit": self.commit,
                "commit": self.commit,
                "scope": ["src/service.py"],
            },
            "findings": [{**finding, "status": "resolved"}],
        }

        with self.assertRaises(ledger_module.LedgerError):
            ledger_module.apply_delta(ledger, delta)

    def test_fingerprint_preserves_path_and_symbol_case(self) -> None:
        lower = ledger_module.finding_fingerprint(
            "boundary", "One owner", [{"path": "src/service.py", "symbol": "save"}]
        )
        upper = ledger_module.finding_fingerprint(
            "boundary", "One owner", [{"path": "src/Service.py", "symbol": "Save"}]
        )

        self.assertNotEqual(lower, upper)

    def apply_delta_cli(self, delta: dict) -> str:
        delta_path = self.root / "delta.json"
        delta_path.write_text(json.dumps(delta), encoding="utf-8")
        return subprocess.run(
            ["python3", str(SCRIPT), "--root", str(self.root), "apply-delta", "--delta", str(delta_path)],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout.strip()

    def seed_delta(self) -> dict:
        return {
            "audit": {"mode": "full", "base_commit": None, "commit": self.commit, "scope": ["src/service.py"]},
            "landmarks": [
                {
                    "id": "owner-service",
                    "kind": "canonical-owner",
                    "statement": "The service owns the policy",
                    "anchors": [{"path": "src/service.py", "symbol": "VALUE"}],
                    "first_seen_commit": self.commit,
                    "last_verified_commit": self.commit,
                }
            ],
        }

    def test_apply_delta_creates_the_ledger_on_a_first_scan(self) -> None:
        path = self.root / ".architecture-fidelity/ledger.json"
        self.assertFalse(path.exists())

        output = self.apply_delta_cli(self.seed_delta())

        self.assertTrue(output.startswith("created:"), output)
        written = json.loads(path.read_text())
        ledger_module.validate_ledger(written)
        self.assertEqual([item["id"] for item in written["landmarks"]], ["owner-service"])
        self.assertEqual(written["audit"]["last_complete_commit"], self.commit)
        self.assertEqual(written["project"]["name"], self.root.name)

    def test_apply_delta_reports_an_update_for_an_existing_ledger(self) -> None:
        path = self.root / ".architecture-fidelity/ledger.json"
        existing = self.ledger()
        existing["landmarks"][0]["id"] = "owner-existing"
        ledger_module.write_json_atomic(path, existing)

        output = self.apply_delta_cli(self.seed_delta())

        self.assertTrue(output.startswith("updated:"), output)
        written = json.loads(path.read_text())
        ledger_module.validate_ledger(written)
        self.assertEqual(
            sorted(item["id"] for item in written["landmarks"]),
            ["owner-existing", "owner-service"],
        )

    def test_init_still_refuses_to_overwrite_an_existing_ledger(self) -> None:
        path = self.root / ".architecture-fidelity/ledger.json"
        ledger_module.write_json_atomic(path, self.ledger())

        result = subprocess.run(
            ["python3", str(SCRIPT), "--root", str(self.root), "init"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing to overwrite", result.stderr)


if __name__ == "__main__":
    unittest.main()
