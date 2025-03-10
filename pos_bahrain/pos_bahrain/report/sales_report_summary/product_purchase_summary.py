# Copyright (c) 2013, 9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import _
import frappe
import json

def execute(filters=None):
    columns = [
        {
            'fieldname': 'item_code',
            'label': _('Item Code'),
            'fieldtype': 'Data'
        },
        {
            'fieldname': 'summary_qty',
            'label': _('Summary QTY'),
            'fieldtype': 'Float'    
        },
        {
            'fieldname': 'net_total',
            'label': _('Net Total'),
            'fieldtype': 'Currency'    
        },
        {
            'fieldname': 'tax_amount',
            'label': _('Tax Amount'),
            'fieldtype': 'Currency'    
        },
        {
            'fieldname': 'gross_amount',
            'label': _('Gross Amount'),
            'fieldtype': 'Currency'    
        }
    ]

    data = []

    sales_filters = "docstatus = 1"
    sales_values = []
    
    if filters.get("company"):
        sales_filters += " AND company = %s"
        sales_values.append(filters["company"])
    
    if filters.get("start_date") and filters.get("end_date"):
        sales_filters += " AND posting_date BETWEEN %s AND %s"
        sales_values.extend([filters["start_date"], filters["end_date"]])
    
    sales_invoices = frappe.db.sql(
        f"""
        SELECT name
        FROM `tabSales Invoice`
        WHERE {sales_filters}
        """, 
        tuple(sales_values), as_dict=True
    )
    invoice_names = [inv.name for inv in sales_invoices]
    
    if not invoice_names:
        return columns, data
    
    
    taxes = frappe.db.sql(
        f"""
        SELECT parent, tax_amount
        FROM `tabSales Taxes and Charges`
        WHERE parent IN ({', '.join(['%s'] * len(invoice_names))})
        """, 
        tuple(invoice_names), as_dict=True
    )
    
    tax_dict = {}
    for tax in taxes:
        tax_dict.setdefault(tax.parent, 0)
        tax_dict[tax.parent] += tax.tax_amount
    
    items = frappe.db.sql("SELECT item_code FROM `tabItem`", as_dict=True)
    for item in items:
        summary_qty = 0
        net_total = 0
        tax_amount = 0 
        gross_amount = 0
        sales_item_filters = "parent IN ({})".format(", ".join(["%s"] * len(invoice_names)))
        sales_item_values = invoice_names
        sales_item_filters += " AND item_code = %s"
        sales_item_values.append(item.item_code)
        if filters.get("warehouse"):
            sales_item_filters += " AND set_warehouse = %s"
            sales_item_values.append(filters["warehouse"])
        
        sales = frappe.db.sql(
            f"""
            SELECT item_code, qty, net_amount, amount, parent
            FROM `tabSales Invoice Item`
            WHERE {sales_item_filters}
            """, 
            tuple(sales_item_values), as_dict=True
        )
      
        if sales:
            for sale in sales:
                summary_qty += sale.qty
                net_total += sale.net_amount
                net_total += sale.amount if sale.amount else 0
                tax_amount += tax_dict.get(sale.parent, 0)
        gross_amount = net_total + tax_amount
        
        data.append([item.item_code, summary_qty, net_total, tax_amount, gross_amount])
    
    return columns, data
