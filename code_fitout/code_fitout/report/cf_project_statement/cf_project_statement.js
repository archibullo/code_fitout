frappe.query_reports["CF Project Statement"] = {
  filters: [
    {fieldname: "project", label: __("Project"), fieldtype: "Link", options: "Project", reqd: 1}
  ]
};
