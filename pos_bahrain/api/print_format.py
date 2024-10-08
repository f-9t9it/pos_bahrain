import frappe


@frappe.whitelist()
def toggle_disable_print_format(name):
    disabled = frappe.get_value('Print Format', name, 'disabled')
    frappe.db.set_value('Print Format', name, 'disabled', not disabled)
    return not disabled
