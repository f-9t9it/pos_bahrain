import frappe


def set_item_price_from_bin(bin):
    settings = frappe.get_single("POS Bahrain Settings")
    if settings.valuation_price_list and settings.valuation_warehouse == bin.warehouse:
        item_price = frappe.db.exists(
            "Item Price",
            {"item_code": bin.item_code, "price_list": settings.valuation_price_list},
        )
        valuation_rate = bin.valuation_rate or 0
        if item_price:
            if (
                frappe.db.get_value("Item Price", item_price, "price_list_rate")
                != bin.valuation_rate
            ):
                frappe.db.set_value(
                    "Item Price", item_price, "price_list_rate", valuation_rate
                )
        else:
            frappe.get_doc(
                {
                    "doctype": "Item Price",
                    "item_code": bin.item_code,
                    "price_list": settings.valuation_price_list,
                    "price_list_rate": valuation_rate,
                }
            ).insert(ignore_permissions=True)
