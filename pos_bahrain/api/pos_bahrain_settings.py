import frappe


@frappe.whitelist()
def hide_sales_return():
    hide_sales_return_except = frappe.db.get_single_value("POS Bahrain Settings", "hide_sales_return_except")
    hide_sales_return_role = frappe.db.get_single_value("POS Bahrain Settings", "hide_sales_return_role")
    return hide_sales_return_role if hide_sales_return_except else None

@frappe.whitelist()
def get_doctype_naming_series(doctype):
    options = frappe.get_meta(doctype).get_field("naming_series").options
    series_list = options.split("\n") if options else []
    return series_list

@frappe.whitelist()
def get_naming_series_settings(doctype, company, pos_profile=None, ):
    pb_settings = frappe.get_single("POS Bahrain Settings")
    filters = {"pb_doctype": doctype, "company":company}
    if pos_profile:
        filters["pos_profile"] = pos_profile
    naming_series_settings = frappe.db.get_all("PB Naming Series Settings", filters=filters, fields=["*"]) 
    return naming_series_settings if pb_settings.enable_naming_series_settings else []