# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, date_diff

data = []
columns = []

def execute(filters=None):
	return get_columns(), get_data(filters)

def get_columns():
	return [
	{
			'fieldname': 'item',
			'label': _('Item'),
			'fieldtype': 'Link',
			'options': 'Item'
		},
		{
			'fieldname': 'item_name',
			'label': _('Item Name'),
			'fieldtype': 'Data',

		},
		{
			'fieldname': 'unit',
			'label': _('Unit'),
			'fieldtype':'Link',
			'options': 'UOM'
		},
		{
			'fieldname': 'last_purchase_invoice_date',
			'label': _('Last Purchase Invoice Date '),
			'fieldtype':'Date',
			
		},
		{
			'fieldname': 'last_sales_invoice_date',
			'label': _('Last Sales Invoice Date '),
			'fieldtype':'Date',
			
		},
		{
			'fieldname': 'total_sales',
			'label': _(' Total Sales'),
			'fieldtype':'Float',
			
		},
		{
			'fieldname': 'percentage',
			'label': _('Percentage %'),
			'fieldtype':'Float',
			
		},
		{
			'fieldname': 'expected_total_sales',
			'label': _('Expected Total Sale'),
			'fieldtype':'Float',
			
		},
		{
			'fieldname': 'min',
			'label': _('Min'),
			'fieldtype':'Float',
			
		},
		{
			'fieldname': 'available_quantity',
			'label': _('Available Quantity'),
			'fieldtype':'Float',
			
		},
		{
			'fieldname': 'on_purchase',
			'label': _('On Purchase'),
			'fieldtype':'Float',
			
		},
		{
			'fieldname': 'available_total_qty',
			'label': _('Available Total Qty'),
			'fieldtype':'Float',
			
		},
		{
			'fieldname': 'total_months_in_report',
			'label': _('Total Months In report'),
			'fieldtype':'Int',
			
		},
		{
			'fieldname': 'monthy_sales',
			'label': _('Monthy Sales'),
			'fieldtype':'Int',
			
		},
		{
			'fieldname': 'annual_sales',
			'label': _('Annual Sales'),
			'fieldtype':'Int',
			
		},
		{
			'fieldname': 'months_to_arrive',
			'label': _('Months To Arrive'),
			'fieldtype':'Float',
			
		},
		{
			'fieldname': 'period_expected_sales',
			'label': _('Period Expected Sales'),
			'fieldtype':'Int',
			
		},
		{
			'fieldname': 'shortage_happened',
			'label': _('Shortage Happend'),
			'fieldtype':'Int',
			
		},
		{
			'fieldname': 'expected_order_quantity',
			'label': _('Expected Order Quantity'),
			'fieldtype':'Int',
			
		},

	]


