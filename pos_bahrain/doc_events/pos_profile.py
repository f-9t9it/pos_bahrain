import frappe

@frappe.whitelist()
def get_series():
	print("method calling..")
	return frappe.get_meta("Sales Invoice").get_field("naming_series").options or ""