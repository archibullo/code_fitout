import frappe
from frappe import _


def execute(filters=None):
    project=(filters or {}).get('project')
    if not project:
        frappe.throw(_("Project is required."))
    columns=[
      {'fieldname':'project','label':_('Project'),'fieldtype':'Link','options':'Project','width':190},
      {'fieldname':'supplier','label':_('Supplier'),'fieldtype':'Link','options':'Supplier','width':220},
      {'fieldname':'work_category','label':_('Work Category'),'fieldtype':'Link','options':'CF Work Category','width':190},
      {'fieldname':'cost_type','label':_('Cost Type'),'fieldtype':'Data','width':170},
      {'fieldname':'record_count','label':_('Records'),'fieldtype':'Int','width':85},
      {'fieldname':'approved','label':_('Approved Costs'),'fieldtype':'Currency','width':155},
      {'fieldname':'paid','label':_('Allocated Paid'),'fieldtype':'Currency','width':155},
      {'fieldname':'outstanding','label':_('Outstanding'),'fieldtype':'Currency','width':155},
    ]
    rows=frappe.db.sql("""
      SELECT c.project,c.supplier,c.work_category,c.cost_type,
        COUNT(c.name) record_count, SUM(c.amount) approved,
        SUM(COALESCE(p.paid,0)) paid,
        SUM(c.amount-COALESCE(p.paid,0)) outstanding
      FROM `tabCF Cost Record` c
      LEFT JOIN (
        SELECT a.cost_record, SUM(a.allocated_amount) paid
        FROM `tabCF Payment Allocation` a
        JOIN `tabCF Payment` p ON p.name=a.parent AND p.docstatus=1
        GROUP BY a.cost_record
      ) p ON p.cost_record=c.name
      WHERE c.docstatus=1 AND c.project=%s
      GROUP BY c.project,c.supplier,c.work_category,c.cost_type
      ORDER BY c.work_category,c.supplier,c.cost_type
    """,(project,),as_dict=True)
    return columns, rows
