# Copyright (c) 2013,     9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import today
from functools import partial, reduce
import operator
from toolz import merge, pluck, get, compose, first, flip, groupby, excepts, concatv
from frappe.utils import getdate, add_days, add_months
from frappe.utils import cint
from frappe.utils.data import flt
from datetime import datetime


from pos_bahrain.pos_bahrain.report.item_consumption_report.helpers import (
    generate_intervals,
)
from pos_bahrain.utils import pick


def execute(filters=None):
    clauses, values = _get_filters(filters)
    columns = _get_columns(values)
    data = _get_data(clauses, values, columns,filters)

    make_column = partial(pick, ["label", "fieldname", "fieldtype", "options", "width"])
    return [make_column(x) for x in columns], data


def _get_filters(filters):
    if not filters.get("company"):
        frappe.throw(_("Company is required to generate report"))
    filters.setdefault("brand",None)

    clauses = concatv(
        ["TRUE"],
        ["i.item_group = %(item_group)s"] if filters.item_group else [],
        ["i.brand = %(brand)s"] if filters.brand else [],
        ["i.name = %(item_code)s"] if filters.item_code else [],
        ["id.default_supplier = %(default_supplier)s"]
        if filters.default_supplier
        else [],
        ["i.name IN (SELECT parent FROM `tabItem Barcode` WHERE barcode = %(barcode)s)"]
        if filters.barcode
        else [],
    )
    warehouse_clauses = concatv(
        ["item_code = %(item_code)s"] if filters.item_code else [],
        ["warehouse = %(warehouse)s"]
        if filters.warehouse
        else [
            "warehouse IN (SELECT name FROM `tabWarehouse` WHERE company = %(company)s)"
        ],
    )
    values = merge(
        filters,
        {
            "price_list": frappe.db.get_value(
                "Buying Settings", None, "buying_price_list"
            ),
            "start_date": filters.start_date or today(),
            "end_date": filters.end_date or today(),
        },
    )

    
    return (
        {
            "clauses": " AND ".join(clauses),
            "warehouse_clauses": " AND ".join(warehouse_clauses),
        },
        values,
    )


def _get_columns(filters):
    def make_column(key, label=None, type="Float", options=None, width=90):
        return {
            "label": _(label or key.replace("_", " ").title()),
            "fieldname": key,
            "fieldtype": type,
            "options": options,
            "width": width,
        }

    columns = [
        make_column("item_code", type="Link", options="Item", width=120),
        make_column("barcode", type="Data", width=120),
        make_column("brand", type="Link", options="Brand", width=120),
        make_column("item_group", type="Link", options="Item Group", width=120),
        make_column("item_name", type="Data", width=200),
        make_column("supplier", type="Link", options="Supplier", width=120),
        make_column(
            "price",
            filters.get("price_list", "Standard Buying Price"),
            type="Currency",
            width=120,
        ),
        make_column("stock", "Available Stock"),
        make_column("average_sales_quantity", "Average Sales Quantity", type="Float", width=120),
    ]

    def get_warehouse_columns():
        if not filters.get("warehouse"):
            return [
                merge(make_column(x, x), {"key": x, "is_warehouse": True})
                for x in pluck(
                    "name",
                    frappe.get_all(
                        "Warehouse",
                        filters={
                            "is_group": 0,
                            "disabled": 0,
                            "company": filters.get("company"),
                        },
                        order_by="name",
                    ),
                )
            ]
        return []

    intervals = compose(
        list,
        partial(map, lambda x: merge(x, make_column(x.get("key"), x.get("label")))),
        generate_intervals,
    )
    return (
        columns
        + intervals(
            filters.get("interval"), filters.get("start_date"), filters.get("end_date")
        )
        + get_warehouse_columns()
        + [make_column("total_consumption")]
    )


def _get_data(clauses, values, columns,filters):
    items = frappe.db.sql(
        """
            SELECT
                i.item_code AS item_code,
                (SELECT GROUP_CONCAT(barcode SEPARATOR ', ') FROM `tabItem Barcode`WHERE parent = i.name) AS barcode ,
                i.brand AS brand,
                i.item_name AS item_name,
                i.item_group AS item_group,
                id.default_supplier AS supplier,
                p.price_list_rate AS price,
                b.actual_qty AS stock
            FROM `tabItem` AS i
            LEFT JOIN `tabItem Price` AS p
                ON p.item_code = i.item_code AND p.price_list = %(price_list)s
            LEFT JOIN (
                SELECT
                    item_code, SUM(actual_qty) AS actual_qty
                FROM `tabBin`
                WHERE {warehouse_clauses}
                GROUP BY item_code
            ) AS b
                ON b.item_code = i.item_code
            LEFT JOIN `tabItem Default` AS id
                ON id.parent = i.name AND id.company = %(company)s
            WHERE i.disabled = 0 AND {clauses}
        """.format(
            **clauses
        ),
        values=values,
        as_dict=1,
    )
    def get_number_of_days(start_date, end_date):
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

        return (end_date_obj - start_date_obj).days
    
    for item in items:
        item_qty ={item.item_code:0}
        statuses_to_exclude = ["Cancelled", "Closed"]
        si = frappe.get_all("Sales Order",filters={
                                            "status": ["not in", statuses_to_exclude],
                                            "creation": ["between", [filters["start_date"], filters["end_date"]]]
                                        })

        for i in si:
            so = frappe.get_doc("Sales Order", i.name)
            for x in so.items:
                if x.item_code == item.item_code:
                    item_qty[item.item_code] += x.qty
        total_sales = item_qty[item.item_code]
        number_of_days = 0
        week_average = 0
        number_of_days = get_number_of_days(filters["start_date"], filters["end_date"])
        average_sales_quantity =0
        if filters.get("interval") == None:
            average_sales_quantity = total_sales / number_of_days if number_of_days > 0 else 0

        elif filters.get("interval") == "Weekly":
            week_average = number_of_days / 7
            if week_average < 1:
                week_average = 1
            
            average_sales_quantity = total_sales / week_average

        elif filters.get("interval") == "Monthly":
            month_average = number_of_days / 30
            if month_average < 1:
                month_average = 1
            average_sales_quantity = total_sales / month_average
        else:
            average_sales_quantity = 0
        item["average_sales_quantity"] = average_sales_quantity

    sles = frappe.db.sql(
        """
            SELECT item_code, posting_date, actual_qty, warehouse
            FROM `tabStock Ledger Entry`
            WHERE docstatus < 2 AND
                voucher_type = 'Sales Invoice' AND
                company = %(company)s AND
                {warehouse_clauses} AND
                posting_date BETWEEN %(start_date)s AND %(end_date)s
        """.format(
            **clauses
        ),
        values=values,
        as_dict=1,
    )
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    get_warehouses = compose(list, partial(filter, lambda x: x.get("is_warehouse")))
    get_periods = compose(
        list, partial(filter, lambda x: x.get("start_date") and x.get("end_date"))
    )

    set_warehouse_qty = _set_warehouse_qtys(sles, get_warehouses(columns))
    set_consumption = _set_consumption(sles, get_periods(columns),filters)

    make_row = compose(partial(pick, keys), set_warehouse_qty, set_consumption)
    return [make_row(x) for x in items]


