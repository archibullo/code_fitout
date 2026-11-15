frappe.query_reports["CF BOQ Budget"] = {
  filters: [
    {fieldname: "project", label: __("Project"), fieldtype: "Link", options: "Project", reqd: 1}
  ]
};
