import frappe


@frappe.whitelist()
def update_status(name, status):
    repack_request = frappe.get_doc("Repack Request", name)
    repack_request.check_permission("write")
    repack_request.set_status(update=True, status=status)
