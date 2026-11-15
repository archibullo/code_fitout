/* BOQ live preview: authoritative amounts are recalculated by CFBOQ.validate. */
function cf_boq_totals(frm) {
    let sum = 0;
    (frm.doc.boq_lines || []).forEach(r => {
        const subtotal = flt(flt(r.qty) * flt(r.rate), 2);
        frappe.model.set_value(r.doctype, r.name, 'amount', subtotal);
        sum += subtotal;
    });
    frm.set_value('total_budget', flt(sum, 2));
}
frappe.ui.form.on('CF BOQ Line', {
    qty(frm) { cf_boq_totals(frm); },
    rate(frm) { cf_boq_totals(frm); },
    boq_lines_add(frm) { cf_boq_totals(frm); },
    boq_lines_remove(frm) { cf_boq_totals(frm); }
});
