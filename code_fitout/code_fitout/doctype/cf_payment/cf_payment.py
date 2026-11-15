import frappe
from frappe import _
from frappe.model.document import Document
from code_fitout.finance import (
    cost_paid, lock_costs, lock_project, money, owner_balances, positive,
    validate_funding,
)


class CFPayment(Document):
    def before_validate(self):
        allocated = money(0)
        for row in self.payment_allocations or []:
            allocated += money(row.allocated_amount)
        self.total_allocated = float(allocated)
        self.unallocated_amount = float(money(self.amount) - allocated)

    def validate(self):
        payment = positive(self.amount, "Payment amount")
        validate_funding(self.paid_by, self.funding_source)
        if not self.supplier:
            frappe.throw(_("Supplier is required."))
        if self.funding_source in {"Owner Funds Already Received", "Personal Funds - Recoverable"} and not self.project:
            frappe.throw(_("A Project is required for this funding source."))
        seen = set()
        allocated = money(0)
        projects = set()
        for row in self.payment_allocations or []:
            if not row.cost_record or row.cost_record in seen:
                frappe.throw(_("A Cost Record is missing or duplicated in allocations."))
            seen.add(row.cost_record)
            allocated += positive(row.allocated_amount, "Allocated amount")
            cost = frappe.db.get_value("CF Cost Record", row.cost_record,
                ["project", "supplier", "docstatus", "amount"], as_dict=True)
            if not cost or cost.supplier != self.supplier:
                frappe.throw(_("Cost record does not exist or belongs to another supplier."))
            if int(cost.docstatus) != 1:
                frappe.throw(_("Only submitted cost records may receive allocations."))
            if self.project and cost.project != self.project:
                frappe.throw(_("Allocated cost belongs to another project."))
            row.project = cost.project
            projects.add(cost.project)
        if allocated > payment:
            frappe.throw(_("Allocations exceed Payment Amount."))
        if payment - allocated > 0 and not self.project:
            frappe.throw(_("Project is required for unallocated advances."))
        if self.funding_source in {"Owner Funds Already Received", "Personal Funds - Recoverable"} and len(projects) > 1:
            frappe.throw(_("Owner-held or personal funding must be recorded per project. Split the transfer into project-specific payments."))
        if self.funding_source == "Owner Paid Directly" and len(projects) > 1:
            customers = {frappe.db.get_value("Project", p, "customer") for p in projects}
            if None in customers or len(customers) != 1:
                frappe.throw(_("One direct owner payment cannot cover projects of different owners."))
        if not self.project and projects and len(projects) == 1:
            # Keep the operational project populated when payment is for one project.
            self.project = next(iter(projects))
        self.total_allocated = float(allocated)
        self.unallocated_amount = float(payment - allocated)

    def before_submit(self):
        if self.funding_source == "Other / To Be Verified":
            frappe.throw(_("An unverified source cannot be submitted."))
        # Serialize submitted payments per payee for duplicate reference checks,
        # even when different projects share the same bank transfer reference.
        frappe.db.sql("SELECT name FROM `tabSupplier` WHERE name=%s FOR UPDATE", (self.supplier,))
        # Lock all project rows in a stable order, so owner balance checks serialize.
        projects = sorted({x.project for x in (self.payment_allocations or []) if x.project}
                          | ({self.project} if self.project else set()))
        for project in projects:
            lock_project(project)
        lock_costs([x.cost_record for x in (self.payment_allocations or []) if x.cost_record])
        if self.transfer_reference:
            dup = frappe.db.sql("""
                SELECT name FROM `tabCF Payment`
                WHERE supplier=%s AND payment_method=%s
                  AND transfer_reference=%s AND docstatus=1 AND name!=%s
                LIMIT 1
            """, (self.supplier, self.payment_method, self.transfer_reference, self.name or ""))
            if dup:
                frappe.throw(_("Transfer reference already used in submitted payment {0}.").format(dup[0][0]))
        # Re-run checks AFTER obtaining locks; earlier validate() may have raced.
        self.validate()
        for row in self.payment_allocations or []:
            already = cost_paid(row.cost_record, excluding=self.name)
            available = money(frappe.db.get_value("CF Cost Record", row.cost_record, "amount")) - already
            if money(row.allocated_amount) > available:
                frappe.throw(_("Allocation exceeds outstanding approved cost {0}.").format(row.cost_record))
        if self.funding_source == "Owner Funds Already Received":
            held, _ = owner_balances(self.project)
            if money(self.amount) > held:
                frappe.throw(_("Insufficient owner funds held for this project."))

    def before_cancel(self):
        projects = sorted({x.project for x in (self.payment_allocations or []) if x.project}
                          | ({self.project} if self.project else set()))
        for project in projects:
            lock_project(project)
        if self.funding_source == "Personal Funds - Recoverable":
            # Removing a personal advance cannot strand previously posted reimbursements.
            _, recoverable = owner_balances(self.project)
            if recoverable - money(self.amount) < 0:
                frappe.throw(_("Cannot cancel: personal reimbursements would exceed advances."))
