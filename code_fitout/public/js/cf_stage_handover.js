frappe.ui.form.on('CF Stage Handover', {
    stage_template(frm) {
        if (!frm.doc.stage_template) return;
        frappe.db.get_doc('CF Stage Template', frm.doc.stage_template).then(template => {
            frm.set_value('work_category', template.work_category);
            frm.clear_table('checklist');
            (template.checklist || []).forEach(c => {
                const row = frm.add_child('checklist');
                row.criterion = c.criterion;
                row.criterion_ar = c.criterion_ar;
                row.acceptance_standard = c.acceptance_standard;
                row.mandatory = c.mandatory;
                row.photo_required = c.photo_required;
            });
            frm.refresh_field('checklist');
        });
    }
});
