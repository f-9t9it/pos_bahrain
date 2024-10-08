# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial
from toolz import concatv, compose, valmap, merge

from pos_bahrain.utils import key_by


def execute(filters=None):
    from erpnext.stock.report.stock_balance.stock_balance import execute

    columns, data = execute(filters)
    prices = {
        "buying": frappe.db.get_single_value("Buying Settings", "buying_price_list"),
        "selling": frappe.db.get_single_value("Selling Settings", "selling_price_list"),
    }
    return _get_columns(columns, prices), _get_data(data, prices, filters)


def _get_columns(columns, prices):
    return list(
        concatv(
            columns[:2],
            [
                {
                    "fieldname": "supplier",
                    "fieldtype": "Link",
                    "width": 100,
                    "label": "Supplier",
                    "options": "Supplier",
                }
            ],
            columns[2:7],
            [
                {
                    "fieldname": "buying_price",
                    "fieldtype": "Currency",
                    "width": 100,
                    "label": prices.get("buying"),
                },
                {
                    "fieldname": "selling_price",
                    "fieldtype": "Currency",
                    "width": 100,
                    "label": prices.get("selling"),
                },
            ],
            columns[7:],
        )
    )


def _get_data(data, prices, filters):
    get_query_by_item_code = compose(
        partial(valmap, lambda x: x.get("value")),
        partial(key_by, "item_code"),
        lambda x: frappe.db.sql(
            x,
            values=merge({"item_codes": [x.get("item_code") for x in data]}, prices),
            as_dict=1,
        ),
    )
    price_query = """
        SELECT
            ip.item_code AS item_code,
            ip.price_list_rate AS value
        FROM `tabItem Price` AS ip
        LEFT JOIN `tabItem` AS i ON i.name = ip.item_code
        WHERE
            ip.price_list = %({price})s AND
            ip.item_code IN %(item_codes)s AND
            IFNULL(ip.uom, '') IN ('', i.stock_uom)
    """

    suppliers_by_item_code = get_query_by_item_code(
        """
            SELECT
                parent AS item_code,
                default_supplier AS value
            FROM `tabItem Default`
            WHERE parent in %(item_codes)s
        """
    )
    buying_prices_by_item_code = get_query_by_item_code(
        price_query.format(price="buying")
    )
    selling_prices_by_item_code = get_query_by_item_code(
        price_query.format(price="selling")
    )

    def add_fields(row):
        item_code = row.get("item_code")
        return merge(
            row,
            {
                "supplier": suppliers_by_item_code.get(item_code),
                "buying_price": buying_prices_by_item_code.get(item_code),
                "selling_price": selling_prices_by_item_code.get(item_code),
            },
        )

    def filter_by_supplier(row):
        if not filters.supplier:
            return True
        return filters.supplier == row[2]

    make_data = compose(
        list, partial(filter, filter_by_supplier), partial(map, add_fields)
    )

    return make_data(data)
