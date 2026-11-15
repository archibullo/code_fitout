import frappe
from frappe import _


def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = [
        {'fieldname':'work_order','label':_('Work Order'),'fieldtype':'Link','options':'CF Work Order','width':170},
        {'fieldname':'project','label':_('Project'),'fieldtype':'Link','options':'Project','width':180},
        {'fieldname':'supplier','label':_('Supplier'),'fieldtype':'Link','options':'Supplier','width':220},
        {'fieldname':'committed','label':_('Contract Value'),'fieldtype':'Currency','width':150},
        {'fieldname':'approved','label':_('Approved Works'),'fieldtype':'Currency','width':150},
        {'fieldname':'paid','label':_('Paid on Works'),'fieldtype':'Currency','width':150},
        {'fieldname':'due','label':_('Approved Due'),'fieldtype':'Currency','width':145},
        {'fieldname':'unperformed','label':_('Not Yet Approved'),'fieldtype':'Currency','width':160},
        {'fieldname':'retention_percent','label':_('Retention %'),'fieldtype':'Percent','width':125},
    ]
    rows = frappe.db.sql('''
        SELECT wo.name work_order, wo.project, wo.supplier,
          wo.committed_amount committed, COALESCE(c.approved,0) approved,
          COALESCE(c.paid,0) paid, COALESCE(c.approved,0)-COALESCE(c.paid,0) due,
          wo.committed_amount-COALESCE(c.approved,0) unperformed,
          wo.retention_percent
        FROM `tabCF Work Order` wo
        LEFT JOIN (
          SELECT cr.work_order, SUM(cr.amount) approved, SUM(COALESCE(pa.paid,0)) paid
          FROM `tabCF Cost Record` cr
          LEFT JOIN (
            SELECT a.cost_record,SUM(a.allocated_amount) paid
            FROM `tabCF Payment Allocation` a
            JOIN `tabCF Payment` p ON p.name=a.parent AND p.docstatus=1
            GROUP BY a.cost_record
          ) pa ON pa.cost_record=cr.name
          WHERE cr.docstatus=1 AND cr.work_order IS NOT NULL
          GROUP BY cr.work_order
        ) c ON c.work_order=wo.name
        WHERE wo.docstatus=1
          AND (%(supplier)s IS NULL OR wo.supplier=%(supplier)s)
          AND (%(project)s IS NULL OR wo.project=%(project)s)
        ORDER BY wo.project,wo.supplier,wo.name
    ''', {'supplier':filters.get('supplier') or None,'project':filters.get('project') or None}, as_dict=True)
    return columns, rows
