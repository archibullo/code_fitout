"""Financial aggregates for the operational fitout ledger.

Never posts to the ERPNext GL. A separate, reviewed accounting integration
is needed for actual liabilities and bank balances.
"""
from decimal import Decimal, ROUND_HALF_UP

import frappe
from frappe import _

CENT = Decimal("0.01")


def money(value):
    return Decimal(str(value or 0)).quantize(CENT, rounding=ROUND_HALF_UP)


def positive(value, field="Amount"):
    result = money(value)
    if result <= 0:
        frappe.throw(_("{0} must be greater than zero.").format(field))
    return result


def lock_project(project):
    if not frappe.db.exists("Project", project):
        frappe.throw(_("Unknown project {0}").format(project))
    # InnoDB record lock: serializes competing owner-ledger mutations per project.
    frappe.db.sql("SELECT name FROM `tabProject` WHERE name=%s FOR UPDATE", (project,))


def lock_costs(names):
    """Lock in deterministic order to reduce deadlocks during simultaneous payments."""
    for name in sorted(set(names)):
        frappe.db.sql("SELECT name FROM `tabCF Cost Record` WHERE name=%s FOR UPDATE", (name,))


def cost_paid(cost_name, excluding=None):
    return money(frappe.db.sql("""
        SELECT COALESCE(SUM(a.allocated_amount),0)
        FROM `tabCF Payment Allocation` a
        JOIN `tabCF Payment` p ON p.name=a.parent
        WHERE a.cost_record=%s AND p.docstatus=1
          AND (%s IS NULL OR p.name!=%s)
    """, (cost_name, excluding, excluding))[0][0])


def owner_balances(project):
    """Returns (held funds, personal recoverable) from SUBMITTED documents.

    All submitted owner movements and payments for this project are included.
    Never count money transferred straight from owner to contractor in held funds.
    """
    rows = frappe.db.sql("""
        SELECT movement_type, COALESCE(SUM(amount),0) AS total
        FROM `tabCF Owner Movement`
        WHERE project=%s AND docstatus=1
        GROUP BY movement_type
    """, (project,), as_dict=True)
    movements = {x.movement_type: money(x.total) for x in rows}
    p_rows = frappe.db.sql("""
        SELECT funding_source, COALESCE(SUM(amount),0) AS total
        FROM `tabCF Payment`
        WHERE project=%s AND docstatus=1
        GROUP BY funding_source
    """, (project,), as_dict=True)
    payments = {x.funding_source: money(x.total) for x in p_rows}

    received = movements.get("Owner Advance Received", money(0))
    refunds = movements.get("Refund to Owner", money(0))
    held_repay = movements.get("Personal Advance Reimbursement - From Held Funds", money(0))
    direct_repay = movements.get("Personal Advance Reimbursement - Owner Directly", money(0))
    spent_held = payments.get("Owner Funds Already Received", money(0))
    spent_personal = payments.get("Personal Funds - Recoverable", money(0))
    incoming = frappe.db.sql("""
        SELECT COALESCE(SUM(amount),0) FROM `tabCF Owner Movement`
        WHERE target_project=%s AND movement_type='Transfer Held Funds to Another Project'
          AND docstatus=1
    """, (project,))[0][0]
    transfer_out = movements.get("Transfer Held Funds to Another Project", money(0))
    return (
        received + money(incoming) - transfer_out - refunds - held_repay - spent_held,
        spent_personal - held_repay - direct_repay,
    )


def validate_funding(paid_by, source):
    mapping = {
        "Property Owner": {"Owner Paid Directly"},
        "Me Personally": {"Owner Funds Already Received", "Personal Funds - Recoverable"},
        "C.O.D.E.": {"C.O.D.E. Operating Funds"},
        "Other": {"Other / To Be Verified"},
    }
    if source not in mapping.get(paid_by, set()):
        frappe.throw(_("Paid By and Funding Source do not match."))
