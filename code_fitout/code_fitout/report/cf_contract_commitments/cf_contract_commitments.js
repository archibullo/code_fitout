frappe.query_reports["CF Contract Commitments"] = {filters: [
    {fieldname: "project", label: __("Project"), fieldtype: "Link", options: "Project"},
    {fieldname: "supplier", label: __("Supplier"), fieldtype: "Link", options: "Supplier"}
]};
