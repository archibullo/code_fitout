import frappe
from frappe import _


def execute(filters=None):
    filters=frappe._dict(filters or {})
    cols=[
      {'fieldname':'payment','label':_('Payment'),'fieldtype':'Link','options':'CF Payment','width':160},
      {'fieldname':'payment_date','label':_('Date'),'fieldtype':'Date','width':110},
      {'fieldname':'supplier','label':_('Supplier'),'fieldtype':'Link','options':'Supplier','width':210},
      {'fieldname':'project','label':_('Project'),'fieldtype':'Link','options':'Project','width':195},
      {'fieldname':'cost_record','label':_('Cost Record'),'fieldtype':'Link','options':'CF Cost Record','width':190},
      {'fieldname':'allocated_amount','label':_('Allocated'),'fieldtype':'Currency','width':130},
      {'fieldname':'paid_by','label':_('Paid By'),'fieldtype':'Data','width':145},
      {'fieldname':'funding_source','label':_('Funding Source'),'fieldtype':'Data','width':195},
      {'fieldname':'payment_method','label':_('Method'),'fieldtype':'Link','options':'Mode of Payment','width':130},
      {'fieldname':'transfer_reference','label':_('Reference'),'fieldtype':'Data','width':130},
    ]
    data=frappe.db.sql("""
      SELECT p.name payment, p.payment_date,p.supplier, a.project,
        a.cost_record, a.allocated_amount, p.paid_by,p.funding_source,
        p.payment_method,p.transfer_reference
      FROM `tabCF Payment` p
      JOIN `tabCF Payment Allocation` a ON a.parent=p.name
      WHERE p.docstatus=1 AND (%(supplier)s IS NULL OR p.supplier=%(supplier)s)
        AND (%(project)s IS NULL OR a.project=%(project)s)
      UNION ALL
      SELECT p.name payment, p.payment_date,p.supplier, p.project,
        NULL cost_record, p.unallocated_amount allocated_amount,
        p.paid_by,p.funding_source,p.payment_method,p.transfer_reference
      FROM `tabCF Payment` p
      WHERE p.docstatus=1 AND p.unallocated_amount>0
        AND (%(supplier)s IS NULL OR p.supplier=%(supplier)s)
        AND (%(project)s IS NULL OR p.project=%(project)s)
      ORDER BY payment_date DESC,payment DESC
    """,{'supplier':filters.get('supplier') or None,'project':filters.get('project') or None},as_dict=True)
    return cols,data
