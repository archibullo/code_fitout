/* Preview only: Python controllers always recalculate on save and submit. */
function cf_refresh_payment_totals(frm) {
    const items = frm.doc.payment_allocations || [];
    const total = items.reduce((v, row) => v + flt(row.allocated_amount), 0);
    frm.set_value({
        total_allocated: flt(total, 2),
        unallocated_amount: flt(flt(frm.doc.amount) - total, 2)
    });
}
frappe.ui.form.on('CF Payment', {
    amount(frm) { cf_refresh_payment_totals(frm); },
    refresh(frm) { if (frm.is_new()) cf_refresh_payment_totals(frm); }
});
frappe.ui.form.on('CF Payment Allocation', {
    allocated_amount(frm) { cf_refresh_payment_totals(frm); },
    payment_allocations_add(frm) { cf_refresh_payment_totals(frm); },
    payment_allocations_remove(frm) { cf_refresh_payment_totals(frm); }
});
