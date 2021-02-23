# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from functools import partial
from toolz import compose, pluck, merge, groupby, concatv


def execute(filters=None):
    columns = _get_columns(filters)
    data = _get_data(_get_clauses(filters), filters)
    return columns, data


def _get_columns(filters):
    def make_column(key, label, type="Float", options=None, width=90):
        return {
            "label": _(label),
            "fieldname": key,
            "fieldtype": type,
            "options": options,
            "width": width,
        }
    return [
        make_column("sales_employee", "Sales Employee", type="Link", options="Employee", width=180),
        make_column("sales_employee_name", "Sales Employee Name", type="Data", width=180),
        make_column("item_code", "Item Code", type="Link", options="Item", width=120),
        make_column("item_name", "Item Name", type="Data", width=180),
        make_column("paid_qty", "Paid Qty"),
        make_column("free_qty", "Free Qty"),
        make_column("gross", "Gross", type="Currency", width=120),
    ]


def _get_clauses(filters):
    clauses = [
        "si.docstatus = 1",
        "si.is_return = 0",
        "si.posting_date BETWEEN %(from_date)s AND %(to_date)s",
    ]
    if filters.get("sales_employee"):
        clauses.append("si.pb_sales_employee = %(sales_employee)s")
    return " AND ".join(clauses)


def _get_data(clauses, args):
    items = frappe.db.sql(
        """
            SELECT
                sii.item_code AS item_code,
                sii.item_name AS item_name,
                SUM(siim.qty) AS paid_qty,
                SUM(siiz.qty) AS free_qty,
                SUM(sii.amount) AS gross,
                si.pb_sales_employee AS sales_employee,
                si.pb_sales_employee_name AS sales_employee_name
            FROM `tabSales Invoice Item` AS sii
            LEFT JOIN (
                SELECT name, qty FROM `tabSales Invoice Item` WHERE amount > 0
            ) AS siim ON siim.name = sii.name
            LEFT JOIN (
                SELECT name, qty FROM `tabSales Invoice Item` WHERE amount = 0
            ) AS siiz ON siiz.name = sii.name
            LEFT JOIN `tabSales Invoice` AS si ON sii.parent = si.name
            WHERE {clauses}
            GROUP BY si.pb_sales_employee, sii.item_code
        """.format(
            clauses=clauses
        ),
        values=args,
        as_dict=1,
    )

    return _group(items)


def _group(items):
    def sum_by(key):
        return compose(sum, partial(map, lambda x: x or 0), partial(pluck, key))

    def subtotal(sales_employee):
        def fn(grouped_items):
            return concatv(
                [
                    {
                        "sales_employee": sales_employee,
                        "paid_qty": sum_by("paid_qty")(grouped_items),
                        "free_qty": sum_by("free_qty")(grouped_items),
                        "gross": sum_by("gross")(grouped_items),
                    }
                ],
                grouped_items,
            )

        return fn

    def set_parent(sales_employee):
        return compose(
            list,
            partial(
                map,
                lambda x: merge(x, {"parent": sales_employee, "sales_employee": None}),
            ),
        )

    transformed = {
        sales_employee: compose(subtotal(sales_employee), set_parent(sales_employee))(
            grouped_items
        )
        for sales_employee, grouped_items in groupby("sales_employee", items).items()
    }
    return compose(list, concatv)(*transformed.values()) + [
        {
            "sales_employee": _("Total"),
            "paid_qty": sum_by("paid_qty")(items),
            "free_qty": sum_by("free_qty")(items),
            "gross": sum_by("gross")(items),
        }
    ]
