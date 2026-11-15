import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate
from code_fitout.finance import money


class CFSupervisorAssignment(Document):
    def validate(self):
        if not frappe.db.exists('Project', self.project):
            frappe.throw(_("Please select a valid Project."))
        if not frappe.db.get_value('CF Supervisor', self.supervisor, 'active'):
            frappe.throw(_("Supervisor is inactive or does not exist."))
        if self.end_date and getdate(self.end_date) < getdate(self.start_date):
            frappe.throw(_("Assignment end date cannot precede its start date."))
        if self.mode == 'Resident':
            days = int(self.resident_days_per_week or 0)
            if not 1 <= days <= 7:
                frappe.throw(_("Resident supervisor requires expected site days between 1 and 7 per week."))
            if self.fee_basis == 'Per Visit':
                frappe.throw(_("Use a Monthly or Fixed fee for Resident supervision; visit-based fees belong to Visits assignments."))
        elif self.mode == 'Visits':
            if self.visit_plan == 'Scheduled' and int(self.visits_per_month or 0) <= 0:
                frappe.throw(_("Scheduled visits require a positive planned visits per month."))
            if int(self.visits_per_month or 0) < 0:
                frappe.throw(_("Planned visits cannot be negative."))
        else:
            frappe.throw(_("Supervision Mode must be Resident or Visits."))
        amounts = {'Monthly Fee': self.monthly_fee,
                   'Per Visit': self.per_visit_fee,
                   'Fixed Fee': self.fixed_fee}
        if self.fee_basis not in ('No Separate Fee', *amounts):
            frappe.throw(_("Invalid fee basis."))
        if self.fee_basis in amounts and money(amounts[self.fee_basis]) <= 0:
            frappe.throw(_("A positive fee is required for the selected fee basis."))
        for field, value in (('Monthly Fee', self.monthly_fee),
                             ('Per Visit', self.per_visit_fee),
                             ('Fixed Fee', self.fixed_fee)):
            if money(value) < 0:
                frappe.throw(_("Supervisor fees cannot be negative."))
            if self.fee_basis != field and money(value) != 0:
                frappe.throw(_("Enter an amount only in the field for the selected fee basis."))
        if self.supervision_agreement:
            agreement = frappe.db.get_value('CF Supervision Agreement', self.supervision_agreement,
                                            ['project', 'docstatus'], as_dict=True)
            if not agreement or agreement.project != self.project or agreement.docstatus != 1:
                frappe.throw(_("Linked owner supervision agreement must be submitted and belong to this Project."))
        if not (self.scope or '').strip():
            frappe.throw(_("Scope / Responsibilities is required."))

    def before_cancel(self):
        frappe.db.sql('SELECT name FROM `tabCF Supervisor Assignment` WHERE name=%s FOR UPDATE', (self.name,))
        if frappe.db.exists('CF Site Visit', {'supervisor_assignment': self.name, 'docstatus': 1}):
            frappe.throw(_("Cancel submitted site logs for this assignment before cancelling the assignment."))
