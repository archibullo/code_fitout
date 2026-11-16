"""Standalone regression checks for initialization timing (no ERPNext install needed).

These tests mock Frappe; they cannot replace a live fresh-site integration test.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SETUP_PATH = ROOT / "code_fitout" / "setup" / "install.py"
HOOKS_PATH = ROOT / "code_fitout" / "hooks.py"
GROUPS = {"Fitout Contractors", "Material Suppliers", "Site Services"}


class FakeDocument:
    def __init__(self, values, database, callback):
        self.data = dict(values)
        self.db = database
        self.callback = callback
        self.name = values.get("supplier_group_name", values.get("name"))

    def get(self, key, default=None):
        return self.data.get(key, default)

    def insert(self, ignore_permissions=False, **kwargs):
        doctype = self.data["doctype"]
        if self.name in self.db.rows.setdefault(doctype, set()):
            raise AssertionError("Non-idempotent duplicate insert: " + str(self.name))
        self.db.rows[doctype].add(self.name)
        if doctype == "Supplier Group":
            self.callback(self, "on_update")
        return self


class FakeDatabase:
    def __init__(self):
        self.rows = {"DocType": {"Supplier Group"}, "Supplier Group": set()}

    def exists(self, doctype, name):
        return name if name in self.rows.get(doctype, set()) else None

    def count(self, doctype):
        return len(self.rows.get(doctype, set()))


class TestSetupLifecycle(unittest.TestCase):
    def setUp(self):
        self.db = FakeDatabase()
        frappe = types.ModuleType("frappe")
        frappe.db = self.db
        frappe._ = lambda text: text
        self.callbacks = []
        self.setup_module = None

        def get_doc(values):
            if values["doctype"] != "Supplier Group":
                raise AssertionError("Unexpected creation: " + str(values))
            return FakeDocument(values, self.db, self.setup_module.on_supplier_group_updated)

        frappe.get_doc = get_doc
        self.fake_frappe = frappe
        self.module_patch = patch.dict(sys.modules, {"frappe": frappe})
        self.module_patch.start()
        spec = importlib.util.spec_from_file_location("code_fitout_setup_lifecycle_test", SETUP_PATH)
        self.setup_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.setup_module)

    def tearDown(self):
        self.module_patch.stop()

    def test_missing_erpnext_root_does_not_create_dummy_root_or_children(self):
        self.setup_module.seed_supplier_groups()
        self.assertEqual(self.db.rows["Supplier Group"], set())

    def test_late_company_creation_repairs_missing_groups(self):
        self.db.rows["Supplier Group"].add("All Supplier Groups")
        self.setup_module.on_company_created(types.SimpleNamespace(name="C.O.D.E."))
        self.assertEqual(self.db.rows["Supplier Group"], GROUPS | {"All Supplier Groups"})
        self.setup_module.seed_supplier_groups()
        self.setup_module.on_company_created(types.SimpleNamespace(name="Other Company"))
        self.assertEqual(self.db.rows["Supplier Group"], GROUPS | {"All Supplier Groups"})

    def test_root_group_creation_event_repairs_when_company_exists_first(self):
        self.db.rows["Supplier Group"].add("All Supplier Groups")
        root = FakeDocument({"doctype": "Supplier Group", "supplier_group_name": "All Supplier Groups", "is_group": 1}, self.db, None)
        self.setup_module.on_supplier_group_updated(root, "on_update")
        self.assertEqual(self.db.rows["Supplier Group"], GROUPS | {"All Supplier Groups"})
        leaf = FakeDocument({"doctype": "Supplier Group", "supplier_group_name": "Unrelated", "is_group": 0}, self.db, None)
        self.setup_module.on_supplier_group_updated(leaf, "on_update")
        self.assertEqual(self.db.rows["Supplier Group"], GROUPS | {"All Supplier Groups"})

    def test_exists_supplier_group_is_not_overwritten(self):
        self.db.rows["Supplier Group"].update({"All Supplier Groups", "Fitout Contractors"})
        self.setup_module.seed_supplier_groups()
        self.assertEqual(self.db.rows["Supplier Group"], GROUPS | {"All Supplier Groups"})

    def test_registered_frappe_lifecycle_hooks(self):
        source = HOOKS_PATH.read_text(encoding="utf-8")
        self.assertIn('setup_wizard_complete = "code_fitout.setup.install.after_setup_wizard"', source)
        self.assertIn('"after_insert": "code_fitout.setup.install.on_company_created"', source)
        self.assertIn('"on_update": "code_fitout.setup.install.on_supplier_group_updated"', source)
        self.assertIn('after_migrate = "code_fitout.setup.install.after_migrate"', source)
        self.assertIn('"route": "/desk/code-fitout/c.o.d.e.-fitout-management"', source)

    def test_setup_diagnostic_is_read_only(self):
        self.db.rows["Supplier Group"].add("All Supplier Groups")
        status = self.setup_module.setup_status()
        self.assertTrue(status["supplier_root_exists"])
        self.assertFalse(any(status["supplier_groups"].values()))
        self.assertFalse(status["instapay_exists"])
        self.assertEqual(self.db.rows["Supplier Group"], {"All Supplier Groups"})


if __name__ == "__main__":
    unittest.main()
