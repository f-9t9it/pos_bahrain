import frappe
import json

@frappe.whitelist()
def check_material_request_repack_items(items):
    items = json.loads(items)
    item_exist = True
    for i in items:
        if frappe.db.exists("Stock Entry Detail", {"material_request_item": i["name"]}):
            item_exist = True
        if not frappe.db.exists("Stock Entry Detail", {"material_request_item": i["name"]}):
            item_exist = False
    return item_exist