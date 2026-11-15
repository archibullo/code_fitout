import frappe
from frappe import _


def execute(filters=None):
    filters=filters or {}
    columns=[
        {'fieldname':'project','label':_('Project'),'fieldtype':'Link','options':'Project','width':180},
        {'fieldname':'work_category','label':_('Work Category'),'fieldtype':'Link','options':'CF Work Category','width':200},
        {'fieldname':'inspection_area','label':_('Zone / Room'),'fieldtype':'Data','width':160},
        {'fieldname':'stage','label':_('Stage'),'fieldtype':'Data','width':230},
        {'fieldname':'stage_order','label':_('Stage Number'),'fieldtype':'Int','width':100},
        {'fieldname':'inspection_date','label':_('Inspection Date'),'fieldtype':'Date','width':130},
        {'fieldname':'outcome','label':_('Outcome'),'fieldtype':'Data','width':110},
        {'fieldname':'handover','label':_('Signed Minutes'),'fieldtype':'Link','options':'CF Stage Handover','width':170},
        {'fieldname':'supervisor','label':_('Supervisor Assignment'),'fieldtype':'Link','options':'CF Supervisor Assignment','width':170},
    ]
    conditions=['h.docstatus=1'];params={}
    if filters.get('project'):
        conditions.append('h.project=%(project)s');params['project']=filters['project']
    rows=frappe.db.sql('''
        SELECT h.project,h.work_category,h.inspection_area,t.stage_name AS stage,
          t.stage_order,h.inspection_date,h.outcome,h.name AS handover,
          h.supervisor_assignment AS supervisor
        FROM `tabCF Stage Handover` h
        JOIN `tabCF Stage Template` t ON h.stage_template=t.name
        WHERE '''+' AND '.join(conditions)+'''
        ORDER BY h.project,h.work_category,h.inspection_area,t.stage_order,h.inspection_date
    ''',params,as_dict=True)
    return columns,rows
