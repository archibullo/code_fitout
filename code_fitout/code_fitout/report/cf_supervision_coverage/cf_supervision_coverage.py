import frappe
from frappe import _
from frappe.utils import getdate


def execute(filters=None):
    filters = frappe._dict(filters or {})
    if filters.get('from_date') and filters.get('to_date') and getdate(filters.from_date) > getdate(filters.to_date):
        frappe.throw(_("From Date cannot be after To Date."))
    cols = [
        {'fieldname':'assignment','label':_('Assignment'),'fieldtype':'Link','options':'CF Supervisor Assignment','width':170},
        {'fieldname':'project','label':_('Project'),'fieldtype':'Link','options':'Project','width':190},
        {'fieldname':'supervisor','label':_('Supervisor'),'fieldtype':'Link','options':'CF Supervisor','width':175},
        {'fieldname':'mode','label':_('Mode'),'fieldtype':'Data','width':100},
        {'fieldname':'start_date','label':_('Start Date'),'fieldtype':'Date','width':110},
        {'fieldname':'end_date','label':_('End Date'),'fieldtype':'Date','width':110},
        {'fieldname':'visit_target','label':_('Planned Visits / Month'),'fieldtype':'Int','width':160},
        {'fieldname':'resident_target','label':_('Resident Days / Week'),'fieldtype':'Int','width':160},
        {'fieldname':'completed_visits','label':_('Submitted Site Visits'),'fieldtype':'Int','width':160},
        {'fieldname':'resident_days','label':_('Submitted Resident Daily Logs'),'fieldtype':'Int','width':185},
        {'fieldname':'last_visit','label':_('Last Submitted Report'),'fieldtype':'Date','width':160},
        {'fieldname':'fee_basis','label':_('Fee Basis'),'fieldtype':'Data','width':125},
        {'fieldname':'rate','label':_('Agreed Fee / Rate (EGP)'),'fieldtype':'Currency','width':175},
        {'fieldname':'per_visit_estimate','label':_('Fee for Reported Visits (EGP)'),'fieldtype':'Currency','width':205},
        {'fieldname':'fee_payer','label':_('Fee Responsibility'),'fieldtype':'Data','width':160},
    ]
    rows = frappe.db.sql('''
        SELECT a.name AS assignment, a.project, a.supervisor, a.mode,
            a.start_date, a.end_date, a.visits_per_month AS visit_target,
            a.resident_days_per_week AS resident_target,
            SUM(CASE WHEN v.visit_kind IN ('Scheduled Supervision Visit','Extra / Emergency Visit') THEN 1 ELSE 0 END) AS completed_visits,
            SUM(CASE WHEN v.visit_kind='Resident Daily Log' THEN 1 ELSE 0 END) AS resident_days,
            MAX(v.visit_date) AS last_visit, a.fee_basis,
            CASE a.fee_basis WHEN 'Monthly Fee' THEN a.monthly_fee
                WHEN 'Per Visit' THEN a.per_visit_fee
                WHEN 'Fixed Fee' THEN a.fixed_fee ELSE 0 END AS rate,
            CASE WHEN a.fee_basis='Per Visit' THEN
                SUM(CASE WHEN v.visit_kind IN ('Scheduled Supervision Visit','Extra / Emergency Visit') THEN 1 ELSE 0 END) * a.per_visit_fee
            ELSE 0 END AS per_visit_estimate,
            a.fee_payer
        FROM `tabCF Supervisor Assignment` a
        LEFT JOIN `tabCF Site Visit` v
            ON v.supervisor_assignment=a.name AND v.docstatus=1
            AND (%(from_date)s IS NULL OR v.visit_date >= %(from_date)s)
            AND (%(to_date)s IS NULL OR v.visit_date <= %(to_date)s)
        WHERE a.docstatus=1
          AND (%(project)s IS NULL OR a.project=%(project)s)
          AND (%(supervisor)s IS NULL OR a.supervisor=%(supervisor)s)
        GROUP BY a.name, a.project, a.supervisor, a.mode, a.start_date, a.end_date,
                 a.visits_per_month, a.resident_days_per_week, a.fee_basis,
                 a.monthly_fee, a.per_visit_fee, a.fixed_fee, a.fee_payer
        ORDER BY a.project, a.supervisor, a.start_date
    ''', {'project':filters.get('project') or None,
          'supervisor':filters.get('supervisor') or None,
          'from_date':filters.get('from_date') or None,
          'to_date':filters.get('to_date') or None}, as_dict=True)
    return cols, rows
