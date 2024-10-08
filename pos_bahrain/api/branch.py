import frappe
from toolz import first


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def branch_query(doctype, txt, searchfield, start, page_len, filters):
    sub_query = """
        SELECT ROUND(`tabBin`.actual_qty, 2) from `tabBin`
        WHERE `tabBin`.warehouse = `tabBranch`.warehouse
        AND `tabBin`.item_code = %(item_code)s
    """

    query = """
        SELECT 
            `tabBranch`.name,
            CONCAT_WS(
                " : ",
                "Actual Qty",
                IFNULL( ({sub_query}), 0 ) 
            ) AS actual_qty
        FROM `tabBranch`
        WHERE `tabBranch`.name LIKE {txt}
        LIMIT {start}, {page_len}
    """.format(
        sub_query=sub_query,
        txt=frappe.db.escape("%{0}%".format(txt)),
        start=start,
        page_len=page_len,
    )

    return frappe.db.sql(query, filters)

@frappe.whitelist()
def get_branch_qty(branch, item):
    data = frappe.db.sql(
        """
        SELECT ROUND(`tabBin`.actual_qty, 2) as qty
        FROM `tabBin`
        INNER JOIN `tabBranch` ON `tabBin`.warehouse = `tabBranch`.warehouse
        WHERE `tabBranch`.name = '%(branch)s'
        AND `tabBin`.item_code = '%(item_code)s'
        """%
        {"item_code": item, "branch": branch},
        as_dict=0
    )
    if data:
        return data[0][0]
    else:
        return None

@frappe.whitelist()
def get_naming_series():
    return {
        "sales_order": _get_series("Sales Order"),
        "sales_invoice": _get_series("Sales Invoice"),
    }

def _get_series(doctype):
    series_text = frappe.get_meta(doctype).get_field("naming_series").options or ""
    return series_text.split("\n")
