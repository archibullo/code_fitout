import frappe
from frappe import _
from frappe.model.document import Document
from code_fitout.finance import money, positive
from decimal import Decimal


class CFBOQ(Document):
    def validate(self):
        total = money(0)
        for row in self.boq_lines or []:
            qty = row.qty or 0
            if float(qty) <= 0:
                frappe.throw(_("BOQ quantities must be greater than zero."))
            rate = positive(row.rate, "BOQ rate")
            row.amount = float(money(rate * Decimal(str(qty))))
            total += money(row.amount)
        self.total_budget = float(total)

    def before_submit(self):
        if not self.boq_lines:
            frappe.throw(_("BOQ must contain at least one line."))
