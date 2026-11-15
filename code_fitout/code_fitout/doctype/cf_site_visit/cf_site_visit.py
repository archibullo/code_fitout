import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class CFSiteVisit(Document):
    def validate(self):
        if self.progress_percent is not None and not 0 <= float(self.progress_percent) <= 100:
            frappe.throw(_("Progress must be between 0 and 100 percent."))
        if self.hours_on_site and float(self.hours_on_site) < 0:
            frappe.throw(_("Hours on site cannot be negative."))
        if self.next_visit_date and getdate(self.next_visit_date) < getdate(self.visit_date):
            frappe.throw(_("Next follow-up date cannot precede visit date."))
        assignment = frappe.db.get_value('CF Supervisor Assignment', self.supervisor_assignment,
            ['project', 'supervisor', 'mode', 'start_date', 'end_date', 'docstatus'], as_dict=True)
        if not assignment or assignment.docstatus != 1:
            frappe.throw(_("Select a submitted Supervision Assignment."))
        if assignment.project != self.project:
            frappe.throw(_("Supervision Assignment must belong to the same Project."))
        day = getdate(self.visit_date)
        if day < getdate(assignment.start_date) or (assignment.end_date and day > getdate(assignment.end_date)):
            frappe.throw(_("Visit date is outside the supervision assignment period."))
        self.supervisor = assignment.supervisor
        if self.visit_kind == 'Resident Daily Log' and assignment.mode != 'Resident':
            frappe.throw(_("Resident Daily Log requires a Resident assignment."))
        if self.visit_kind == 'Scheduled Supervision Visit' and assignment.mode != 'Visits':
            frappe.throw(_("Scheduled Supervision Visit requires a Visits assignment."))
        if self.visit_kind not in ('Resident Daily Log', 'Scheduled Supervision Visit', 'Extra / Emergency Visit'):
            frappe.throw(_("Invalid visit type."))
        if self.related_task:
            task_project = frappe.db.get_value('Task', self.related_task, 'project')
            if task_project != self.project:
                frappe.throw(_("Task must belong to the same project."))

    def before_submit(self):
        if self.status != 'Closed':
            frappe.throw(_("Close the site inspection report before submitting it."))
        # Prevent duplicate certified resident daily logs for one assignment/date.
        if self.visit_kind == 'Resident Daily Log':
            frappe.db.sql('SELECT name FROM `tabCF Supervisor Assignment` WHERE name=%s FOR UPDATE',
                          (self.supervisor_assignment,))
            existing = frappe.db.get_value('CF Site Visit', {
                'supervisor_assignment': self.supervisor_assignment,
                'visit_date': self.visit_date,
                'visit_kind': 'Resident Daily Log',
                'docstatus': 1,
            }, 'name')
            if existing and existing != self.name:
                frappe.throw(_("Only one submitted Resident Daily Log per assignment and date is allowed."))
