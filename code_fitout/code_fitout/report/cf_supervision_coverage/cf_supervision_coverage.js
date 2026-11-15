frappe.query_reports["CF Supervision Coverage"] = {filters: [
  {fieldname:"project",label:__("Project"),fieldtype:"Link",options:"Project"},
  {fieldname:"supervisor",label:__("Supervisor"),fieldtype:"Link",options:"CF Supervisor"},
  {fieldname:"from_date",label:__("From Date"),fieldtype:"Date"},
  {fieldname:"to_date",label:__("To Date"),fieldtype:"Date"},
]};
