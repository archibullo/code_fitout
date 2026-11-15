frappe.query_reports["CF Owner Balance"] = {
  filters: [
    {fieldname: "project", label: __("Project"), fieldtype: "Link", options: "Project", reqd: 1}
  ]
};
