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

    columns = [
        make_column("salesman_name", "Salesman Name", type="Data", width=180),
        make_column("item_code", "Item Code", type="Link", options="Item", width=120),
        make_column("item_name", "Item Name", type="Data", width=180),
        make_column("paid_qty", "Paid Qty"),
        make_column("free_qty", "Free Qty"),
        make_column("gross", "Gross", type="Currency", width=120),
    ]
    return columns


def _get_clauses(filters):
    clauses = [
        "si.docstatus = 1",
        "si.is_return = 0",
        "si.posting_date BETWEEN %(from_date)s AND %(to_date)s",
    ]
    if filters.get("salesman"):
        clauses.append("sii.salesman = %(salesman)s")
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
                sii.salesman_name AS salesman_name
            FROM `tabSales Invoice Item` AS sii
            LEFT JOIN (
                SELECT name, qty FROM `tabSales Invoice Item` WHERE amount > 0
            ) AS siim ON siim.name = sii.name
            LEFT JOIN (
                SELECT name, qty FROM `tabSales Invoice Item` WHERE amount = 0
            ) AS siiz ON siiz.name = sii.name
            LEFT JOIN `tabSales Invoice` AS si ON sii.parent = si.name
            WHERE {clauses}
            GROUP BY sii.salesman_name, sii.item_code
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

    def subtotal(salesman_name):
        def fn(grouped_items):
            return concatv(
                [
                    {
                        "salesman_name": salesman_name,
                        "paid_qty": sum_by("paid_qty")(grouped_items),
                        "free_qty": sum_by("free_qty")(grouped_items),
                        "gross": sum_by("gross")(grouped_items),
                    }
                ],
                grouped_items,
            )

        return fn

    def set_parent(salesman_name):
        return compose(
            list,
            partial(
                map,
                lambda x: merge(x, {"parent": salesman_name, "salesman_name": None}),
            ),
        )

    transformed = {
        salesman_name: compose(subtotal(salesman_name), set_parent(salesman_name))(
            grouped_items
        )
        for salesman_name, grouped_items in groupby("salesman_name", items).items()
    }
    return compose(list, concatv)(*transformed.values()) + [
        {
            "salesman_name": _("Total"),
            "paid_qty": sum_by("paid_qty")(items),
            "free_qty": sum_by("free_qty")(items),
            "gross": sum_by("gross")(items),
        }
    ]
