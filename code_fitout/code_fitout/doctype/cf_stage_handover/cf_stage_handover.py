import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class CFStageHandover(Document):
    def validate(self):
        self.check_links()
        self.check_results()

    def check_links(self):
        template = frappe.db.get_value('CF Stage Template', self.stage_template,
            ['work_category','stage_order','active'],as_dict=True)
        if not template or not template.active:
            frappe.throw(_("Select an active handover stage template."))
        self.work_category = template.work_category
        if self.supervisor_assignment:
            assignment=frappe.db.get_value('CF Supervisor Assignment',self.supervisor_assignment,
                ['project','start_date','end_date','docstatus'],as_dict=True)
            if not assignment or assignment.docstatus != 1 or assignment.project != self.project:
                frappe.throw(_("Supervisor assignment must be submitted for this project."))
            if getdate(self.inspection_date) < getdate(assignment.start_date) or (assignment.end_date and getdate(self.inspection_date)>getdate(assignment.end_date)):
                frappe.throw(_("Inspection date is outside the supervisor's assignment."))
        if self.reinspection_of:
            previous=frappe.db.get_value('CF Stage Handover',self.reinspection_of,
                ['project','stage_template','inspection_area','outcome','docstatus'],as_dict=True)
            if not previous or previous.project!=self.project or previous.stage_template!=self.stage_template or previous.inspection_area!=self.inspection_area or previous.docstatus!=1 or previous.outcome!='Rejected':
                frappe.throw(_("Reinspection must reference a submitted rejected inspection for this stage and area."))
        source=frappe.get_doc('CF Stage Template',self.stage_template)
        expected={r.criterion:r for r in source.checklist}
        if not self.checklist:
            # Snapshot is kept with the inspection even when template is edited later.
            for row in source.checklist:
                self.append('checklist',{'criterion':row.criterion,'criterion_ar':row.criterion_ar,
                    'acceptance_standard':row.acceptance_standard,'mandatory':row.mandatory,
                    'photo_required':row.photo_required})
        else:
            provided={r.criterion for r in self.checklist}
            if len(provided)!=len(self.checklist) or provided!=set(expected):
                frappe.throw(_("Checklist must match the selected stage. Clear and reload after template change."))
            for row in self.checklist:
                ref=expected[row.criterion]
                row.criterion_ar=ref.criterion_ar
                row.acceptance_standard=ref.acceptance_standard
                row.mandatory=ref.mandatory
                row.photo_required=ref.photo_required

    def check_results(self):
        if not self.checklist:
            frappe.throw(_("Inspection checklist is empty."))
        if self.outcome not in ('Accepted','Rejected'):
            frappe.throw(_("Choose Accepted or Rejected."))
        for row in self.checklist:
            if row.result not in ('Pass','Fail','Not Applicable'):
                # Allow draft to be completed before submission.
                if self.flags.in_submit:
                    frappe.throw(_("Record a result for every criterion."))
                continue
            if row.result=='Not Applicable' and not (row.remarks or '').strip():
                frappe.throw(_("Not Applicable requires an explanation."))
            if row.result=='Pass' and row.photo_required and not row.evidence:
                if self.flags.in_submit:
                    frappe.throw(_("Attach evidence for mandatory test/inspection criteria."))
            if self.outcome=='Accepted' and row.mandatory and row.result!='Pass':
                if self.flags.in_submit:
                    frappe.throw(_("All mandatory criteria must pass before acceptance."))
        if self.outcome=='Rejected' and not (self.notes or '').strip() and self.flags.in_submit:
            frappe.throw(_("Rejected handover requires remarks identifying deficiencies."))

    def before_submit(self):
        self.flags.in_submit=True
        self.check_links()
        self.check_results()
        if self.outcome=='Accepted' and not self.inspector_signed:
            frappe.throw(_("Inspector must confirm the signed handover minutes."))
        if self.outcome=='Accepted' and not self.signed_copy:
            frappe.throw(_("Attach the signed acceptance minutes before submitting an accepted stage."))
        # Serialize approvals for the same project to prevent duplicate accepted stages.
        frappe.db.sql('SELECT name FROM `tabProject` WHERE name=%s FOR UPDATE',(self.project,))
        template=frappe.db.get_value('CF Stage Template',self.stage_template,
            ['work_category','stage_order'],as_dict=True)
        if self.outcome=='Accepted':
            duplicates=frappe.db.sql('''
                SELECT name FROM `tabCF Stage Handover`
                WHERE project=%s AND inspection_area=%s AND stage_template=%s
                  AND outcome='Accepted' AND docstatus=1 AND name!=%s LIMIT 1
            ''',(self.project,self.inspection_area,self.stage_template,self.name or ''))
            if duplicates:
                frappe.throw(_("This work-stage is already accepted for that project and zone."))
            preceding=frappe.db.sql('''
                SELECT name FROM `tabCF Stage Template`
                WHERE work_category=%s AND active=1 AND stage_order<%s
                ORDER BY stage_order ASC
            ''',(template.work_category,template.stage_order),as_dict=True)
            for required in preceding:
                accepted=frappe.db.exists('CF Stage Handover',{
                    'project':self.project,'inspection_area':self.inspection_area,
                    'stage_template':required.name,'outcome':'Accepted','docstatus':1})
                if not accepted:
                    frappe.throw(_("Previous acceptance stage {0} must be submitted first for this area.").format(required.name))

    def before_cancel(self):
        frappe.db.sql('SELECT name FROM `tabProject` WHERE name=%s FOR UPDATE',(self.project,))
        if self.outcome=='Accepted':
            final=frappe.db.sql("""
                SELECT t.name FROM `tabCF Trade Stage Receipt` r
                JOIN `tabCF Trade Handover` t ON t.name=r.parent
                WHERE r.accepted_handover=%s AND t.docstatus=1 LIMIT 1
            """,(self.name,))
            if final:
                frappe.throw(_("Cancel final trade handover {0} first.").format(final[0][0]))
            this_order=int(frappe.db.get_value('CF Stage Template',self.stage_template,'stage_order'))
            followup=frappe.db.sql('''
                SELECT h.name FROM `tabCF Stage Handover` h
                JOIN `tabCF Stage Template` t ON t.name=h.stage_template
                WHERE h.project=%s AND h.inspection_area=%s AND t.work_category=%s
                AND t.stage_order>%s AND h.outcome='Accepted' AND h.docstatus=1
                LIMIT 1
            ''',(self.project,self.inspection_area,self.work_category,this_order))
            if followup:
                frappe.throw(_("Cannot cancel: subsequent work stages were already accepted. Cancel in reverse order."))
