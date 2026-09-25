import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import measure_context_savings as measurement


class MeasurementTests(unittest.TestCase):
    def write_pair(
        self,
        directory: Path,
        identifier: str = "01",
        report: str = "# Worker report\n\nA nonempty finding.\n",
        receipt_overrides: dict | None = None,
    ) -> None:
        worker = directory / f"worker-{identifier}.md"
        worker.write_text(report, encoding="utf-8")
        receipt = {
            "status": "done",
            "report_path": str(worker.resolve()),
            "sources_reviewed": 1,
            "finding_count": 1,
            "evidence_count": 1,
            "coverage_complete": True,
            "report_bytes": len(report.encode("utf-8")),
            "gaps": [],
            **(receipt_overrides or {}),
        }
        (directory / f"receipt-{identifier}.json").write_text(
            json.dumps(receipt, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    def test_valid_zero_count_fixture_measures_intermediate_handoff_only(self):
        with tempfile.TemporaryDirectory(prefix="research-swarm-measure-") as directory:
            run_dir = Path(directory)
            report = "# Coverage\n\nNo material findings for this lane.\n"
            self.write_pair(
                run_dir,
                report=report,
                receipt_overrides={
                    "sources_reviewed": 0,
                    "finding_count": 0,
                    "evidence_count": 0,
                    "report_bytes": len(report.encode("utf-8")),
                },
            )
            result = measurement.calculate(run_dir, "o200k_base")
        self.assertEqual(result["scope"], "worker-to-main intermediate handoff only")
        self.assertEqual(
            result["cost_scope"],
            "not total API usage, billing, quota, or aggregate worker compute",
        )
        self.assertFalse(result["input_scope"]["runtime_lifecycle_verified"])
        self.assertFalse(result["input_scope"]["persistent_workflow_artifacts_authorized"])

    def test_missing_matching_or_malformed_inputs_are_rejected(self):
        cases = [
            ("missing artifacts", {}),
            ("identifier mismatch", {"identifiers": ("01", "02")}),
            ("malformed json", {"raw_receipt": "not-json"}),
            ("non-object receipt", {"raw_receipt": "[]"}),
            ("wrong count type", {"receipt_overrides": {"finding_count": "1"}}),
            ("wrong report path", {"receipt_overrides": {"report_path": "/tmp/other.md"}}),
            ("wrong report bytes", {"receipt_overrides": {"report_bytes": 1}}),
            ("empty report", {"report": "   \n"}),
        ]
        for name, options in cases:
            with self.subTest(name), tempfile.TemporaryDirectory(
                prefix="research-swarm-invalid-"
            ) as directory:
                run_dir = Path(directory)
                if options.get("identifiers"):
                    worker_id, receipt_id = options["identifiers"]
                    report = "# Worker report\n"
                    worker = run_dir / f"worker-{worker_id}.md"
                    worker.write_text(report, encoding="utf-8")
                    receipt = {
                        "status": "done",
                        "report_path": str(worker.resolve()),
                        "sources_reviewed": 0,
                        "finding_count": 0,
                        "evidence_count": 0,
                        "coverage_complete": True,
                        "report_bytes": len(report.encode("utf-8")),
                        "gaps": [],
                    }
                    (run_dir / f"receipt-{receipt_id}.json").write_text(
                        json.dumps(receipt), encoding="utf-8"
                    )
                elif "raw_receipt" in options:
                    self.write_pair(run_dir)
                    (run_dir / "receipt-01.json").write_text(
                        options["raw_receipt"], encoding="utf-8"
                    )
                elif options:
                    self.write_pair(run_dir, **options)
                with self.assertRaises(measurement.MeasurementError):
                    measurement.validate_run(run_dir)

    def test_validator_output_does_not_claim_runtime_lifecycle_verification(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_ephemeral_contract.py")],
            capture_output=True,
            text=True,
            check=True,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["scope"], "static documentation fragment checks only")
        self.assertFalse(result["runtime_lifecycle_verified"])


if __name__ == "__main__":
    unittest.main()
