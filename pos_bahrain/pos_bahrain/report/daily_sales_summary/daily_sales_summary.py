# Copyright (c) 2013,     9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from functools import partial
from toolz import compose, pluck, keyfilter, valmap, groupby, merge


def execute(filters=None):
    columns = _get_columns(filters)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)

    def post_row(row):
        return merge(row, {x: row.get(x) or 0 for x in keys})

    return columns, list(map(post_row, data))



def _get_columns(filters):
    def make_column(key, label=None, col_type="Float", options=None, width=120):
        col_data = {
            "label": _(label or key.replace("_", " ").title()),
            "fieldname": key,
            "fieldtype": col_type,
            "options": options,
            "width": width,
            "precision":3
        }
        if(col_type != 'Float'):
            del col_data['precision']
        return col_data

    columns = [
        make_column("posting_date", "Date", col_type="Date", width=90),
        make_column("grand_total"),
        make_column("tax_total"),
        make_column("net_total", "Total Sales Value"),
        make_column("returns_grand_total", "Total Returns"),
        make_column("net_total_after_returns", "Net Sales After Tax & Returns"),
    ]
    mops = pluck("name", frappe.get_all("Mode of Payment", order_by="modified desc"))
    return columns + [make_column(x, x) for x in mops]


def _get_filters(filters):
    clauses = [
        "s.docstatus = 1",
        "s.posting_date BETWEEN %(from_date)s AND %(to_date)s",
    ]
    return " AND ".join(clauses), filters


def _get_data(clauses, values, keys):
    items = frappe.db.sql(
        """
            SELECT
                s.posting_date AS posting_date,
                SUM(si.base_grand_total) AS grand_total,
                SUM(si.base_total_taxes_and_charges) AS tax_total,
                SUM(si.base_net_total) AS net_total,
                SUM(sr.base_grand_total) AS returns_grand_total
            FROM `tabSales Invoice` as s
            LEFT JOIN (
                SELECT * FROM `tabSales Invoice` WHERE is_return = 0
            ) AS si ON si.name = s.name
            LEFT JOIN (
                SELECT * from `tabSales Invoice` WHERE is_return = 1
            ) AS sr ON sr.name = s.name
            WHERE {clauses}
            GROUP BY s.posting_date
        """.format(
            clauses=clauses
        ),
        values=values,
        as_dict=1,
    )
    payments = frappe.db.sql(
        """
            SELECT
                s.posting_date AS posting_date,
                p.mode_of_payment AS mode_of_payment,
                SUM(p.base_amount) AS amount
            FROM `tabSales Invoice` as s
            LEFT JOIN `tabSales Invoice Payment` as p ON p.parent = s.name
            WHERE s.is_return = 0 AND {clauses}
            GROUP BY s.posting_date, p.mode_of_payment
        """.format(
            clauses=clauses
        ),
        values=values,
        as_dict=1,
    )

    def add_net_with_returns(row_dict):
        row = frappe._dict(row_dict)
        return merge(
            row_dict,
            {
                "net_total_after_returns": (row.net_total or 0)
                + (row.returns_grand_total or 0)
            },
        )

    make_row = compose(
        partial(valmap, lambda x: x or None),
        partial(keyfilter, lambda k: k in keys),
        _set_payments(payments),
        add_net_with_returns,
    )

    return [make_row(x) for x in items]


def _set_payments(payments):
    mop_map = compose(
        partial(
            valmap,
            compose(sum, partial(map, lambda x: x or 0), partial(pluck, "amount")),
        ),
        partial(groupby, ("mode_of_payment")),
    )

    payments_grouped = compose(
        partial(valmap, mop_map), partial(groupby, "posting_date")
    )(payments)

    def fn(row):
        mop_payments = payments_grouped.get(row.get("posting_date")) or {}
        cash_amount = (mop_payments.get("Cash") or 0) - (row.get("change_amount") or 0)
        return merge(row, mop_payments, {"Cash": cash_amount})

    return fn
