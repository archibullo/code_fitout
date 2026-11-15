import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ROOT / "code_fitout" / "code_fitout" / "doctype"
REPORTS = ROOT / "code_fitout" / "code_fitout" / "report"


class TestSourceStructure(unittest.TestCase):
    def test_doctypes(self):
        docs = {}
        for p in DOCS.glob("*/*.json"):
            d = json.loads(p.read_text(encoding="utf-8"))
            docs[d["name"]] = d
            self.assertEqual(d["module"], "Code Fitout")
            self.assertEqual(d["field_order"], [f["fieldname"] for f in d["fields"]])
            self.assertEqual(len(d["field_order"]), len(set(d["field_order"])))
            self.assertEqual(bool(d.get("istable")), not bool(d["permissions"]))
            self.assertTrue(p.with_suffix(".py").exists(), str(p))
        for required in ("CF Cost Record", "CF Payment", "CF Payment Allocation",
                         "CF Owner Movement", "CF BOQ", "CF Supervision Agreement",
                         "CF Work Order", "CF Site Visit", "CF Stage Template", "CF Stage Handover",
                         "CF Trade Handover", "CF Site Store", "CF Owner Material Movement"):
            self.assertIn(required, docs)
        for d in docs.values():
            for f in d["fields"]:
                if f["fieldtype"] == "Table":
                    self.assertIn(f["options"], docs)
                    self.assertEqual(docs[f["options"]]["istable"], 1)
                if f["fieldtype"] == "Link" and f.get("options", "").startswith("CF "):
                    self.assertIn(f["options"], docs)

    def test_reports(self):
        reports = list(REPORTS.glob("*/*.json"))
        self.assertEqual(len(reports), 9)
        for p in reports:
            d = json.loads(p.read_text())
            self.assertEqual(d["is_standard"], "Yes")
            self.assertTrue(p.with_suffix(".py").exists())
            self.assertTrue(p.with_suffix(".js").exists())

    def test_fixture(self):
        fields = json.loads((ROOT / "code_fitout/fixtures/custom_field.json").read_text())
        names = [x["fieldname"] for x in fields]
        self.assertEqual(len(names), len(set(names)))
        self.assertTrue(all(n.startswith("custom_cf_") for n in names))

    def test_readme_and_install_files(self):
        for path in ("README.md", "pyproject.toml", "LICENSE", "code_fitout/hooks.py",
                     "code_fitout/modules.txt", "code_fitout/setup/install.py", "docs/INSTALL.md"):
            self.assertTrue((ROOT/path).is_file())

    def test_fresh_install_has_no_legacy_migration(self):
        self.assertFalse((ROOT/'code_fitout/setup/legacy.py').exists())
        self.assertFalse((ROOT/'code_fitout/workspace_sidebar').exists())
        self.assertTrue((ROOT/'code_fitout/public/images/fitout-mark.svg').exists())
