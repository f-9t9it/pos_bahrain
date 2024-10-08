import frappe


@frappe.whitelist()
def hide_sales_return():
    hide_sales_return_except = frappe.db.get_single_value("POS Bahrain Settings", "hide_sales_return_except")
    hide_sales_return_role = frappe.db.get_single_value("POS Bahrain Settings", "hide_sales_return_role")
    return hide_sales_return_role if hide_sales_return_except else None
