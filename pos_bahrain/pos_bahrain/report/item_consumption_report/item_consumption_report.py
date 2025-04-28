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
from erpnext.stock.utils import get_stock_balance


from pos_bahrain.pos_bahrain.report.item_consumption_report.helpers import (
    generate_intervals,
)
from pos_bahrain.utils import pick


def execute(filters=None):
    warehouses = frappe.get_all(
        "Warehouse",
        filters={"is_group": 0, "disabled": 0, "company": filters.get("company")},
        
    )

    warehouses = [x.name for x in warehouses]

    warehouse_columns = ", ".join(
        [f"SUM(CASE WHEN sles.warehouse = '{warehouse}' THEN sles.actual_qty ELSE 0 END) * -1 AS `{warehouse}`" for warehouse in warehouses]
    )
    clauses, values = _get_filters(filters)
    columns = _get_columns(values)
    data = _get_data(clauses, values, columns,filters, warehouse_columns)

    make_column = partial(pick, ["label", "fieldname", "fieldtype", "options", "width"])
    return [make_column(x) for x in columns], data


def _get_filters(filters):
    if not filters.get("company"):
        frappe.throw(_("Company is required to generate report"))
    filters.setdefault("brand",None)

    clauses = concatv(
        ["TRUE"],
        ["i.is_stock_item = 1"],
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

    additional_warehouse = filters.get("additional_warehouse")
    if additional_warehouse:
        columns.append(
            make_column(
                "additional_warehouse_stock_qty", 
                label="Add Ware Stock Qty", 
                type="Float",
                width=140
            )
        )

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


def _get_data(clauses, values, columns,filters, warehouse_columns):
    values['interval'] = filters.get('interval')
    items = frappe.db.sql(
         """
                    SELECT
                i.item_code AS item_code,
                (SELECT GROUP_CONCAT(barcode SEPARATOR ', ') FROM `tabItem Barcode` WHERE parent = i.name) AS barcode,
                i.brand AS brand,
                i.item_name AS item_name,
                i.item_group AS item_group,
                id.default_supplier AS supplier,
                MAX(p.price_list_rate) AS price,
                b.actual_qty AS stock,
                so.total_sales AS total_sales,
                 CASE 
                    WHEN %(interval)s is NULL THEN
                        0
                    WHEN %(interval)s = 'Daily' THEN 
                        (so.total_sales / DATEDIFF(%(end_date)s, %(start_date)s))
                    WHEN %(interval)s = 'Weekly' THEN 
                        (so.total_sales / GREATEST(1, DATEDIFF(%(end_date)s, %(start_date)s) / 7))
                    WHEN %(interval)s = 'Monthly' THEN 
                        (so.total_sales / GREATEST(1, DATEDIFF(%(end_date)s, %(start_date)s) / 30))
                    WHEN %(interval)s = 'Yearly' THEN 
                        (so.total_sales / GREATEST(1, DATEDIFF(%(end_date)s, %(start_date)s) / 365))
                    ELSE 0
                END AS average_sales_quantity,
                CASE 
                     WHEN %(interval)s is NULL THEN
                        0
                    WHEN %(interval)s = 'Daily' THEN  
                        (   SUM(CASE WHEN sles.warehouse IS NOT NULL  THEN sles.actual_qty ELSE 0 END) * -1  / DATEDIFF(%(end_date)s, %(start_date)s))
                    WHEN %(interval)s = 'Weekly' THEN 
                        (   SUM(CASE WHEN sles.warehouse IS NOT NULL  THEN sles.actual_qty ELSE 0 END) * -1  / GREATEST(1, DATEDIFF(%(end_date)s, %(start_date)s) / 7))
                    WHEN %(interval)s = 'Monthly' THEN 
                        (   SUM(CASE WHEN sles.warehouse IS NOT NULL  THEN sles.actual_qty ELSE 0 END) * -1  / GREATEST(1, DATEDIFF(%(end_date)s, %(start_date)s) / 30))
                    WHEN %(interval)s = 'Yearly' THEN 
                        (   SUM(CASE WHEN sles.warehouse IS NOT NULL  THEN sles.actual_qty ELSE 0 END) * -1  / GREATEST(1, DATEDIFF(%(end_date)s, %(start_date)s) / 365))
                    ELSE 0
                END AS average_sales_quantity,
                SUM(CASE WHEN sles.warehouse IS NOT NULL  THEN sles.actual_qty ELSE 0 END) * -1 AS total_consumption,
                {warehouse_columns}
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
            LEFT JOIN (
                SELECT 
                    item_code, 
                    SUM(qty) AS total_sales 
                FROM `tabSales Order Item` 
                WHERE creation BETWEEN %(start_date)s AND %(end_date)s AND docstatus = 1
                GROUP BY item_code
            ) AS so
                ON so.item_code = i.item_code
            LEFT JOIN `tabStock Ledger Entry` AS sles
                ON sles.item_code = i.item_code AND sles.posting_date BETWEEN %(start_date)s AND %(end_date)s AND sles.docstatus <2 AND  sles.voucher_type = 'Sales Invoice' AND
                sles.company = %(company)s AND
                {warehouse_clauses} 
            WHERE i.disabled = 0 AND {clauses}
            GROUP BY
                i.item_code, i.brand, i.item_name, i.item_group, id.default_supplier, b.actual_qty, so.total_sales
        """.format(
            **clauses,
            warehouse_columns = warehouse_columns,
        ),
        values=values,
        as_dict=1,
    ) 
    return items

