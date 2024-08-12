# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial
from toolz import pluck, compose, concatv, groupby, first, valmap, merge
from pos_bahrain.utils.report import make_column


def execute(filters=None):
    from erpnext.stock.report.stock_balance.stock_balance import execute

    columns, data = execute(filters)
    return _get_columns(), _get_data(data)


def _get_columns():
    return [
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
        make_column("sku_counts", "SKU Counts", "Float"),
        make_column("bal_val", "Balance Value", "Currency"),
        make_column("ret_val", "Retail", "Currency"),
    ]


def _get_data(data):
    def get_distinct_data(column_name):
        return compose(list, set, partial(pluck, column_name), lambda: data)()

    def get_merged_data(rows):
        parent_item_groups = _get_parent_item_groups(get_distinct_data("item_group"))
        item_selling_prices = _get_item_selling_prices(get_distinct_data("item_code"))
        return compose(
            list,
            partial(
                map,
                lambda x: merge(
                    x,
                    {
                        "parent_item_group": parent_item_groups.get(
                            x.get("item_group")
                        ),
                        "ret_val": item_selling_prices.get(x.get("item_code"), 0.00)
                        * x.get("bal_qty"),
                        "sku_counts": 1.0,
                    },
                ),
            ),
            lambda: rows,
        )()

    def item_group_by_data(rows):
        if not rows:
            return {}
        
        ref_data = rows[0]
        sum_fields = [
            "reorder_level",
            "reorder_qty",
            "opening_qty",
            "opening_val",
            "in_qty",
            "in_val",
            "out_qty",
            "out_val",
            "bal_qty",
            "bal_val",
            "val_rate",
            "ret_val",
            "sku_counts",
        ]

        for row in rows[1:]:
            for field in sum_fields:
                ref_data[field] = ref_data.get(field, 0) + row.get(field, 0)
        
        return ref_data


    merge_by_item_group = compose(
        partial(valmap, item_group_by_data), partial(groupby, "item_group")
    )

    return compose(list, lambda x: x.values(), merge_by_item_group, get_merged_data)(
        data
    )


def _get_parent_item_groups(item_groups):
    data = frappe.db.get_all(
        "Item Group",
        filters=[["name", "in", item_groups]],
        fields=["name", "parent_item_group"],
    )
    return {x.get("name"): x.get("parent_item_group") for x in data}


def _get_item_selling_prices(items):
    price_list = "Standard Selling"
    data = frappe.db.get_all(
        "Item Price",
        filters=[["item_code", "in", items], ["price_list", "=", price_list]],
        fields=["item_code", "price_list_rate"],
    )
    return {x.get("item_code"): x.get("price_list_rate") for x in data}