def get_data(filters):
	data.clear()
	item_filters = {}
	stock_ledger_sales_filters = {}
	stock_ledger_purchase_filters = {}
	if filters.item :
		item_filters.update({'item_code':filters.item})
	if filters.item_group and frappe.db.get_value("Item Group",filters.item_group, 'is_group' ) == 0:
		item_filters.update({'item_group':filters.item_group})
	if filters.item_group and frappe.db.get_value("Item Group",filters.item_group, 'is_group' ) == 1:
		item_groups_list  = []
		item_groups = frappe.db.get_list('Item Group', {'parent_item_group': filters.item_group})
		for item in item_groups:
			item_groups_list.append(item.name)
		item_filters.update({'item_group':['in', item_groups_list]})
	items = frappe.db.get_list('Item', filters=item_filters,  fields=['*'])
	for item in items:
			item_delivery_notes_qty = frappe.db.count("Delivery Note Item", {"item_code": item.name})
			on_purchase = 0
			total_sales = item_delivery_notes_qty
			sales_total_sales = []
			purchase_total_sales = []
			last_purchase_invoice_date = ''
			last_sales_invoice_date = ''
			stock_ledger_sales_filters.update({'docstatus':1,  'posting_date': ['between', [filters.start_date, filters.end_date]]})
			stock_ledger_purchase_filters.update({'voucher_type':'Purchase Invoice', 'item_code':item.name, 'posting_date': ['between', [filters.start_date, filters.end_date]]})
			if frappe.db.get_value('Bin', {'item_code': item.name} , 'ordered_qty'):
				on_purchase = frappe.db.get_value('Bin', {'item_code': item.name} , 'ordered_qty')
			available_qty = 0
			if frappe.db.get_value('Bin', {'item_code': item.name} , 'actual_qty'):
				warehouse = frappe.db.get_list('Warehouse', fields=['*'])
				for ware in warehouse:
					available_qty += frappe.db.get_value('Bin', {'item_code': item.name, 'warehouse':ware.name} , 'actual_qty') if frappe.db.get_value('Bin', {'item_code': item.name, 'warehouse':ware.name} , 'actual_qty') else 0
			#frappe.throw(f"{get_last_purchase_stock_ledger_entry({'item_code':'Beans', 'start_date':filters.start_date, 'end_date':filters.end_date})}")
			if get_last_purchase_stock_ledger_entry({'item_code':item.item_code, 'start_date':filters.start_date, "end_date":filters.end_date}) != []:
				last_purchase_invoice_date = get_last_purchase_stock_ledger_entry({'item_code':item.item_code, 'start_date':filters.start_date, "end_date":filters.end_date})[0]["posting_date"]
			if get_last_sales_stock_ledger_entry({'item_code':item.item_code, 'start_date':filters.start_date, "end_date":filters.end_date}) != []:
				last_sales_invoice_date = get_last_sales_stock_ledger_entry({'item_code':item.item_code, 'start_date':filters.start_date, "end_date":filters.end_date})[0]["posting_date"]
			
			if frappe.db.get_list('Sales Invoice', filters=stock_ledger_sales_filters, fields=['*']):
				sales_total_sales = frappe.db.get_list('Sales Invoice', filters=stock_ledger_sales_filters, fields=['*'])
			if frappe.db.get_list('Stock Ledger Entry', filters=stock_ledger_purchase_filters, fields=['*']):
				purchase_total_sales = frappe.db.get_list('Stock Ledger Entry', filters=stock_ledger_purchase_filters, fields=['*'])
			for sale in sales_total_sales :
				item_sales = frappe.db.get_list('Sales Invoice Item', filters={'parent': sale.name, 'item_code':item.item_code}, fields=['*'])
				if item_sales != []:
					for item_sale in item_sales:
						total_sales+= item_sale.qty
			
			expected_sales = total_sales + (total_sales * float(filters.percentage)/ 100)
			total_months_in_report =  date_diff(filters.end_date , filters.start_date) / 30 if date_diff(filters.end_date , filters.start_date)>=30 else 0
			monthly_sales = int(expected_sales) / int(total_months_in_report) if total_months_in_report != 0 else 0
			annual_sales = monthly_sales * 12
			period_expected_sales = monthly_sales * float(filters.months_to_arrive)
			shortage_happened = (available_qty + on_purchase) -period_expected_sales 
			min = monthly_sales * float(filters.minimum_months)
			expected_order_quantity = shortage_happened - min - min
			data.append([item.name , item.item_name, item.stock_uom, last_purchase_invoice_date, last_sales_invoice_date, total_sales, float(filters.percentage), expected_sales, min, available_qty, on_purchase, available_qty + on_purchase, total_months_in_report, monthly_sales ,annual_sales, float(filters.months_to_arrive), period_expected_sales, shortage_happened, expected_order_quantity])
	return data



def get_last_sales_stock_ledger_entry(filters=None):
	query = frappe.db.sql("""
        SELECT
            sle.posting_date
        FROM
            `tabStock Ledger Entry` AS sle
		WHERE
            sle.voucher_type = 'Sales Invoice'
            AND sle.item_code = %(item_code)s
            AND sle.posting_date BETWEEN %(start_date)s AND %(end_date)s
        ORDER BY
            sle.creation DESC
        LIMIT 1
    """, values=filters,as_dict=1)
	return query

def get_last_purchase_stock_ledger_entry(filters=None):
	query = frappe.db.sql("""
        SELECT
            sle.posting_date
        FROM
            `tabStock Ledger Entry` AS sle
		WHERE
            sle.voucher_type = 'Purchase Invoice'
            AND sle.item_code = %(item_code)s
            AND sle.posting_date BETWEEN %(start_date)s AND %(end_date)s
        ORDER BY
            sle.creation DESC
	    LIMIT 1
    """, values=filters,as_dict=1)
	return query
	