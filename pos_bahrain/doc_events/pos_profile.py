import frappe

@frappe.whitelist()
def get_series():
	return frappe.get_meta("Sales Invoice").get_field("naming_series").options or ""