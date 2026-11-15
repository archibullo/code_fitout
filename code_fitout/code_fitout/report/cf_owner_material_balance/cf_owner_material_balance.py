import frappe
from frappe import _


def execute(filters=None):
    filters=filters or {}
    columns=[
        {'fieldname':'project','label':_('Project'),'fieldtype':'Link','options':'Project','width':170},
        {'fieldname':'site_store','label':_('Site Store'),'fieldtype':'Link','options':'CF Site Store','width':200},
        {'fieldname':'item_code','label':_('Material / Item'),'fieldtype':'Link','options':'Item','width':170},
        {'fieldname':'uom','label':_('UOM'),'fieldtype':'Link','options':'UOM','width':90},
        {'fieldname':'balance','label':_('Qty on Hand'),'fieldtype':'Float','precision':3,'width':140},
    ]
    params={};where=''
    if filters.get('project'):
        where=' AND s.project=%(project)s';params['project']=filters['project']
    rows=frappe.db.sql('''
        SELECT s.project,s.name AS site_store,l.item_code,MAX(l.uom) AS uom,
          ROUND(SUM(CASE
          WHEN m.target_store=s.name AND m.movement_type IN ('Receipt','Transfer','Stock Adjustment (+)') THEN l.quantity
          WHEN m.source_store=s.name AND m.movement_type IN ('Consumption','Return to Supplier','Transfer','Stock Adjustment (-)') THEN -l.quantity
          ELSE 0 END),3) AS balance
        FROM `tabCF Site Store` s
        JOIN `tabCF Owner Material Movement` m ON (m.source_store=s.name OR m.target_store=s.name) AND m.docstatus=1
        JOIN `tabCF Owner Material Line` l ON l.parent=m.name
        WHERE s.stock_mode='Owner-Owned Operational Stock' '''+where+'''
        GROUP BY s.project,s.name,l.item_code
        HAVING ABS(balance)>0.0001
        ORDER BY s.project,s.name,l.item_code
    ''',params,as_dict=True)
    return columns,rows
