# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.accounts.report.accounts_receivable.accounts_receivable import (
    execute as accounts_receivable,
    ReceivablePayableReport,
)


def execute(filters=None):
    return extend_report(accounts_receivable, filters)


def extend_report(base_execute, filters):
    base_result = base_execute(filters)
    columns, data = base_result[0], base_result[1]
    extended_data = _extend_data(filters, data)
    return columns, extended_data, None, _extend_chart(filters, extended_data)


def _extend_data(filters, data):
    if not filters.cost_center:
        return data
    invoices = [
        x.get("voucher_no") for x in data if x.get("voucher_type") == "Sales Invoice"
    ]
    if not invoices:
        return []

    filtered = [
        x[0]
        for x in frappe.db.sql(
            """
            SELECT name FROM `tabSales Invoice`
            WHERE name IN %(invoices)s AND pb_set_cost_center = %(cost_center)s
        """,
            values={"invoices": invoices, "cost_center": filters.cost_center},
        )
    ]

    return [x for x in data if x.get("voucher_no") in filtered]


def _extend_chart(filters, data):
    rep = ReceivablePayableReport(filters)
    rep.columns = []
    rep.data = data
    rep.setup_ageing_columns()
    rep.get_chart_data()
    return rep.chart
