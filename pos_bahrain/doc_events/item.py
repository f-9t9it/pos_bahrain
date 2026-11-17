import frappe


def on_update(doc, method):
    auto_create_prices_from_item_defaults = frappe.db.get_single_value("POS Bahrain Settings", "auto_create_prices_from_item_defaults")
    if auto_create_prices_from_item_defaults == 1:
        for item in doc.item_defaults:
            if item.custom_rate > 0 and item.default_price_list:
                exist_price = frappe.db.exists("Item Price", {"item_code": doc.name, "uom": doc.stock_uom,"price_list": item.default_price_list})
                if not exist_price:
                    item_price = frappe.get_doc({
                        "doctype": "Item Price",
                        "item_code": doc.name,
                        "uom": doc.stock_uom,
                        "selling": frappe.db.get_value("Price List", item.default_price_list, "selling"),
                        "buying": frappe.db.get_value("Price List", item.default_price_list, "buying"),
                        "price_list": item.default_price_list,
                        "price_list_rate": item.custom_rate
                    })
                    item_price.insert(ignore_permissions=True)
                else:
                    item_price = frappe.get_doc("Item Price", exist_price)
                    item_price.price_list_rate = item.custom_rate
                    item_price.save(ignore_permissions=True)
            elif item.custom_rate <= 0 and item.default_price_list:
                return frappe.throw(f"Custom Rate must be greater than 0 for Item {doc.name} in Price List {item.default_price_list}")