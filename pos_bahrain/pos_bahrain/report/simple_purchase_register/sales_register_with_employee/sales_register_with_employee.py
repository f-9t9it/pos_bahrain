# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.accounts.report.sales_register.sales_register import (
    execute as sales_register,
)
from toolz.curried import groupby, first, compose, valmap, concatv, merge


def execute(filters=None):
    filters.net_amount_col = "net_total"
    return extend_report(sales_register, filters)


def extend_report(base_execute, filters):
    _validate_filters(filters)
    results = iter(base_execute(filters))
    columns, data = next(results), next(results)
    return (
        _extend_columns(filters, columns),
        _extend_data(filters, data),
    )


def _validate_filters(filters):
    if not 0 <= frappe.utils.flt(filters.commission_rate) <= 100:
        frappe.throw(frappe._("Commission Rate should be between 0 and 100%"))


def _extend_columns(filters, columns):
    return (
        [
            {
                "label": frappe._("Sales Employee"),
                "fieldname": "sales_employee",
                "fieldtype": "Link",
                "options": "Employee",
                "width": 120,
            },
            {
                "label": frappe._("Sales Employee Name"),
                "fieldname": "sales_employee_name",
                "fieldtype": "Data",
                "width": 150,
            },
        ]
        + columns
        + [
            {
                "label": frappe._(
                    "{}% Commission on Net Sales".format(
                        frappe.utils.flt(filters.commission_rate)
                    )
                ),
                "fieldname": "net_sales_commission",
                "fieldtype": "Currency",
                "width": 120,
            },
        ]
    )


def _extend_data(filters, data):
    invoices = [x.get("invoice") for x in data]
    get_employee_map = compose(
        valmap(
            lambda x: {
                "sales_employee": x.get("pb_sales_employee"),
                "sales_employee_name": x.get("pb_sales_employee_name"),
            }
        ),
        valmap(first),
        groupby("name"),
        lambda: frappe.db.sql(
            """
            SELECT name, pb_sales_employee, pb_sales_employee_name FROM `tabSales Invoice`
            WHERE name IN %(invoices)s
        """,
            values={"invoices": invoices},
            as_dict=1,
        ),
    )
    employees = get_employee_map() if invoices else {}
    set_employee = compose(lambda x: merge(x, employees.get(x.get("invoice"))))

    commission_rate = filters.get("commission_rate")
    set_commission = compose(
        lambda x: merge(
            x,
            {
                "net_sales_commission": x.get(filters.net_amount_col, 0.00)
                * frappe.utils.flt(commission_rate)
                / 100
            },
        ),
    )

    make_row = compose(set_commission, set_employee)
    extended = [make_row(x) for x in data]

    if not filters.sales_employee:
        return extended

    return [x for x in extended if x.get("sales_employee") == filters.sales_employee]
