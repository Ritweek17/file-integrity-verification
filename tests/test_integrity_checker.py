import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import integrity_checker as checker


class FileIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.target = self.root / "target"
        self.target.mkdir()
        (self.target / "keep.txt").write_text("unchanged", encoding="utf-8")
        (self.target / "edit.txt").write_text("before", encoding="utf-8")
        self.baseline = self.root / "baseline.json"
        checker.initialize_baseline(self.target, self.baseline)

    def tearDown(self):
        self.temp_dir.cleanup()

    def verify(self):
        report_path = self.root / "report.json"
        report = checker.verify_target(self.target, self.baseline, report_path)
        self.assertEqual(json.loads(report_path.read_text(encoding="utf-8")), report)
        return report["summary"]

    def test_unchanged_files(self):
        summary = self.verify()
        self.assertEqual(summary["UNCHANGED"], 2)
        self.assertEqual(summary["changes_detected"], 0)

    def test_modified_file(self):
        (self.target / "edit.txt").write_text("after", encoding="utf-8")
        summary = self.verify()
        self.assertEqual(summary["MODIFIED"], 1)

    def test_added_file(self):
        (self.target / "new.txt").write_text("new", encoding="utf-8")
        summary = self.verify()
        self.assertEqual(summary["ADDED"], 1)

    def test_deleted_file(self):
        (self.target / "keep.txt").unlink()
        summary = self.verify()
        self.assertEqual(summary["DELETED"], 1)

    def test_report_is_valid_json(self):
        summary = self.verify()
        self.assertIn("total_compared", summary)


if __name__ == "__main__":
    unittest.main()
