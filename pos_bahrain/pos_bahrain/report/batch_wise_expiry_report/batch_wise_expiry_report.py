# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import today, getdate
from functools import partial
from toolz import merge, pluck, keyfilter, compose, concatv, unique

from pos_bahrain.utils import pick
from pos_bahrain.utils.report import make_column
from pos_bahrain.pos_bahrain.report.batch_wise_expiry_report.helpers import (
    get_uom_columns,
    make_uom_col_setter,
)


NUM_OF_UOM_COLUMNS = 3


def execute(filters=None):
    args = _get_args(filters)
    columns = _get_columns(args)
    keys = _get_keys(args)
    data = _get_data(args, keys)
    return columns, data


def _get_args(filters={}):
    if not filters.get("company"):
        frappe.throw(_("Company is required to generate report"))
    return merge(
        filters,
        {
            "query_date": filters.get("query_date") or today(),
            "price_list1": frappe.db.get_value(
                "Buying Settings", None, "buying_price_list"
            )
            or "Standard Buying",
            "price_list2": frappe.db.get_value(
                "Selling Settings", None, "selling_price_list"
            )
            or "Standard Selling",
        },
    )


def _get_columns(args):
    join_columns = compose(list, concatv)
    columns = [
        make_column("supplier", type="Link", options="Supplier"),
        make_column("brand", type="Link", options="Brand"),
        make_column("item_code", type="Link", options="Item"),
        make_column("item_name", width=200),
        make_column("batch_no", "Batch", type="Link", options="Batch"),
        make_column("expiry_date", type="Date", width=90),
        make_column("expiry_in_days", "Expiry in Days", type="Int", width=90),
        make_column("qty", "Quantity", type="Float", width=90),
        make_column("stock_uom", "Stock UOM", width=90),
        make_column("price1", args.get("price_list1"), type="Currency"),
        make_column("price2", args.get("price_list2"), type="Currency"),
        make_column("warehouse"),
    ]
    return (
        join_columns(columns, get_uom_columns(NUM_OF_UOM_COLUMNS))
        if args.get("show_alt_uoms")
        else columns
    )


def _get_keys(args):
    return compose(list, partial(pluck, "fieldname"), _get_columns)(args)


def _item_price_clauses(alias):
    return """
        {alias}.item_code = sle.item_code AND
        IFNULL({alias}.uom, '') = i.stock_uom AND
        IFNULL({alias}.customer, '') = '' AND
        IFNULL({alias}.supplier, '') = '' AND
        %(query_date)s BETWEEN
            IFNULL({alias}.valid_from, '2000-01-01') AND
            IFNULL({alias}.valid_upto, '2500-12-31')
    """.format(
        alias=alias
    )


def _sle_clauses(args):
    join_clauses = compose(lambda x: " AND ".join(x), concatv)
    return join_clauses(
        [
            "sle.docstatus = 1",
            "sle.company = %(company)s",
            "sle.posting_date <= %(query_date)s",
            "IFNULL(sle.batch_no, '') != ''",
            "id.company = %(company)s",
        ],
        ["sle.warehouse = %(warehouse)s"] if args.get("warehouse") else [],
    )


def _get_data(args, keys):
    sles = frappe.db.sql(
        """
            SELECT
                sle.batch_no AS batch_no,
                sle.item_code AS item_code,
                sle.warehouse AS warehouse,
                SUM(sle.actual_qty) AS qty,
                i.stock_uom AS stock_uom,
                i.item_name AS item_name,
                i.brand AS brand,
                id.default_supplier AS supplier,
                b.expiry_date AS expiry_date,
                p1.price_list_rate AS price1,
                p2.price_list_rate AS price2
            FROM `tabStock Ledger Entry` AS sle
            LEFT JOIN `tabItem` AS i ON
                i.item_code = sle.item_code
            LEFT JOIN `tabItem Default` AS id ON
                id.parent = i.name
            LEFT JOIN `tabBatch` AS b ON
                b.batch_id = sle.batch_no
            LEFT JOIN `tabItem Price` AS p1 ON
                {p1_clauses}
                AND p1.price_list = %(price_list1)s
            LEFT JOIN `tabItem Price` AS p2 ON
                {p2_clauses}
                AND p2.price_list = %(price_list2)s
            WHERE {sle_clauses}
            GROUP BY sle.batch_no, sle.warehouse
            ORDER BY sle.item_code, sle.warehouse
        """.format(
            sle_clauses=_sle_clauses(args),
            p1_clauses=_item_price_clauses("p1"),
            p2_clauses=_item_price_clauses("p2"),
        ),
        values=args,
        as_dict=1,
    )

    def get_make_row():
        def set_expiry(row):
            expiry_in_days = (
                (row.expiry_date - getdate()).days if row.expiry_date else None
            )
            return merge(row, {"expiry_in_days": expiry_in_days})

        if not args.get("show_alt_uoms"):
            return compose(partial(keyfilter, lambda k: k in keys), set_expiry)

        get_item_codes = compose(list, unique, partial(pluck, "item_code"))
        add_uom = make_uom_col_setter(get_item_codes(sles))

        return compose(partial(keyfilter, lambda k: k in keys), add_uom, set_expiry)

    make_row = get_make_row()

    filter_rows = compose(
        list,
        partial(
            filter, lambda x: True if not args.get("hide_zero_stock") else x.get("qty")
        ),
        partial(map, make_row),
    )

    return filter_rows(sles)