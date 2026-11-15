from frappe import _
import frappe
from frappe.model.document import Document
from code_fitout.finance import money


class CFSupervisionAgreement(Document):
    def validate(self):
        project_customer = frappe.db.get_value("Project", self.project, "customer")
        if not project_customer or self.customer != project_customer:
            frappe.throw(_("Agreement customer must match the Project customer."))
        if self.linked_sales_invoice:
            invoice_customer = frappe.db.get_value("Sales Invoice", self.linked_sales_invoice, "customer")
            if not invoice_customer or invoice_customer != self.customer:
                frappe.throw(_("Linked Sales Invoice customer does not match."))
        if self.fee_basis == "Fixed":
            fee = money(self.fixed_fee)
        else:
            fee = money(money(self.budget_basis) * money(self.fee_percent) / 100)
        if fee < 0:
            frappe.throw(_("Supervision fee cannot be negative."))
        self.agreed_fee = float(fee)
        if self.linked_sales_invoice and not frappe.db.exists("Sales Invoice", self.linked_sales_invoice):
            frappe.throw(_("Linked Sales Invoice not found."))

    def before_submit(self):
        if money(self.agreed_fee) <= 0:
            frappe.throw(_("A positive agreed supervision fee is required."))