def _set_consumption(sles, periods,filters):
    def groupby_filter(sl):
        def fn(p):
            return p.get("start_date") <= sl.get("posting_date") <= p.get("end_date")

        return fn

    segregate = _make_segregator(sles, groupby_filter, periods)

    total_fn = compose(
        operator.neg,
        sum,
        partial(pluck, "actual_qty"),
        lambda item_code: filter(lambda x: x.get("item_code") == item_code, sles),
    )

    def fn(item):
        item_code = item.get("item_code")
        ##########    AVERAGE SALES CALCULATION - BY USMAN KHALID     ##########################
        ########################################################################################
        number_of_days = 0
        week_average = 0
        def get_number_of_days(start_date, end_date):
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            return (end_date_obj - start_date_obj).days
    
        number_of_days = get_number_of_days(filters["start_date"], filters["end_date"])
        average_sales_quantity =0
        divide = 0
        if filters.get("interval") == None:
            average_sales_quantity = total_fn(item_code) / number_of_days if number_of_days > 0 else 0

        elif filters.get("interval") == "Weekly":
            divide = _difference_weeks(filters["start_date"], filters["end_date"])
            week_average = number_of_days / 7
            if week_average < 1:
                week_average = 1
            average_sales_quantity = total_fn(item_code) / divide
        elif filters.get("interval") == "Monthly":
            divide = _difference_months(filters["start_date"], filters["end_date"])
            month_average = number_of_days / 30
            if month_average < 1:
                month_average = 1
            average_sales_quantity = total_fn(item_code) / divide
        elif filters.get("interval") == "Yearly":
            divide = _difference_years(filters["start_date"], filters["end_date"])
            year_average = number_of_days / 365
            if year_average < 1:
                year_average = 1
            average_sales_quantity = total_fn(item_code) / divide
        else:
            average_sales_quantity = 0
        item["average_sales_quantity"] = average_sales_quantity
        ########################################################################################
        return merge(
            item, segregate(item_code), {"total_consumption": total_fn(item_code)},
        )

    return fn

def _difference_weeks(start_date,end_date):
    d1 = datetime.strptime(start_date, "%Y-%m-%d")
    d2 = datetime.strptime(end_date, "%Y-%m-%d")
    days = (d2 - d1)
    weeks = (days.days) // 7
    if weeks < 1:
        weeks = 1
    return weeks

def _difference_months(start_date,end_date):
    d1 = datetime.strptime(start_date, "%Y-%m-%d")
    d2 = datetime.strptime(end_date, "%Y-%m-%d")
    days = (d2 - d1)
    months = (days.days) // 30
    if months < 1:
        months = 1
    return months   

def _difference_years(start_date,end_date):
    d1 = datetime.strptime(start_date, "%Y-%m-%d")
    d2 = datetime.strptime(end_date, "%Y-%m-%d")
    days = (d2 - d1)
    years = (days.days) // 365
    if years < 1:
        years = 1
    return years


def _set_warehouse_qtys(sles, warehouses):
    def groupby_filter(sl):
        def fn(w):
            return w.get("key") == sl.get("warehouse")

        return fn

    segregate = _make_segregator(sles, groupby_filter, warehouses)

    def fn(item):
        item_code = item.get("item_code")
        return merge(item, segregate(item_code))

    return fn


def _make_segregator(sles, groupby_filter, partitions):
    groupby_fn = compose(
        partial(get, "key", default=None),
        excepts(StopIteration, first, lambda __: {}),
        partial(flip, filter, partitions),
        groupby_filter,
    )

    sles_grouped = groupby(groupby_fn, sles)

    def seg_filter(x):
        return lambda sl: sl.get("item_code") == x

    summer = compose(operator.neg, sum, partial(pluck, "actual_qty"))

    def seg_reducer(item_code):
        def fn(a, p):
            key = get("key", p, None)
            seger = get("seger", p, lambda __: None)
            return merge(a, {key: seger(item_code)})

        return fn

    segregator_fns = [
        merge(
            x,
            {
                "seger": compose(
                    summer,
                    partial(flip, filter, get(x.get("key"), sles_grouped, [])),
                    seg_filter,
                )
            },
        )
        for x in partitions
    ]

    def fn(item_code):
        return reduce(seg_reducer(item_code), segregator_fns, {})

    return fn
