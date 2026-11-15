import frappe
from frappe import _
from frappe.model.document import Document


class CFSupervisor(Document):
    def validate(self):
        if not (self.supervisor_name or '').strip():
            frappe.throw(_("Supervisor Name is required."))
        if self.user:
            enabled = frappe.db.get_value('User', self.user, 'enabled')
            if not enabled:
                frappe.throw(_("Linked ERPNext user must be enabled."))
            existing = frappe.db.get_value('CF Supervisor', {'user': self.user}, 'name')
            if existing and existing != self.name:
                frappe.throw(_("The ERPNext user is already linked to another supervisor."))
        if self.supplier and not frappe.db.exists('Supplier', self.supplier):
            frappe.throw(_("Linked supplier was not found."))
