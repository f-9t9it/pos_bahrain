# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from functools import partial
from toolz import compose, pluck, merge

from pos_bahrain.utils import pick


def execute(filters=None):
    columns = _get_columns(filters)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns(filters):
    def make_column(key, label=None, type="Data", options=None, width=120):
        return {
            "label": _(label or key.replace("_", " ").title()),
            "fieldname": key,
            "fieldtype": type,
            "options": options,
            "width": width,
        }

    return [
        make_column("invoice", type="Link", options="Sales Invoice"),
        make_column("posting_date", "Date", type="Date"),
        make_column("posting_time", "Time", type="Time"),
        make_column("cash"),
    ]


def _get_filters(filters):
    clauses = [
        "si.docstatus = 1",
        "si.posting_date BETWEEN %(from_date)s AND %(to_date)s",
    ]
    return " AND ".join(clauses), filters


def _get_data(clauses, values, keys):
    result = frappe.db.sql(
        """
            SELECT
                si.name AS invoice,
                si.posting_date AS posting_date,
                si.posting_time AS posting_time,
                SUM(sip.amount) AS cash_amount,
                si.change_amount AS change_amount
            FROM `tabSales Invoice` AS si
            RIGHT JOIN `tabSales Invoice Payment` AS sip ON
                sip.parent = si.name AND sip.mode_of_payment = 'Cash'
            WHERE {clauses}
            GROUP BY si.name
        """.format(
            clauses=clauses
        ),
        values=values,
        as_dict=1,
    )

    def set_cash(row):
        return merge(row, {"cash": row.cash_amount - row.change_amount})

    make_row = compose(partial(pick, keys), set_cash)
    return [make_row(x) for x in result]
