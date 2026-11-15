import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


def store_changes(doc):
    # Signed owner-owned quantity deltas by (site store, item).
    changes={}
    for row in doc.items or []:
        qty=flt(row.quantity,3)
        if doc.movement_type in ('Consumption','Return to Supplier','Transfer','Stock Adjustment (-)'):
            key=(doc.source_store,row.item_code)
            changes[key]=round(changes.get(key,0)-qty,3)
        if doc.movement_type in ('Receipt','Transfer','Stock Adjustment (+)'):
            key=(doc.target_store,row.item_code)
            changes[key]=round(changes.get(key,0)+qty,3)
    return changes


def owner_qty(store,item,excluding=None):
    # Ledger is independent from ERPNext GL / Stock Ledger.
    value=frappe.db.sql('''
        SELECT COALESCE(SUM(CASE
          WHEN m.movement_type IN ('Consumption','Return to Supplier','Transfer','Stock Adjustment (-)')
               AND m.source_store=%s THEN -l.quantity
          WHEN m.movement_type IN ('Receipt','Transfer','Stock Adjustment (+)')
               AND m.target_store=%s THEN l.quantity
          ELSE 0 END),0)
        FROM `tabCF Owner Material Line` l
        JOIN `tabCF Owner Material Movement` m ON m.name=l.parent
        WHERE m.docstatus=1 AND l.item_code=%s
          AND (m.source_store=%s OR m.target_store=%s)
          AND m.name!=%s
    ''',(store,store,item,store,store,excluding or ''))[0][0]
    return round(flt(value,3),3)


class CFOwnerMaterialMovement(Document):
    def validate(self):
        types={'Receipt','Consumption','Return to Supplier','Transfer','Stock Adjustment (+)','Stock Adjustment (-)'}
        if self.movement_type not in types:
            frappe.throw(_("Invalid material movement type."))
        required_source=self.movement_type in ('Consumption','Return to Supplier','Transfer','Stock Adjustment (-)')
        required_target=self.movement_type in ('Receipt','Transfer','Stock Adjustment (+)')
        if (required_source and not self.source_store) or (required_target and not self.target_store):
            frappe.throw(_("Choose the source/target store required by this movement."))
        if not required_source and self.source_store:
            frappe.throw(_("This movement must not have a source store."))
        if not required_target and self.target_store:
            frappe.throw(_("This movement must not have a target store."))
        if self.movement_type=='Transfer' and self.source_store==self.target_store:
            frappe.throw(_("Source and target stores must differ."))
        stores={}
        for name in (self.source_store,self.target_store):
            if not name:
                continue
            store=frappe.db.get_value('CF Site Store',name,
                ['project','stock_mode','active'],as_dict=True)
            if not store or not store.active or store.stock_mode!='Owner-Owned Operational Stock':
                frappe.throw(_("Owner material ledger can use active owner-owned site stores only."))
            stores[name]=store
        if self.movement_type=='Transfer':
            a=frappe.db.get_value('Project',stores[self.source_store].project,'customer')
            b=frappe.db.get_value('Project',stores[self.target_store].project,'customer')
            if not a or not b or a!=b:
                frappe.throw(_("Owner-owned materials can transfer only between projects of the same owner; different owners require separate documented return and receipt after legal transfer."))
            if not self.handover_received or not self.proof:
                frappe.throw(_("Transfers require receiving-site confirmation and signed transfer proof."))
        if self.movement_type in ('Return to Supplier','Stock Adjustment (-)','Stock Adjustment (+)') and not (self.reason or '').strip():
            frappe.throw(_("Returns and adjustments require a reason."))
        if not self.items:
            frappe.throw(_("Add at least one material item."))
        seen=set()
        for row in self.items:
            if not row.item_code or flt(row.quantity,3)<=0:
                frappe.throw(_("A stock item and positive quantity are required."))
            if row.item_code in seen:
                frappe.throw(_("Combine duplicated item rows for this movement."))
            seen.add(row.item_code)
            item=frappe.db.get_value('Item',row.item_code,['stock_uom','disabled','is_stock_item'],as_dict=True)
            if not item or item.disabled or not item.is_stock_item:
                frappe.throw(_("Select an active ERPNext stock-tracked Item, not a service Item."))
            row.uom=item.stock_uom
            if flt(row.unit_cost or 0)<0:
                frappe.throw(_("Material reference values cannot be negative."))

    def _check_balances(self,cancel=False):
        changes=store_changes(self)
        for store in sorted({s for s,_ in changes}):
            frappe.db.sql('SELECT name FROM `tabCF Site Store` WHERE name=%s FOR UPDATE',(store,))
        for key,delta in changes.items():
            # Exclude this movement when cancelling, then simulate removal.
            if cancel:
                available=owner_qty(key[0],key[1],excluding=self.name)
            else:
                available=owner_qty(key[0],key[1]) + delta
            if available < -0.0001:
                frappe.throw(_("Insufficient owner material stock at {0} for item {1}.").format(key[0],key[1]))

    def before_submit(self):
        self.validate()
        if self.movement_type in ('Receipt','Return to Supplier','Transfer','Stock Adjustment (+)','Stock Adjustment (-)') and not self.proof:
            frappe.throw(_("Attach a signed delivery / return / adjustment proof before submitting."))
        self._check_balances()

    def before_cancel(self):
        self._check_balances(cancel=True)
