import frappe
from frappe import _
from frappe.model.document import Document
from code_fitout.finance import money, lock_costs, cost_paid, positive


class CFCostRecord(Document):
    def validate(self):
        positive(self.amount, "Cost amount")
        if self.accounting_document and not frappe.db.exists("Purchase Invoice", self.accounting_document):
            frappe.throw(_("Linked ERPNext invoice does not exist."))
        if self.boq:
            b = frappe.db.get_value("CF BOQ", self.boq, ["project", "docstatus"], as_dict=True)
            if not b or b.project != self.project or b.docstatus != 1:
                frappe.throw(_("BOQ must be submitted and belong to the same project."))
        if self.work_order:
            order = frappe.db.get_value("CF Work Order", self.work_order,
                ["project", "supplier", "docstatus", "committed_amount", "allow_overrun"], as_dict=True)
            if not order or order.project != self.project or order.supplier != self.supplier:
                frappe.throw(_("Work order must match project and supplier."))
            if order.docstatus != 1:
                frappe.throw(_("Work order must be submitted before its costs."))

    def before_submit(self):
        if self.financial_responsibility == "To Be Determined":
            frappe.throw(_("Specify financial responsibility before approving costs."))
        positive(self.amount, "Cost amount")
        if self.work_order:
            # Serialize costs submitted against the same commitment.
            frappe.db.sql("SELECT name FROM `tabCF Work Order` WHERE name=%s FOR UPDATE", (self.work_order,))
            self.validate()
            order = frappe.db.get_value("CF Work Order", self.work_order,
                ["committed_amount", "allow_overrun"], as_dict=True)
            if not order.allow_overrun:
                used = frappe.db.sql("""
                    SELECT COALESCE(SUM(amount),0) FROM `tabCF Cost Record`
                    WHERE work_order=%s AND docstatus=1 AND name!=%s
                """, (self.work_order,self.name))[0][0]
                if money(used) + money(self.amount) > money(order.committed_amount):
                    frappe.throw(_("Approved costs exceed work order total. Amend the contract/variation first."))

    def before_cancel(self):
        lock_costs([self.name])
        if cost_paid(self.name) > 0:
            frappe.throw(_("Cannot cancel cost with submitted payments. Cancel/reverse them first."))
