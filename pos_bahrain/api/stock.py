import frappe

@frappe.whitelist()
def get_total_stock_qty(item_code):
    total_qty = frappe.db.sql("""SELECT SUM(actual_qty) FROM `tabBin` WHERE item_code='%(item_code)s'"""
        %{"item_code": item_code},
        as_dict=0)
    return total_qty[0][0] if total_qty else 0