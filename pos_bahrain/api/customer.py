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
