import frappe
from frappe import _


def validate(doc, method):
    try:
        use_minimum_price_list = frappe.db.get_single_value(
            "POS Bahrain Settings", "use_minimum_price_list"
        )
        if use_minimum_price_list:
            _validate_minimum_price_list(doc)
    except Exception as e:
        pass


def _validate_minimum_price_list(doc):
    minimum_doc = _get_minimum_doc()
    if doc.doctype not in minimum_doc:
        return

    minimum_price_list = frappe.db.get_single_value(
        "POS Bahrain Settings", "minimum_price_list"
    )
    price_list_rates = _get_price_list_rates(
        minimum_price_list,
        list(map(lambda x: x.item_code, doc.items)),
    )

    for item in doc.items:
        item_price = price_list_rates.get(item.item_code, None)
        if not _is_mgr() and item_price and item_price > item.rate:
            frappe.throw(
                _(
                    "Unable to save. Item {} is less than the minimum price list".format(
                        item.item_code
                    )
                )
            )


def _get_minimum_doc():
    data = frappe.get_all("POS Bahrain Settings Minimum Doc", fields=["minimum_dt"])
    return [x.get("minimum_dt") for x in data]


def _get_price_list_rates(price_list, items):
    data = frappe.get_all(
        "Item Price",
        filters=[
            ["price_list", "=", price_list],
            ["item_code", "in", items],
            ["selling", "=", 1],
        ],
        fields=["price_list_rate", "item_code"],
    )
    return {x.get("item_code"): x.get("price_list_rate") for x in data}


def _is_mgr():
    return "Sales Master Manager" in frappe.get_roles(frappe.session.user)
