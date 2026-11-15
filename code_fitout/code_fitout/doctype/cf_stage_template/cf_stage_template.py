import frappe
from frappe import _
from frappe.model.document import Document


class CFStageTemplate(Document):
    def validate(self):
        old = self.get_doc_before_save()
        if old and frappe.db.exists('CF Stage Handover', {'stage_template': self.name, 'docstatus': 1}):
            old_checks = [(x.criterion, x.criterion_ar, x.acceptance_standard, x.mandatory, x.photo_required) for x in old.checklist]
            new_checks = [(x.criterion, x.criterion_ar, x.acceptance_standard, x.mandatory, x.photo_required) for x in self.checklist]
            if (old.work_category, old.stage_order, old.active, old_checks) != (self.work_category, self.stage_order, self.active, new_checks):
                frappe.throw(_("Cannot alter accepted stage criteria or order. Use a new approved stage/template release."))
        if not self.stage_order or int(self.stage_order) <= 0:
            frappe.throw(_("Stage order must be a positive integer."))
        if not self.checklist:
            frappe.throw(_("At least one acceptance criterion is required."))
        seen = set()
        for row in self.checklist:
            if not (row.criterion or '').strip():
                frappe.throw(_("Checklist description cannot be empty."))
            key = row.criterion.strip().casefold()
            if key in seen:
                frappe.throw(_("Duplicate criterion in the same stage."))
            seen.add(key)
        duplicate = frappe.db.exists('CF Stage Template', {
            'work_category':self.work_category,
            'stage_order':int(self.stage_order),
            'active':1,
        })
        if self.active and duplicate and duplicate != self.name:
            frappe.throw(_("Another active stage already uses this order in the work category."))
