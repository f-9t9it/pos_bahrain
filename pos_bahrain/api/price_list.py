import frappe
from toolz import first, merge


@frappe.whitelist()
def get_selling_rate(item, price_list, currency):
    return merge(
        _get_selling_rate(item, price_list, currency),
        _get_default_selling_rate(item, currency),
    )


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def price_list_query(doctype, txt, searchfield, start, page_len, filters):
    includes = frappe.db.sql(""" SELECT price_list from `tabApply Offer Pricelist` """, as_dict = 0)
    print("///////////",includes) 
    # query = """
    #     SELECT 
    #         pl.name,
    #         CONCAT_WS(": ", "Rate", ifnull(round(ip.price_list_rate, 2), 0 )) rate
    #     FROM `tabPrice List` pl
    #     LEFT JOIN `tabItem Price` ip ON ip.price_list = pl.name
    #     WHERE pl.name LIKE {txt}
    #     AND ip.item_code = %(item_code)s
    #     AND pl.currency = %(currency)s
    #     AND pl.selling = %(selling)s
    #     AND (pl.name = %(regural_price_list)s or pl.name = %(customer_price_list)s or pl.name = %(preferred)s)
    #     LIMIT {start}, {page_len}
    # """.format(
    #     txt=frappe.db.escape("%{0}%".format(txt)), start=start, page_len=page_len
    # )
    query = """
        SELECT 
            pl.name,
            CONCAT_WS(": ", "Rate", ifnull(round(ip.price_list_rate, 2), 0 )) rate
        FROM `tabPrice List` pl
        LEFT JOIN `tabItem Price` ip ON ip.price_list = pl.name
        WHERE pl.name LIKE {txt}
        AND ip.item_code = %(item_code)s
        AND pl.currency = %(currency)s
        AND pl.selling = %(selling)s
        AND pl.name IN (select price_list from `tabApply Offer Pricelist`)
        LIMIT {start}, {page_len}
    """.format(
        txt=frappe.db.escape("%{0}%".format(txt)), start=start, page_len=page_len
    )
    return frappe.db.sql(query, filters)


def _get_default_selling_rate(item, currency):
    item_defaults = frappe.get_all(
        "Item Default",
        filters={"parent": item},
        fields=["default_price_list"],
    )

    if item_defaults:
        item_default = first(item_defaults)
        return {
            "default_price_list_rate": _get_selling_rate(
                item,
                item_default.get("default_price_list"),
                currency,
            ).get("price_list_rate")
        }

    return {}


def _get_selling_rate(item, price_list, currency):
    item_price = frappe.get_all(
        "Item Price",
        filters={
            "item_code": item,
            "price_list": price_list,
            "currency": currency,
            "selling": 1,
        },
        fields=["price_list_rate"],
    )
    return first(item_price) if item_price else {"price_list_rate":0}
