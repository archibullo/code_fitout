import frappe
from frappe import _


def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = [
        {"fieldname": "supplier", "label": _("Supplier"), "fieldtype": "Link", "options": "Supplier", "width": 250},
        {"fieldname": "approved", "label": _("Approved Costs"), "fieldtype": "Currency", "width": 150},
        {"fieldname": "confirmed", "label": _("Confirmed Payments"), "fieldtype": "Currency", "width": 165},
        {"fieldname": "allocated", "label": _("Allocated"), "fieldtype": "Currency", "width": 145},
        {"fieldname": "advances", "label": _("Unallocated Advances"), "fieldtype": "Currency", "width": 165},
        {"fieldname": "outstanding", "label": _("Outstanding Costs"), "fieldtype": "Currency", "width": 160},
        {"fieldname": "net_balance", "label": _("Net Balance"), "fieldtype": "Currency", "width": 150},
    ]
    data = frappe.db.sql("""
    SELECT s.supplier, COALESCE(c.approved,0) approved,
        COALESCE(p.confirmed,0) confirmed, COALESCE(p.allocated,0) allocated,
        COALESCE(p.confirmed,0)-COALESCE(p.allocated,0) advances,
        COALESCE(c.approved,0)-COALESCE(p.allocated,0) outstanding,
        COALESCE(c.approved,0)-COALESCE(p.confirmed,0) net_balance
    FROM (
        SELECT supplier FROM `tabCF Cost Record` WHERE docstatus=1 AND supplier IS NOT NULL
        UNION
        SELECT supplier FROM `tabCF Payment` WHERE docstatus=1
    ) s
    LEFT JOIN (
        SELECT supplier, SUM(amount) approved
        FROM `tabCF Cost Record` WHERE docstatus=1 GROUP BY supplier
    ) c ON c.supplier=s.supplier
    LEFT JOIN (
        SELECT supplier, SUM(amount) confirmed, SUM(total_allocated) allocated
        FROM `tabCF Payment` WHERE docstatus=1 GROUP BY supplier
    ) p ON p.supplier=s.supplier
    WHERE (%(supplier)s IS NULL OR s.supplier=%(supplier)s)
    ORDER BY s.supplier
    """, {'supplier':filters.get('supplier') or None},as_dict=True)
    return columns,data
