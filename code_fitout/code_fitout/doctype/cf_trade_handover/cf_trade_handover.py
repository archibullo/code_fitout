import frappe
from frappe import _
from frappe.model.document import Document


class CFTradeHandover(Document):
    def _populate(self):
        templates = frappe.get_all('CF Stage Template', filters={
            'work_category': self.work_category, 'active':1},
            fields=['name','stage_order'],order_by='stage_order asc')
        if not templates:
            frappe.throw(_("No active stage templates exist for this trade."))
        stages=[]
        for stage in templates:
            rows=frappe.db.sql('''
                SELECT name,inspection_date,supplier FROM `tabCF Stage Handover`
                WHERE project=%s AND work_category=%s AND stage_template=%s
                AND inspection_area=%s AND outcome='Accepted' AND docstatus=1
                ORDER BY inspection_date DESC LIMIT 1
            ''',(self.project,self.work_category,stage.name,self.inspection_area),as_dict=True)
            if not rows:
                frappe.throw(_("Missing submitted accepted stage: {0}.").format(stage.name))
            stages.append({'stage_template':stage.name,'accepted_handover':rows[0].name,'supplier':rows[0].supplier,'date':rows[0].inspection_date})
        self.set('stages',[])
        for stage in stages:
            self.append('stages',stage)

    def validate(self):
        if not frappe.db.get_value('Project',self.project,'customer'):
            frappe.throw(_("Project requires its Customer/owner before final handover."))
        self._populate()
        if not self.signed_final_copy:
            # Draft can be saved before signing; submission requires scan.
            pass

    def before_submit(self):
        frappe.db.sql('SELECT name FROM `tabProject` WHERE name=%s FOR UPDATE',(self.project,))
        self._populate()
        if not self.signed_final_copy:
            frappe.throw(_("Attach the signed final trade handover minutes."))
        dup=frappe.db.exists('CF Trade Handover',{'project':self.project,
            'work_category':self.work_category,'inspection_area':self.inspection_area,'docstatus':1})
        if dup and dup!=self.name:
            frappe.throw(_("A final trade handover already exists for this project and zone."))

    def before_cancel(self):
        # No dependent trade closure records yet. Normal cancellation history is retained.
        frappe.db.sql('SELECT name FROM `tabProject` WHERE name=%s FOR UPDATE',(self.project,))
