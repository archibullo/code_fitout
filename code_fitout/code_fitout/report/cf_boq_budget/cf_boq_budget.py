import frappe
from frappe import _


def execute(filters=None):
    project=(filters or {}).get('project')
    if not project:
        frappe.throw(_("Project is required."))
    cols=[
      {'fieldname':'work_category','label':_('Category'),'fieldtype':'Link','options':'CF Work Category','width':215},
      {'fieldname':'cost_type','label':_('Type'),'fieldtype':'Data','width':180},
      {'fieldname':'budget','label':_('Submitted BOQ Budget'),'fieldtype':'Currency','width':170},
      {'fieldname':'actual','label':_('Approved Actual Costs'),'fieldtype':'Currency','width':170},
      {'fieldname':'variance','label':_('Budget Less Actual'),'fieldtype':'Currency','width':170},
    ]
    # Multiple submitted BOQs per project count cumulatively (use for change orders,
    # not superseded revisions; revisions must be cancelled to remove them).
    data=frappe.db.sql("""
      SELECT types.work_category, types.cost_type,
        COALESCE(b.budget,0) budget,COALESCE(c.actual,0) actual,
        COALESCE(b.budget,0)-COALESCE(c.actual,0) variance
      FROM (
        SELECT l.work_category,l.cost_type
          FROM `tabCF BOQ Line` l JOIN `tabCF BOQ` h ON h.name=l.parent
          WHERE h.docstatus=1 AND h.project=%(project)s
        UNION
        SELECT work_category,cost_type FROM `tabCF Cost Record`
          WHERE docstatus=1 AND project=%(project)s
      ) types
      LEFT JOIN (
        SELECT l.work_category,l.cost_type,SUM(l.amount) budget
          FROM `tabCF BOQ Line` l JOIN `tabCF BOQ` h ON h.name=l.parent
          WHERE h.docstatus=1 AND h.project=%(project)s
          GROUP BY l.work_category,l.cost_type
      ) b ON b.work_category=types.work_category AND b.cost_type=types.cost_type
      LEFT JOIN (
        SELECT work_category,cost_type,SUM(amount) actual
          FROM `tabCF Cost Record` WHERE docstatus=1 AND project=%(project)s
          GROUP BY work_category,cost_type
      ) c ON c.work_category=types.work_category AND c.cost_type=types.cost_type
      ORDER BY types.work_category,types.cost_type
    """,{'project':project},as_dict=True)
    return cols,data
