"""Smoke tests for the curriculum coverage file and validation scripts.

Run: python -m unittest discover -s tests -v
"""
import subprocess
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
COVERAGE = ROOT / "curriculum" / "coverage.yaml"


class CoverageFileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = yaml.safe_load(COVERAGE.read_text(encoding="utf-8"))
        cls.topics = [t for d in cls.data["domains"] for t in d["topics"]]

    def test_all_thirty_domains_present(self):
        ids = [d["id"] for d in self.data["domains"]]
        self.assertEqual(ids, [f"D{n:02d}" for n in range(1, 31)])

    def test_topic_ids_unique_and_well_formed(self):
        ids = [t["id"] for t in self.topics]
        self.assertEqual(len(ids), len(set(ids)))
        for tid in ids:
            self.assertRegex(tid, r"^D\d{2}-T\d{2}$")

    def test_statuses_valid(self):
        for t in self.topics:
            self.assertIn(t["status"], self.data["status_values"], t["id"])

    def test_non_planned_topics_have_existing_pages(self):
        for t in self.topics:
            if t["status"] != "Planned":
                self.assertTrue((ROOT / t["destination"]).is_file(), f"{t['id']} -> {t['destination']}")

    def test_every_section_has_an_index_page(self):
        for d in self.data["domains"]:
            self.assertTrue((ROOT / "docs" / d["section"] / "index.md").is_file(), d["id"])


class ScriptTests(unittest.TestCase):
    def run_script(self, *args):
        return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True)

    def test_validate_content_passes(self):
        result = self.run_script("scripts/validate-content.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_coverage_outputs_up_to_date(self):
        result = self.run_script("scripts/build-coverage.py", "--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_assets_registered(self):
        result = self.run_script("scripts/check-assets.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
