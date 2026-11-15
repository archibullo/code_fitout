import frappe
from frappe import _
from frappe.model.document import Document
from code_fitout.finance import lock_project, money, owner_balances, positive

RECEIVED = "Owner Advance Received"
REFUND = "Refund to Owner"
HELD_REIMB = "Personal Advance Reimbursement - From Held Funds"
DIRECT_REIMB = "Personal Advance Reimbursement - Owner Directly"
TRANSFER = "Transfer Held Funds to Another Project"
KINDS = {RECEIVED, REFUND, HELD_REIMB, DIRECT_REIMB, TRANSFER}


class CFOwnerMovement(Document):
    def validate(self):
        if self.movement_type not in KINDS:
            frappe.throw(_("Invalid owner fund movement type."))
        positive(self.amount, "Owner movement amount")
        if not self.project:
            frappe.throw(_("Project is required."))
        if self.movement_type == TRANSFER:
            if not self.target_project or self.target_project == self.project:
                frappe.throw(_("Select a different target project for transfer."))
            a = frappe.db.get_value("Project", self.project, "customer")
            b = frappe.db.get_value("Project", self.target_project, "customer")
            if not a or a != b:
                frappe.throw(_("Both projects must belong to the same identified owner."))
        elif self.target_project:
            frappe.throw(_("Target Project is only used for inter-project transfers."))

    def _lock_projects(self):
        for p in sorted({self.project} | ({self.target_project} if self.target_project else set())):
            lock_project(p)

    def _check_reference(self):
        if self.transfer_reference:
            duplicate = frappe.db.sql("""
                SELECT name FROM `tabCF Owner Movement`
                WHERE project=%s AND movement_type=%s AND transfer_reference=%s
                AND docstatus=1 AND name!=%s LIMIT 1
            """, (self.project, self.movement_type, self.transfer_reference, self.name or ''))
            if duplicate:
                frappe.throw(_("Owner movement reference already submitted ({0}).").format(duplicate[0][0]))

    def before_submit(self):
        self._lock_projects()
        self.validate()
        self._check_reference()
        held, recoverable = owner_balances(self.project)
        amt = money(self.amount)
        if self.movement_type in {REFUND, HELD_REIMB, TRANSFER} and amt > held:
            frappe.throw(_("Insufficient owner funds held for this movement."))
        if self.movement_type in {HELD_REIMB, DIRECT_REIMB} and amt > recoverable:
            frappe.throw(_("Reimbursement exceeds personal advances recoverable."))

    def before_cancel(self):
        self._lock_projects()
        held, recoverable = owner_balances(self.project)
        amt = money(self.amount)
        if self.movement_type == RECEIVED and held - amt < 0:
            frappe.throw(_("Cannot cancel receipt: owner funds would become negative."))
        if self.movement_type == TRANSFER:
            target_held, _ = owner_balances(self.target_project)
            if target_held - amt < 0:
                frappe.throw(_("Cannot cancel transfer: target project has spent the transferred funds."))
