import frappe


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def batch_query(doctype, txt, searchfield, start, page_len, filters):
    query = """
        SELECT
            b.name,
            b.item,
            i.item_name,
            b.expiry_date
        FROM `tabBatch` AS b
        JOIN `tabItem` AS i ON i.name = b.item
        WHERE b.name LIKE {txt}
        OR b.item LIKE {txt}
        OR i.item_name LIKE {txt}
        OR b.expiry_date LIKE {txt}
        LIMIT {start}, {page_len}
    """.format(
        txt=frappe.db.escape("%{0}%".format(txt)),
        start=start,
        page_len=page_len,
    )

    return frappe.db.sql(query)
