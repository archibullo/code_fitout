app_name = "code_fitout"
app_title = "C.O.D.E. Fitout"
app_publisher = "C.O.D.E."
app_description = "Fitout projects, supervision, staged handover, inventories, contractor payments and owner funds."
app_email = ""
app_license = "MIT"
required_apps = ["erpnext"]

before_install = "code_fitout.setup.install.before_install"
after_install = "code_fitout.setup.install.after_install"
after_migrate = "code_fitout.setup.install.after_migrate"

# Supplier's additional payment and specialization fields are versioned fixtures.
fixtures = [
    {"dt": "Custom Field", "filters": [["fieldname", "in", [
        "custom_cf_specialties", "custom_cf_instapay_address", "custom_cf_instapay_mobile",
        "custom_cf_beneficiary_name", "custom_cf_payment_notes",
        "custom_cf_property_address", "custom_cf_building", "custom_cf_unit",
        "custom_cf_floor", "custom_cf_internal_budget", "custom_cf_scope"
    ]]]}
]

doctype_js = {
    "CF Payment": "public/js/cf_payment.js",
    "CF BOQ": "public/js/cf_boq.js",
    "CF Site Store": "public/js/cf_site_store.js",
    "CF Stage Handover": "public/js/cf_stage_handover.js",
}

# Frappe v16 Apps page. No legacy workspace_sidebar fixture is shipped.
app_logo_url = "/assets/code_fitout/images/fitout-mark.svg"
add_to_apps_screen = [{
    "name": "code_fitout",
    "logo": "/assets/code_fitout/images/fitout-mark.svg",
    "title": "C.O.D.E. Fitout",
    "route": "/desk/code-fitout/cf-work-category",
    "sequence_id": 35,
}]
