import importlib
import sys
import types
import unittest


class TestFinanceHelpers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous = sys.modules.get("frappe")
        fake = types.ModuleType("frappe")
        fake._ = lambda s: s
        fake.throw = lambda message: (_ for _ in ()).throw(ValueError(message))
        sys.modules["frappe"] = fake
        sys.modules.pop("code_fitout.finance", None)
        cls.finance = importlib.import_module("code_fitout.finance")

    @classmethod
    def tearDownClass(cls):
        sys.modules.pop("code_fitout.finance", None)
        if cls.previous is None:
            sys.modules.pop("frappe", None)
        else:
            sys.modules["frappe"] = cls.previous

    def test_money(self):
        self.assertEqual(str(self.finance.money("1.005")), "1.01")
        self.assertEqual(str(self.finance.money("700") + self.finance.money("300")), "1000.00")
        for invalid in ("0", "-5"):
            with self.assertRaises(ValueError):
                self.finance.positive(invalid)

    def test_valid_and_invalid_funding(self):
        self.finance.validate_funding("Property Owner", "Owner Paid Directly")
        self.finance.validate_funding("Me Personally", "Owner Funds Already Received")
        self.finance.validate_funding("Me Personally", "Personal Funds - Recoverable")
        with self.assertRaises(ValueError):
            self.finance.validate_funding("Property Owner", "Personal Funds - Recoverable")
