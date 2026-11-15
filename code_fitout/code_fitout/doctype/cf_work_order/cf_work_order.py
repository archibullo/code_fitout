import frappe
from frappe import _
from frappe.model.document import Document
from code_fitout.finance import money, positive


class CFWorkOrder(Document):
    def validate(self):
        positive(self.base_amount, "Contract amount")
        total = money(self.base_amount) + money(self.variation_amount)
        if total <= 0:
            frappe.throw(_("Contract total must be greater than zero."))
        if self.retention_percent and not 0 <= float(self.retention_percent) <= 100:
            frappe.throw(_("Retention percentage must be between 0 and 100."))
        if self.start_date and self.end_date and self.end_date < self.start_date:
            frappe.throw(_("End date precedes start date."))
        self.committed_amount = float(total)

    def before_cancel(self):
        frappe.db.sql("SELECT name FROM `tabCF Work Order` WHERE name=%s FOR UPDATE", (self.name,))
        if frappe.db.exists("CF Cost Record", {"work_order": self.name, "docstatus": 1}):
            frappe.throw(_("Cannot cancel work order with submitted costs. Cancel linked costs first."))
