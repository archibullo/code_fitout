frappe.ui.form.on('CF Site Store', {
    refresh(frm) {
        if (!frm.is_new() && frm.doc.stock_mode === 'Company-Owned ERP Stock') {
            frm.add_custom_button(__('Create / Link ERPNext Warehouse'), () => {
                frappe.call({method: 'code_fitout.code_fitout.doctype.cf_site_store.cf_site_store.create_company_warehouse',
                    args: {site_store: frm.doc.name}, callback: r => {
                        if (r.message) {frappe.show_alert({message: __('Warehouse: ') + r.message, indicator: 'green'});frm.reload_doc();}
                    }});
            });
        }
        if (!frm.is_new() && frm.doc.erp_warehouse) {
            frm.add_custom_button(__('Open Warehouse'), () => frappe.set_route('Form','Warehouse',frm.doc.erp_warehouse));
        }
    }
});
