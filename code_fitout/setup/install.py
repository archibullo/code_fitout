from pathlib import Path
import json
"""Install configuration: avoids mutating legacy hand-built DocTypes."""
import frappe
from frappe import _

CATEGORIES = [
    "HVAC / Air Conditioning", "Electrical Works", "Plumbing & Sanitary",
    "Civil Works", "Masonry & Blockwork", "Plastering",
    "Painting & Wall Finishes", "Carpentry & Woodwork", "Doors & Joinery",
    "Aluminum & Glass", "Gypsum Board & False Ceilings", "Flooring & Tiling",
    "Marble & Granite", "Waterproofing", "Thermal & Acoustic Insulation",
    "Metalwork & Steel", "Kitchens & Cabinets", "Bathroom Fixtures",
    "Lighting Systems", "Low Current Systems", "Smart Home & Automation",
    "CCTV & Security Systems", "Fire Alarm & Fire Fighting",
    "Networking & Data Cabling", "Elevators & Lifts", "Demolition & Removal",
    "Landscaping & Outdoor Works", "Swimming Pools",
    "Cleaning & Site Preparation", "General Finishing", "General Maintenance",
    "Material Supply", "Transportation & Logistics", "Equipment Rental",
    "General Labor", "Other",
]
ROLES = ["CF Fitout Viewer", "CF Fitout Editor", "CF Fitout Approver"]


def before_install():
    if not frappe.db.exists("DocType", "Project") or not frappe.db.exists("DocType", "Supplier"):
        frappe.throw(_("ERPNext must be installed before C.O.D.E. Fitout."))
    # Roles must exist before syncing DocType permissions.
    for role in ROLES:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1}).insert(ignore_permissions=True)


def after_install():
    seed()


def after_migrate():
    # Repair missing setup records on every site migration.
    seed()


def after_setup_wizard(args=None):
    # Runs after ERPNext has completed its setup stages.
    seed()


def on_company_created(doc, method=None):
    # Company can be created after code_fitout is installed.
    seed_supplier_groups()


def on_supplier_group_updated(doc, method=None):
    # Root Supplier Group may appear after app installation and after Company.
    # Only react to the root; inserting our children must not recurse.
    if doc.name == "All Supplier Groups" and doc.get("is_group"):
        seed_supplier_groups()


def seed_supplier_groups():
    """Insert only missing leaf groups; leave existing ERPNext masters untouched."""
    if not frappe.db.exists("DocType", "Supplier Group"):
        return
    if not frappe.db.exists("Supplier Group", "All Supplier Groups"):
        return

    for group in ("Fitout Contractors", "Material Suppliers", "Site Services"):
        if not frappe.db.exists("Supplier Group", group):
            frappe.get_doc({
                "doctype": "Supplier Group",
                "supplier_group_name": group,
                "parent_supplier_group": "All Supplier Groups",
                "is_group": 0,
            }).insert(ignore_permissions=True)


def setup_status():
    """Read-only setup diagnostic; can be called with bench execute."""
    groups = ("Fitout Contractors", "Material Suppliers", "Site Services")
    return {
        "supplier_root_exists": bool(frappe.db.exists("Supplier Group", "All Supplier Groups")),
        "supplier_groups": {name: bool(frappe.db.exists("Supplier Group", name)) for name in groups},
        "instapay_exists": bool(frappe.db.exists("Mode of Payment", "InstaPay")),
        "work_categories": frappe.db.count("CF Work Category") if frappe.db.exists("DocType", "CF Work Category") else 0,
        "stage_templates": frappe.db.count("CF Stage Template") if frappe.db.exists("DocType", "CF Stage Template") else 0,
        "print_formats": {
            name: bool(frappe.db.exists("Print Format", name))
            for name in ("CF Stage Handover Minutes", "CF Final Trade Handover")
        },
    }


def seed():
    if not frappe.db.exists("DocType", "CF Work Category"):
        return
    for name in CATEGORIES:
        if not frappe.db.exists("CF Work Category", name):
            frappe.get_doc({"doctype": "CF Work Category", "category_name": name}).insert(ignore_permissions=True)
    seed_supplier_groups()
    if frappe.db.exists("DocType", "Mode of Payment") and not frappe.db.exists("Mode of Payment", "InstaPay"):
        frappe.get_doc({"doctype": "Mode of Payment", "mode_of_payment": "InstaPay", "type": "General"}).insert(ignore_permissions=True)
    seed_handover_templates()
    install_print_formats()


def seed_handover_templates():
    """Install editable stage templates once; never overwrite customized criteria."""
    if not frappe.db.exists("DocType", "CF Stage Template"):
        return
    path = Path(__file__).resolve().parents[1] / "data" / "stage_templates.json"
    for stage in json.loads(path.read_text(encoding="utf-8")):
        if not frappe.db.exists("CF Stage Template", stage["stage_code"]):
            values = dict(stage)
            values["doctype"] = "CF Stage Template"
            frappe.get_doc(values).insert(ignore_permissions=True)


def install_print_formats():
    """Create custom source-controlled Jinja formats; preserve local edits on upgrades."""
    formats = (("CF Stage Handover Minutes", "CF Stage Handover", "cf_stage_handover.html"),
               ("CF Final Trade Handover", "CF Trade Handover", "cf_trade_handover.html"))
    root = Path(__file__).resolve().parents[1] / "templates" / "print_formats"
    for name,doctype,filename in formats:
        if not frappe.db.exists("DocType", doctype) or frappe.db.exists("Print Format", name):
            continue
        frappe.get_doc({
            "doctype":"Print Format", "name":name, "doc_type":doctype,
            "standard":"No", "custom_format":1, "print_format_type":"Jinja",
            "html":(root / filename).read_text(encoding="utf-8"),
            "disabled":0
        }).insert(ignore_permissions=True)
