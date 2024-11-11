# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, scrub
import json
import numpy
from datetime import date

def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = [
        {"fieldname": "invoice_date", "label": _("Tax Invoice Date"), "fieldtype": "Data", "width": 120},
        {"fieldname": "sales_man", "label": _("Sales Man"), "fieldtype": "Data", "width": 150},
        {"fieldname": "customer", "label": _("Customer Name"), "fieldtype": "Data", "width": 160},
        {"fieldname": "invoice_no", "label": _("Description"), "fieldtype": "Link", "options": "Sales Invoice", "width": 100},
        {"fieldname": "amount_before_discount", "label": _("Amount Before Discount"), "fieldtype": "Float", "width": 100, "precision": 3},
        {"fieldname": "discount", "label": _("Discount"), "fieldtype": "Float", "width": 80, "precision": 3},
        {"fieldname": "amount_after_discount", "label": _("Amount After Discount"), "fieldtype": "Float", "width": 100, "precision": 3},
        {"fieldname": "vat", "label": _("VAT"), "fieldtype": "Float", "width": 60, "precision": 3},
        {"fieldname": "valuation_rate", "label": _("Cost of Sales"), "fieldtype": "Float", "width": 100, "precision": 3},
        {"fieldname": "total_sales", "label": _("Total Sales"), "fieldtype": "Float", "width": 80, "precision": 3},
        {"fieldname": "payment", "label": _("Payment"), "fieldtype": "Float", "width": 80, "precision": 3},
        {"fieldname": "outstanding", "label": _("Outstanding"), "fieldtype": "Float", "width": 100, "precision": 3},
        {"fieldname": "mode_of_payment", "label": _("Payment Method"), "fieldtype": "Data", "width": 100},
        {"fieldname": "disc_percent", "label": _("Discount %"), "fieldtype": "Data", "width": 100}
    ]

    data = get_data(filters.get("from_date"), filters.get("to_date"))
    return columns, data

def get_data(from_date, to_date):
    total_field = "si.grand_total" 
    inv_data = frappe.db.sql(f"""
        SELECT
            si.posting_date AS invoice_date,
            si.pb_sales_employee_name AS sales_man,
            si.customer_name AS customer,
            si.name AS invoice_no,
            (SELECT sum(inv_item.price_list_rate * inv_item.qty) AS amount_before_discount
             FROM `tabSales Invoice Item` inv_item WHERE parent = si.name) AS amount_before_discount,
            (SELECT sum(inv_item.discount_amount * inv_item.qty)
             FROM `tabSales Invoice Item` inv_item WHERE parent = si.name) + si.discount_amount AS discount,
            (SELECT (sum(inv_item.amount) - si.discount_amount) FROM tabSales Invoice Item inv_item WHERE parent = si.name) AS amount_after_discount,
            si.total_taxes_and_charges AS vat,
            si.grand_total AS total_sales,
            ({total_field} - si.outstanding_amount) AS payment,
            si.outstanding_amount AS outstanding,
            IFNULL(ip.mode_of_payment, pe.mode_of_payment) AS mode_of_payment,
            round(((SELECT sum(inv_item.discount_amount * inv_item.qty)
                     FROM `tabSales Invoice Item` inv_item WHERE parent = si.name) + si.discount_amount) /
                  ((SELECT sum(inv_item.discount_amount * inv_item.qty)
                     FROM `tabSales Invoice Item` inv_item WHERE parent = si.name) + si.discount_amount + si.total) * 100, 3) AS disc_percent
        FROM
            `tabSales Invoice` si
        LEFT JOIN
            `tabSales Invoice Payment` ip ON ip.parent = si.name
        LEFT JOIN
            `tabPayment Entry Reference` per ON per.reference_name = si.name
        LEFT JOIN
            `tabPayment Entry` pe ON pe.name = per.parent
        WHERE
            si.docstatus = 1 AND si.posting_date BETWEEN '{from_date}' AND '{to_date}'
        GROUP BY
            si.name
    """, as_dict=1)

    inv_data_with_cos = get_cost_of_sales(inv_data)
    inv_data_return = negative_values_for_return(inv_data_with_cos)
    return inv_data_return

def get_cost_of_sales(inv_data):
    for invoice in inv_data:
        items = frappe.db.sql(f"""
            SELECT item_code, qty FROM `tabSales Invoice Item` WHERE parent = '{invoice.invoice_no}'
        """, as_dict=1)
        valuation_rate = 0
        for item in items:
            val_rate = frappe.db.sql(f"""
                SELECT valuation_rate FROM `tabStock Ledger Entry`
                WHERE item_code = '{item.item_code}'
                ORDER BY posting_date DESC, posting_time DESC LIMIT 1
            """)
            if val_rate:
                valuation_rate += val_rate[0][0] * item.qty

        invoice.update({"valuation_rate": valuation_rate})

    return inv_data

def negative_values_for_return(inv_data):
    for inv in inv_data:
        if inv.is_return == 1:
            pass

    return inv_data
