# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial
from toolz import compose, pluck, merge, concatv

from pos_bahrain.utils import pick
from pos_bahrain.utils.report import make_column
from pos_bahrain.pos_bahrain.report.batch_wise_expiry_report.helpers import (
    get_uom_columns,
    make_uom_col_setter,
)


NUM_OF_UOM_COLUMNS = 3


def execute(filters=None):
    columns = _get_columns(filters)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns(filters):
    join_columns = compose(list, concatv)
    columns = [
        make_column("item_code", type="Link", options="Item"),
        make_column("item_name", width=150),
        make_column("item_group", type="Link", options="Item Group"),
        make_column("brand", type="Link", options="Brand"),
        make_column("supplier", "Default Supplier", type="Link", options="Supplier"),
        make_column("supplier_name", "Supplier Name", width=150),
        make_column("supplier_part_no"),
        make_column("stock_uom", "Stock UOM", width=90),
        make_column("qty", "Balance Qty", type="Float", width=90),
    ]

    return (
        join_columns(columns, get_uom_columns(NUM_OF_UOM_COLUMNS))
        if filters.get("show_alt_uoms")
        else columns
    )


def _get_filters(filters):
    item_codes = (
        compose(
            list,
            partial(filter, lambda x: x),
            partial(map, lambda x: x.strip()),
            lambda x: x.split(","),
        )(filters.item_codes)
        if filters.item_codes
        else None
    )
    clauses = concatv(
        ["i.disabled = 0"], ["i.item_code IN %(item_codes)s"] if item_codes else []
    )
    bin_clauses = concatv(
        ["b.item_code = i.item_code"],
        ["b.warehouse = %(warehouse)s"] if filters.warehouse else [],
    )
    defaults_clauses = concatv(["id.parent = i.name"], ["id.company = %(company)s"])
    supplier_clauses = concatv(
        ["isp.parent = i.name"], ["isp.supplier = id.default_supplier"]
    )
    return (
        {
            "clauses": " AND ".join(clauses),
            "bin_clauses": " AND ".join(bin_clauses),
            "defaults_clauses": " AND ".join(defaults_clauses),
            "supplier_clauses": " AND ".join(supplier_clauses),
        },
        merge(filters, {"item_codes": item_codes} if item_codes else {}),
    )


def _get_data(clauses, values, keys):
    result = frappe.db.sql(
        """
            SELECT
                i.item_code AS item_code,
                i.item_name AS item_name,
                i.item_group AS item_group,
                i.stock_uom AS stock_uom,
                i.brand AS brand,
                id.default_supplier AS supplier,
                s.supplier_name AS supplier_name,
                isp.supplier_part_no AS supplier_part_no,
                SUM(b.actual_qty) AS qty
            FROM `tabItem` AS i
            LEFT JOIN `tabBin` AS b ON {bin_clauses}
            LEFT JOIN `tabItem Default` AS id ON {defaults_clauses}
            LEFT JOIN `tabItem Supplier` AS isp ON {supplier_clauses}
            LEFT JOIN `tabSupplier` AS s ON s.name = id.default_supplier
            WHERE {clauses}
            GROUP BY i.item_code
        """.format(
            **clauses
        ),
        values=values,
        as_dict=1,
    )

    def get_make_row():
        if not values.get("show_alt_uoms"):
            return partial(pick, keys)

        add_uom = make_uom_col_setter([x.get("item_code") for x in result])
        return compose(partial(pick, keys), add_uom)

    make_row = get_make_row()

    return [
        make_row(x) for x in result if not values.get("hide_zero_stock") or x.get("qty")
    ]
