import frappe
from frappe import _
from frappe.model.document import Document


class CFSiteStore(Document):
    def validate(self):
        project_company=frappe.db.get_value('Project',self.project,'company')
        if not project_company:
            frappe.throw(_("Project must have a Company before configuring a site store."))
        self.company=project_company
        if self.stock_mode=='Owner-Owned Operational Stock':
            if self.erp_warehouse:
                frappe.throw(_("Owner-owned stock must not use a company ERP Warehouse. Use the operational ledger."))
            if not frappe.db.get_value('Project',self.project,'customer'):
                frappe.throw(_("Owner-owned materials require a Project with a specified Customer / owner."))
        elif self.stock_mode=='Company-Owned ERP Stock':
            if self.erp_warehouse:
                warehouse=frappe.db.get_value('Warehouse',self.erp_warehouse,['company','is_group'],as_dict=True)
                if not warehouse or warehouse.company!=project_company or warehouse.is_group:
                    frappe.throw(_("Choose a non-group ERP Warehouse belonging to the Project company."))
                duplicate=frappe.db.exists('CF Site Store',{'erp_warehouse':self.erp_warehouse})
                if duplicate and duplicate!=self.name:
                    frappe.throw(_("The same ERPNext Warehouse is linked to another site store."))
        else:
            frappe.throw(_("Invalid stock ownership mode."))
        if not self.is_new():
            prior=frappe.db.get_value('CF Site Store',self.name,['project','stock_mode'],as_dict=True)
            if prior and (prior.project!=self.project or prior.stock_mode!=self.stock_mode):
                if frappe.db.exists('CF Owner Material Movement',{'docstatus':1,'source_store':self.name}) or frappe.db.exists('CF Owner Material Movement',{'docstatus':1,'target_store':self.name}):
                    frappe.throw(_("Cannot change project or ownership after posting owner material movements."))


@frappe.whitelist()
def create_company_warehouse(site_store):
    if not frappe.has_permission('Warehouse','create') or not frappe.has_permission('CF Site Store','write',site_store):
        frappe.throw(_("Insufficient permission to create and link a Warehouse."),frappe.PermissionError)
    store=frappe.get_doc('CF Site Store',site_store)
    store.validate()
    if store.stock_mode!='Company-Owned ERP Stock':
        frappe.throw(_("Create ERPNext Warehouses only for company-owned stock."))
    if store.erp_warehouse:
        return store.erp_warehouse
    root=frappe.db.get_value('Warehouse',{'company':store.company,'parent_warehouse':['is','not set'],'is_group':1},'name')
    if not root:
        frappe.throw(_("No group root Warehouse found for company; create one using ERPNext Stock first."))
    new=frappe.get_doc({'doctype':'Warehouse','warehouse_name':store.store_name+' '+store.name,
                        'company':store.company,'parent_warehouse':root,'is_group':0})
    new.insert()
    store.erp_warehouse=new.name
    store.save()
    return new.name
