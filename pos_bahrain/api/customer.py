import frappe


@frappe.whitelist()
def get_user_branch(user=None):
    branch = frappe.db.exists("Branch", {"pb_user": user or frappe.session.user})
    if branch:
        return branch
    employee = frappe.db.exists("Employee", {"user_id": user or frappe.session.user})
    if employee:
        return frappe.db.get_value("Employee", employee, "branch")
    return None


@frappe.whitelist()
def get_user_warehouse():
    branch = get_user_branch()
    return frappe.db.get_value("Branch", branch, "warehouse") if branch else None

@frappe.whitelist()
def validate_contact(doc, method):
    #contact_phone_exists = frappe.db.exists("Contact Phone", {"parent": doc.name})
    #frappe.errprint(f"{contact_phone_exists}")
    #contact_phone_doc = frappe.get_doc("Contact Phone", contact_phone_exists)
    #if not contact_phone_doc.phone.isdigit():
    #    frappe.throw("Use numbers only for contact phone")
    return None
