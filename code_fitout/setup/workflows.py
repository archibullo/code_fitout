"""Optional explicit Frappe Workflow provisioning.

Native Submit/Cancel works immediately without this module. A site admin can
choose to turn on workflow buttons after exercising staging acceptance tests.
No production workflow is activated by default.
"""
import frappe

DEFINITIONS = [
    ("CF Cost Approval", "CF Cost Record", [
        ("Pending Review", 0), ("Approved", 1), ("Cancelled", 2)], [
        ("Pending Review", "Approve", "Approved"),
        ("Approved", "Cancel", "Cancelled")]),
    ("CF Payment Verification", "CF Payment", [
        ("Pending Verification", 0), ("Verified", 1), ("Cancelled", 2)], [
        ("Pending Verification", "Verify", "Verified"),
        ("Verified", "Cancel", "Cancelled")]),
    ("CF Owner Fund Verification", "CF Owner Movement", [
        ("Pending Confirmation", 0), ("Posted", 1), ("Cancelled", 2)], [
        ("Pending Confirmation", "Post", "Posted"),
        ("Posted", "Cancel", "Cancelled")]),
    ("CF BOQ Approval", "CF BOQ", [
        ("Pending Review", 0), ("Approved", 1), ("Cancelled", 2)], [
        ("Pending Review", "Approve", "Approved"),
        ("Approved", "Cancel", "Cancelled")]),
]


def configure(activate=False):
    """Import optional workflows. `activate=False` by default for safety.

    Does not overwrite any existing CF Workflow. Activation must be performed
    deliberately by editing that workflow after a staging review.
    """
    if isinstance(activate, str):
        activate = activate.lower() in ("true", "1", "yes")
    if frappe.session.user != "Administrator":
        frappe.throw("Workflow setup requires Administrator.")
    for name, doctype, states, transitions in DEFINITIONS:
        if frappe.db.exists("Workflow", name):
            print("Already exists; unchanged:", name)
            continue
        for state, _ in states:
            if not frappe.db.exists("Workflow State", state):
                frappe.get_doc({
                    "doctype": "Workflow State", "workflow_state_name": state
                }).insert(ignore_permissions=True)
        for _, action, _ in transitions:
            if not frappe.db.exists("Workflow Action Master", action):
                frappe.get_doc({
                    "doctype": "Workflow Action Master", "workflow_action_name": action
                }).insert(ignore_permissions=True)
        doc = frappe.get_doc({
            "doctype": "Workflow", "workflow_name": name,
            "document_type": doctype, "workflow_state_field": "workflow_state",
            "is_active": int(bool(activate)), "send_email_alert": 0,
            "states": [{
                "state": state,
                "doc_status": status,
                "allow_edit": "CF Fitout Editor" if status == 0 else "CF Fitout Approver",
            } for state, status in states],
            "transitions": [{
                "state": start, "action": action, "next_state": end,
                "allowed": "CF Fitout Approver",
                "allow_self_approval": 1,
            } for start, action, end in transitions],
        })
        doc.insert(ignore_permissions=True)
        print("Created:", name, "Active:", bool(activate))
    print("Use native Submit/Cancel unless a workflow was explicitly activated and tested.")
