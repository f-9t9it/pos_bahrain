import frappe


@frappe.whitelist()
def get_user_branch(user=None):
    branch = frappe.db.get_all("Branch Users", filters={"branch_user": user or frappe.session.user}, fields=['parent'] )
    branch_exists = frappe.db.exists("Branch Users", {"branch_user": user or frappe.session.user})
    if branch_exists:
        return branch[0].parent if branch != [] else None
    # employee = frappe.db.exists("Employee", {"user_id": user or frappe.session.user})
    # if employee:
    #     return frappe.db.get_value("Employee", employee, "branch")
    # return None


@frappe.whitelist()
def get_user_warehouse():
    branch = get_user_branch()
    return frappe.db.get_value("Branch", branch, "warehouse") if branch else None
