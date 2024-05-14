import frappe
from frappe import _

def execute(filters=None):
    static_columns = [
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 100},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 100},
        {"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 100},
        {"label": _("Default Supplier"), "fieldname": "default_supplier", "fieldtype": "Link", "options": "Supplier", "width": 100},
        {"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 100},
        {"label": _("Standard Selling Price"), "fieldname": "selling_price", "fieldtype": "Currency", "width": 100},
        {"label": _("Standard Buying Price"), "fieldname": "buying_price", "fieldtype": "Currency", "width": 100},
        {"label": _("Valuation Rate"), "fieldname": "valuation_rate", "fieldtype": "Currency", "width": 100}
    ]
    dynamic_columns = get_dynamic_columns()
    columns = static_columns + dynamic_columns

    static_data = get_static_data(filters)
    dynamic_data = get_dynamic_data(filters)

    data = merge_data(static_data, dynamic_data)

    return columns, data

def get_static_data(filters):
    where_clause = get_where_clause(filters)

    sql = """
        SELECT 
            item.name AS item_code,
            item.item_name,
            item.item_group,
            IFNULL(id.default_supplier, '') AS default_supplier,
            IFNULL(SUM(bin.actual_qty), 0) AS qty,
            IF(selling_price.price_list = 'Standard Selling', selling_price.price_list_rate, NULL) AS selling_price,
            IF(buying_price.price_list = 'Standard Buying', buying_price.price_list_rate, NULL) AS buying_price,
            IFNULL(item.valuation_rate, 0) AS valuation_rate
        FROM 
            `tabItem` item
        INNER JOIN
            `tabItem Default` id ON item.name = id.parent
        LEFT JOIN
            `tabBin` bin ON bin.item_code = item.name
        LEFT JOIN
            (SELECT item_code, price_list_rate, price_list FROM `tabItem Price` WHERE price_list = 'Standard Selling') AS selling_price
            ON selling_price.item_code = item.name
        LEFT JOIN
            (SELECT item_code, price_list_rate, price_list FROM `tabItem Price` WHERE price_list = 'Standard Buying') AS buying_price
            ON buying_price.item_code = item.name
        WHERE 
            item.disabled = 0 AND 
            item.is_stock_item = 1 {}
        GROUP BY 
            item.name, item.item_name, item.item_group, id.default_supplier
    """.format(where_clause)

    return frappe.db.sql(sql, as_dict=True)

def get_dynamic_columns():
    dynamic_columns = []
    settings = frappe.get_single("POS Bahrain Settings")
    custom_price_list = settings.custom_price_list
    if custom_price_list:
        for price_list in custom_price_list:
            dynamic_column_name = price_list.price_list.lower().replace(" ", "_")
            if item_prices_exist(price_list.price_list):
                column = {"label": _(price_list.price_list), "fieldname": dynamic_column_name, "fieldtype": "Currency", "width": 100}
                dynamic_columns.append(column)
    return dynamic_columns

def item_prices_exist(price_list):
    sql = """
        SELECT
            COUNT(*) as count
        FROM
            `tabItem Price`
        WHERE
            price_list = '{}'
    """.format(price_list)
    result = frappe.db.sql(sql, as_dict=True)
    return result[0]['count'] > 0


def get_dynamic_data(filters):
    dynamic_data = []
    settings = frappe.get_single("POS Bahrain Settings")
    custom_price_list = settings.custom_price_list
    if custom_price_list:
        for price_list in custom_price_list:
            sql = """
                SELECT 
                    item.name AS item_code,
                    price_list.price_list_rate AS {}
                FROM 
                    `tabItem` item
                LEFT JOIN
                    `tabItem Price` price_list ON item.name = price_list.item_code
                WHERE 
                    price_list.price_list = '{}'
                    AND item.disabled = 0 
                    AND item.is_stock_item = 1 {}
                GROUP BY 
                    item.name
            """.format(price_list.price_list.lower().replace(" ", "_"), price_list.price_list, get_where_clause(filters))
            dynamic_data.append(frappe.db.sql(sql, as_dict=True))
    return dynamic_data

def merge_data(static_data, dynamic_data):
    merged_data = static_data.copy()
    for dynamic_item in dynamic_data:
        for item in merged_data:
            if dynamic_item and dynamic_item[0]['item_code'] == item['item_code']:
                item.update(dynamic_item[0])
    return merged_data

def get_where_clause(filters):
    where_clause = ""
    if filters.get('item'):
        where_clause += "AND item.name = '{}' ".format(filters.get('item'))
    if filters.get('item_group'):
        where_clause += "AND item.item_group = '{}' ".format(filters.get('item_group'))
    if filters.get('warehouse'):
        where_clause += "AND bin.warehouse = '{}' ".format(filters.get('warehouse'))
    if filters.get('date'):
        creation_date = filters.get('date').split(' ')[0]
        where_clause += "AND DATE(item.creation) = '{}' ".format(creation_date)
    if not filters.get('show_item_in_stock'):
        where_clause += "AND (IFNULL((SELECT SUM(actual_qty) FROM `tabBin` WHERE item_code = item.name), 0) = 0 OR item.name NOT IN (SELECT DISTINCT item_code FROM `tabBin`))"
    return where_clause


