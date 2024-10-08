# Copyright (c) 2013,     9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import today
from functools import partial, reduce
from toolz import (
    merge,
    pluck,
    get,
    compose,
    first,
    flip,
    groupby,
    excepts,
    concat,
    keyfilter,
)

from pos_bahrain.pos_bahrain.report.item_consumption_report.helpers import (
    generate_intervals,
)


def execute(filters=None):
    args = _get_args(filters)
    columns = _get_columns(args)
    data = _get_data(args, columns)
    make_column = partial(
        keyfilter,
        lambda k: k in ["label", "fieldname", "fieldtype", "options", "width"],
    )
    return [make_column(x) for x in columns], data


def _get_args(filters={}):
    if not filters.get("customer"):
        frappe.throw(_("Customer is required to generate report"))
    return merge(
        filters,
        {
            "start_date": filters.get("start_date") or today(),
            "end_date": filters.get("end_date") or today(),
        },
    )


def _get_columns(args):
    def make_column(key, label, type="Currency", options=None, width=120):
        return {
            "label": _(label),
            "fieldname": key,
            "fieldtype": type,
            "options": options,
            "width": width,
        }

    def add_interval_column(column):
        return [
            merge(
                column,
                make_column(
                    column.get("key"),
                    "{} Qty".format(column.get("label")),
                    type="Float",
                    width=90,
                ),
            ),
            make_column(
                "{}_amount".format(column.get("key")),
                "{} Amount".format(column.get("label")),
            ),
        ]

    columns = [
        make_column("item_code", "Item Code", type="Link", options="Item"),
        make_column("item_name", "Item Name", type="Data", width=180),
    ]
    intervals = compose(
        list, concat, partial(map, add_interval_column), generate_intervals
    )
    return (
        columns
        + intervals(args.get("interval"), args.get("start_date"), args.get("end_date"))
        + [
            make_column("total_qty", "Total Qty", type="Float", width=90),
            make_column("total_amount", "Total Amount"),
        ]
    )


def _get_data(args, columns):
    items = frappe.db.sql(
        """
            SELECT item_code, item_name FROM `tabItem` WHERE disabled != 1
        """,
        as_dict=1,
    )
    sales = frappe.db.sql(
        """
            SELECT
                sii.item_code AS item_code,
                sii.qty AS qty,
                sii.amount AS amount,
                si.posting_date AS posting_date
            FROM `tabSales Invoice Item` AS sii
            LEFT JOIN `tabSales Invoice` AS si ON sii.parent = si.name
            WHERE
                si.docstatus = 1 AND
                si.customer = %(customer)s AND
                si.posting_date BETWEEN %(start_date)s AND %(end_date)s
        """,
        values={
            "customer": args.get("customer"),
            "start_date": args.get("start_date"),
            "end_date": args.get("end_date"),
        },
        as_dict=1,
    )
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    periods = list(filter(lambda x: x.get("start_date") and x.get("end_date"), columns))

    make_data = compose(
        list,
        partial(map, partial(keyfilter, lambda k: k in keys)),
        partial(filter, lambda x: x.get("total_qty") > 0),
        partial(map, _set_period_columns(sales, periods)),
    )

    return make_data(items)


def _set_period_columns(sales, periods):
    def groupby_filter(sl):
        def fn(p):
            return p.get("start_date") <= sl.get("posting_date") <= p.get("end_date")

        return fn

    groupby_fn = compose(
        partial(get, "key", default=None),
        excepts(StopIteration, first, lambda __: {}),
        partial(flip, filter, periods),
        groupby_filter,
    )

    sales_grouped = groupby(groupby_fn, sales)

    def summer(key):
        return compose(sum, partial(pluck, key))

    def seg_filter(x):
        return lambda sale: sale.get("item_code") == x

    def seger(sum_fn, x):
        return compose(
            sum_fn,
            partial(flip, filter, get(x.get("key"), sales_grouped, [])),
            seg_filter,
        )

    def total_fn(sum_fn):
        return compose(sum_fn, partial(flip, filter, sales), seg_filter)

    summer_qty = summer("qty")
    summer_amount = summer("amount")

    segregator_fns = [
        merge(
            x,
            {
                "seger_qty": seger(summer_qty, x),
                "seger_amount": seger(summer_amount, x),
            },
        )
        for x in periods
    ]

    def seg_reducer(item_code):
        def fn(a, p):
            key = get("key", p, None)
            seger_qty = get("seger_qty", p, lambda __: None)
            seger_amount = get("seger_amount", p, lambda __: None)
            return merge(
                a,
                {
                    key: seger_qty(item_code),
                    "{}_amount".format(key): seger_amount(item_code),
                },
            )

        return fn

    def fn(item):
        item_code = item.get("item_code")
        total_qty = total_fn(summer_qty)
        total_amount = total_fn(summer_amount)
        return merge(
            item,
            reduce(seg_reducer(item_code), segregator_fns, {}),
            {
                "total_qty": total_qty(item_code),
                "total_amount": total_amount(item_code),
            },
        )

    return fn
