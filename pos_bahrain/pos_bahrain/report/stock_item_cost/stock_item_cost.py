# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from pos_bahrain.utils.report import make_column
from functools import partial
from toolz import pluck, compose, concatv, merge, groupby, valmap


def execute(filters=None):
    columns, data = _get_columns(), _get_data(filters)
    return columns, data


def _get_columns():
    return list(
        concatv(
            [
                make_column(
                    "parent_item_group",
                    "Parent Item Group",
                    "Link",
                    options="Item Group",
                ),
                make_column(
                    "item_group",
                    "Item Group",
                    "Link",
                    options="Item Group",
                ),
                make_column(
                    "name",
                    "Item Code",
                    "Link",
                    options="Item",
                ),
                make_column("description", "Description", width=350),
                make_column("barcode", "Barcode", width=180),
            ],
            [make_column(_get_key(x), x, "Float") for x in _get_warehouses()],
            [
                make_column("qty_sold", "Qty Sold", "Float"),
                make_column("sold_valuation", "Sold Valuation", "Currency"),
            ],
        )
    )


def _get_data(filters):
    items = _get_items()
    warehouses = _get_warehouses()

    def get_gp_details():
        from erpnext.accounts.report.gross_profit.gross_profit import execute

        gp_columns, gp_data = execute(
            frappe._dict(merge(filters, {"group_by": "Item Code"}))
        )
        columns = list(map(_get_fieldname, gp_columns))

        def get_column_data(column_name, row):
            column_data = columns.index(column_name)
            return row[column_data]

        return {
            get_column_data("Item Code", x): {
                "qty_sold": get_column_data("Qty", x),
                "sold_valuation": get_column_data("Valuation Rate", x),
            }
            for x in gp_data
        }

    def make_gp(data):
        return merge({"qty_sold": 0.00, "sold_valuation": 0.00}, data)

    def make_stock(data):
        return merge({_get_key(x): 0.00 for x in warehouses}, data)

    gp_details = get_gp_details()
    item_barcodes = _get_item_barcodes()
    item_stocks = _get_item_stocks()

    data = compose(
        list,
        partial(
            map,
            lambda x: merge(x, make_gp(gp_details.get(x.get("name"), {}))),
        ),
        partial(
            map,
            lambda x: merge(x, make_stock(item_stocks.get(x.get("name"), {}))),
        ),
        partial(map, lambda x: merge(x, {"barcode": item_barcodes.get(x.get("name"))})),
    )

    return data(items)


def _get_items():
    return frappe.db.sql(
        """
            SELECT
                i.name,
                i.description,
                i.item_group,
                ig.parent_item_group
            FROM `tabItem` i
            JOIN `tabItem Group` ig ON ig.name = i.item_group
            ORDER BY i.name
        """,
        as_dict=1,
    )


def _get_item_barcodes():
    item_barcodes = frappe.db.get_all("Item Barcode", fields=["parent", "barcode"])
    return {x.get("parent"): x.get("barcode") for x in item_barcodes}


def _get_item_stocks():
    item_stocks = frappe.db.get_all(
        "Bin", fields=["warehouse", "item_code", "actual_qty"]
    )
    return compose(
        partial(
            valmap,
            lambda x: {_get_key(z.get("warehouse")): z.get("actual_qty") for z in x},
        ),
        partial(groupby, "item_code"),
    )(item_stocks)


def _get_warehouses():
    return compose(list, partial(pluck, "name"))(
        frappe.db.get_all("Warehouse", filters={"is_group": 0}, fields=["name"])
    )


def _get_key(text):
    return text.lower().replace(" ", "_").replace("-", "_")


def _get_fieldname(column):
    if isinstance(column, dict):
        return column.get("label")
    return column.split(":")[0]
