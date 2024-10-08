# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import json
from functools import partial, reduce
from toolz import (
    compose,
    pluck,
    merge,
    concatv,
    valmap,
    itemmap,
    groupby,
    reduceby,
    excepts,
)

from pos_bahrain.utils import pick, sum_by, with_report_error_check


def execute(filters=None, transaction_type="Sales"):
    columns = _get_columns(filters, transaction_type)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters, transaction_type)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns(filters, transaction_type):
    def make_column(key, label=None, type="Data", options=None, width=120):
        return {
            "label": _(label or key.replace("_", " ").title()),
            "fieldname": key,
            "fieldtype": type,
            "options": options,
            "width": width,
        }

    return [
        make_column("posting_date", type="Date", width=90),
        make_column(
            "invoice", type="Link", options="{} Invoice".format(transaction_type)
        ),
        make_column("item_code", type="Link", options="Item"),
        make_column("item_name", width=150),
        make_column("item_group", type="Link", options="Item Group"),
        make_column("default_supplier", type="Link", options="Supplier"),
        make_column("supplier_name", type="Data", width=150),
        make_column("current_qty", type="Float", width=90),
        make_column("stock_qty", type="Float", width=90),
        make_column("rate", type="Currency", width=90),
        make_column("amount", type="Currency", width=90),
        make_column("tax", type="Currency", width=90),
        make_column("total", type="Currency", width=90),
    ]


def _get_filters(filters, transaction_type):
    clauses = concatv(
        [
            "inv.docstatus = 1",
            "inv.posting_date BETWEEN %(from_date)s AND %(to_date)s",
            "inv.company = %(company)s",
        ],
        ["inv_item.item_code = %(item_code)s"] if filters.item_code else [],
        ["INSTR(inv_item.item_name, %(item_name)s) > 0"] if filters.item_name else [],
        ["inv_item.item_group = %(item_group)s"] if filters.item_group else [],
        ["inv.customer = %(customer)s"] if filters.customer else [],
        ["inv.supplier = %(supplier)s"] if filters.supplier else [],
        ["inv_item.warehouse = %(warehouse)s"] if filters.warehouse else [],
    )
    bin_clauses = concatv(
        ["TRUE"], ["warehouse = %(warehouse)s"] if filters.warehouse else []
    )
    values = merge(
        pick(
            [
                "customer",
                "supplier",
                "company",
                "warehouse",
                "item_code",
                "item_name",
                "item_group",
            ],
            filters,
        ),
        {"from_date": filters.from_date, "to_date": filters.to_date},
    )
    return (
        {
            "clauses": " AND ".join(clauses),
            "bin_clauses": " AND ".join(bin_clauses),
            "transaction_type": transaction_type,
        },
        values,
    )


@with_report_error_check
def _get_data(clauses, values, keys):
    items = frappe.db.sql(
        """
            SELECT
                inv.posting_date AS posting_date,
                inv.name AS invoice,
                inv_item.item_code AS item_code,
                inv_item.item_name AS item_name,
                inv_item.item_group AS item_group,
                id.default_supplier AS default_supplier,
                s.supplier_name AS supplier_name,
                b.actual_qty AS current_qty,
                inv_item.stock_qty AS stock_qty,
                inv_item.stock_uom AS stock_uom,
                inv_item.qty AS qty,
                inv_item.uom AS uom,
                inv_item.net_rate AS net_rate,
                inv_item.net_amount AS net_amount
            FROM `tab{transaction_type} Invoice Item` AS inv_item
            LEFT JOIN `tab{transaction_type} Invoice` AS inv ON
                inv.name = inv_item.parent
            LEFT JOIN `tabItem Default` AS id ON
                id.parent = inv_item.item_code AND id.company = %(company)s
            LEFT JOIN `tabSupplier` AS s ON
                s.name = id.default_supplier
            LEFT JOIN (
                SELECT item_code, SUM(actual_qty) AS actual_qty
                FROM `tabBin` WHERE {bin_clauses} GROUP BY item_code
            ) AS b ON
                b.item_code = inv_item.item_code
            WHERE {clauses}
            ORDER BY inv.posting_date DESC
        """.format(
            **clauses
        ),
        values=values,
        as_dict=1,
    )

    def set_amount(row_dict):
        row = frappe._dict(row_dict)
        return merge(
            row,
            {"rate": row.net_rate * row.qty / row.stock_qty, "amount": row.net_amount},
        )

    set_tax = _set_tax_amount(items, transaction_type=clauses.get("transaction_type"))

    template = reduce(lambda a, x: merge(a, {x: None}), keys, {})
    make_row = compose(
        partial(pick, keys), partial(merge, template), set_tax, set_amount
    )

    return [make_row(x) for x in items]


def _set_tax_amount(items, transaction_type):
    item_map = valmap(
        lambda values: reduceby(
            "item_code", lambda a, x: a + x.get("net_amount", 0), values, 0
        ),
        groupby("invoice", items),
    )

    def set_amount(item_code, tax_detail):
        return item_code, tax_detail[1]

    def make_tax_amount(tax):
        return compose(
            partial(itemmap, lambda x: set_amount(*x)),
            excepts(ValueError, json.loads, {}),
        )(tax.item_wise_tax_detail)

    tax_map = compose(
        partial(groupby, "invoice"),
        partial(map, lambda x: merge({"invoice": x.invoice}, make_tax_amount(x))),
    )(
        frappe.db.sql(
            """
                SELECT parent AS invoice, item_wise_tax_detail
                FROM `tab{transaction_type} Taxes and Charges` WHERE parent in %(invoices)s
            """.format(
                transaction_type=transaction_type
            ),
            values={"invoices": list(item_map.keys())},
            as_dict=1,
        )
    )

    def fn(row_dict):
        row = frappe._dict(row_dict)
        net_amount = row.net_amount or 0
        item_net = item_map.get(row.invoice, {}).get(row.item_code, 0)
        tax_weight = net_amount / item_net if item_net else 0
        tax = sum_by(row.item_code, tax_map.get(row.invoice, [])) * tax_weight
        return merge(row_dict, {"tax": tax, "total": net_amount + tax})

    return fn
