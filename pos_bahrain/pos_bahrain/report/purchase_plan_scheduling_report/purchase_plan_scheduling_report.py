# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today, date_diff

data = []
columns = []

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = [
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
			'fieldtype':'Float/1:60',
			
		},
		{
			'fieldname': 'percentage',
			'label': _('Percentage %'),
			'fieldtype':'Float/1:60',
			
		},
		{
			'fieldname': 'expected_total_sales',
			'label': _('Expected Total Sale'),
			'fieldtype':'Float/1:60',
			
		},
		{
			'fieldname': 'min',
			'label': _('Min'),
			'fieldtype':'Float/1:60',
			
		},
		{
			'fieldname': 'available_quantity',
			'label': _('Available Quantity'),
			'fieldtype':'Float/1:60',
			
		},
		{
			'fieldname': 'on_purchase',
			'label': _('On Purchase'),
			'fieldtype':'Float/1:60',
			
		},
		{
			'fieldname': 'available_total_qty',
			'label': _('Available Total Qty'),
			'fieldtype':'Float/1:60',
			
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
			'fieldtype':'Float/1:60',
			
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
			'fieldname': 'minimum_purchase_qty',
			'label': _('Minimum Purchase Qty'),
			'fieldtype': 'Int'
		},
		{
			'fieldname': 'expected_order_quantity',
			'label': _('Expected Order Quantity'),
			'fieldtype':'Int',
			
		},
		{
            		'fieldname': 'priority_month',
            		'label': _('Priority Month'),
            		'fieldtype': 'Int',
       		 }

	]
	if filters and filters.get('uom_conversion'):
		columns.append({
			'fieldname': 'meter',
			'label': _('Meter'),
			'fieldtype': 'Float'
		})
	
	return columns


def get_data(filters):
	data.clear()
	item_filters = {}
	stock_ledger_sales_filters = {}
	stock_ledger_purchase_filters = {}
	stock_ledger_delivery_note = {}
	if filters.item :
		item_filters.update({'item_code':filters.item})
	if filters.item_group and frappe.db.get_value("Item Group",filters.item_group, 'is_group' ) == 0:
		item_filters.update({'item_group':filters.item_group})
	if filters.item_group and frappe.db.get_value("Item Group",filters.item_group, 'is_group' ) == 1:
		item_groups_list  = [filters.item_group]
		item_groups = frappe.db.get_list('Item Group', {'parent_item_group': filters.item_group})
		for item in item_groups:
			item_groups_list.append(item.name)
		for item_group in item_groups:
			if frappe.db.get_value("Item Group", item_group.name, 'is_group' ) == 1:
				children_groups = frappe.db.get_list('Item Group', {'parent_item_group': item_group.name})
				for child in children_groups:
					item_groups_list.append(child.name)
	
		item_filters.update({'item_group':['in', item_groups_list]})
	items = frappe.db.get_list('Item', filters=item_filters,  fields=['*'])
	for item in items:
			# on_purchase = 0
			total_sales =0
			sales_total_sales = []
			delivery_total_sales = []
			purchase_total_sales = []
			last_purchase_invoice_date = ''
			last_sales_invoice_date = ''
			# stock_ledger_sales_filters.update({'docstatus':1, "item_code":item.item_code,  'voucher_type':'Sales Invoice', 'posting_date': ['between', [filters.start_date, filters.end_date]]})
			stock_ledger_sales_filters.update({'docstatus':1, "item_code":item.item_code,  'creation': ['between', [filters.start_date, filters.end_date]]})
			stock_ledger_purchase_filters.update({'voucher_type':'Purchase Invoice', 'item_code':item.name, 'posting_date': ['between', [filters.start_date, filters.end_date]]})
			stock_ledger_delivery_note.update({'voucher_type':'Delivery Note', 'item_code':item.name, 'posting_date': ['between', [filters.start_date, filters.end_date]]})
			# if frappe.db.get_value('Bin', {'item_code': item.item_code} , 'ordered_qty'):
			# 	warehouse = frappe.db.get_list('Warehouse', fields=['*'])
			# 	# on_purchase = frappe.db.get_value('Bin', {'item_code': item.name} , 'ordered_qty')
			# 	for ware in warehouse:
			# 		on_purchase += frappe.db.get_value('Bin', {'item_code': item.name, 'warehouse':ware.name} , 'ordered_qty') if frappe.db.get_value('Bin', {'item_code': item.name, 'warehouse':ware.name} , 'ordered_qty') else 0
			on_purchase = 0
			# if frappe.db.get_value('Bin', {'item_code': item.name} , 'ordered_qty'):
			# 	on_purchase = frappe.db.get_value('Bin', {'item_code': item.name} , 'ordered_qty')
			# if frappe.db.get_value('Bin', {'item_code': item.name} , 'ordered_qty'):
			warehouse = frappe.db.get_list('Warehouse', fields=['*'])
			for ware in warehouse:
				on_purchase += frappe.db.get_value('Bin', {'item_code': item.name, 'warehouse':ware.name} , 'ordered_qty') if frappe.db.get_value('Bin', {'item_code': item.name, 'warehouse':ware.name} , 'ordered_qty') else 0

			available_qty = 0
			# if frappe.db.get_value('Bin', {'item_code': item.name} , 'actual_qty'):
			warehouse = frappe.db.get_list('Warehouse', fields=['*'])
			for ware in warehouse:
				available_qty += frappe.db.get_value('Bin', {'item_code': item.name, 'warehouse':ware.name} , 'actual_qty') if frappe.db.get_value('Bin', {'item_code': item.name, 'warehouse':ware.name} , 'actual_qty') else 0
			#frappe.throw(f"{get_last_purchase_stock_ledger_entry({'item_code':'Beans', 'start_date':filters.start_date, 'end_date':filters.end_date})}")
			if get_last_purchase_stock_ledger_entry({'item_code':item.item_code}) != []:
				last_purchase_invoice_date = get_last_purchase_stock_ledger_entry({'item_code':item.item_code})[0]["posting_date"]
			if get_last_sales_stock_ledger_entry({'item_code':item.item_code}) != []:
				last_sales_invoice_date = get_last_sales_stock_ledger_entry({'item_code':item.item_code})[0]["posting_date"]
			
			# if frappe.db.get_list('Stock Ledger Entry', filters=stock_ledger_sales_filters, fields=['*']):
			# 	sales_total_sales = frappe.db.get_list('Stock Ledger Entry', filters=stock_ledger_sales_filters, fields=['*'])
			if frappe.db.get_list('Sales Invoice Item', filters=stock_ledger_sales_filters, fields=['*']):
				sales_total_sales = frappe.db.get_list('Sales Invoice Item', filters=stock_ledger_sales_filters, fields=['*'])
			if frappe.db.get_list('Stock Ledger Entry', filters=stock_ledger_purchase_filters, fields=['*']):
				purchase_total_sales = frappe.db.get_list('Stock Ledger Entry', filters=stock_ledger_purchase_filters, fields=['*'])
			if frappe.db.get_list('Stock Ledger Entry', filters=stock_ledger_delivery_note, fields=['*']):
				delivery_total_sales = frappe.db.get_list('Stock Ledger Entry', filters=stock_ledger_delivery_note, fields=['*'])
			if sales_total_sales != []:
				for invoices in sales_total_sales:
					# total_sales += -(invoices.actual_qty)
					total_sales += (invoices.qty)
			# if delivery_total_sales != []:
			# 	for delivery in delivery_total_sales:
			# 		total_sales_d += -(delivery.actual_qty)
			expected_sales = total_sales + (total_sales * float(filters.percentage)/ 100)
			total_months_in_report =  date_diff(filters.end_date , filters.start_date) / 30 if date_diff(filters.end_date , filters.start_date)>=30 else 0
			monthly_sales = int(expected_sales) / int(total_months_in_report) if total_months_in_report != 0 else 0
			annual_sales = monthly_sales * 12
			period_expected_sales = monthly_sales * float(filters.months_to_arrive)
			shortage_happened = (available_qty + on_purchase) -period_expected_sales 
			min = monthly_sales * float(filters.minimum_months)
			minimum_purchase_qty = get_minimum_purchase_qty(item.item_code, frappe.defaults.get_user_default("Company"))
			expected_order_quantity = shortage_happened - min - min - minimum_purchase_qty
			priority_month = (available_qty + on_purchase) / monthly_sales if monthly_sales > 0 else 0

			if filters.get('uom_conversion'):
				meter = expected_order_quantity / filters.get('uom_conversion')
			else:
				meter = None

			data.append([item.name , item.item_name, item.stock_uom, last_purchase_invoice_date, last_sales_invoice_date, total_sales, float(filters.percentage), expected_sales, min, available_qty, on_purchase, available_qty + on_purchase, total_months_in_report, monthly_sales ,annual_sales, float(filters.months_to_arrive), period_expected_sales, shortage_happened, minimum_purchase_qty , expected_order_quantity, priority_month , meter])
	return data
	
def get_minimum_purchase_qty(item_code, company_abbr):
	company_abbr = frappe.get_value("Company", company_abbr, "abbr")
	
	reorder_entry = frappe.db.sql("""
		SELECT warehouse_reorder_level
		FROM `tabItem Reorder` ir
		WHERE 
			ir.parent = %(item_code)s
			AND ir.warehouse_group = %(warehouse_group)s
			AND ir.material_request_type = 'Purchase'
	""", values={
		'item_code': item_code,
		'warehouse_group': f"All Warehouses - {company_abbr}"
	}, as_dict=1)

	return reorder_entry[0].warehouse_reorder_level if reorder_entry else 0	

def get_last_sales_stock_ledger_entry(filters=None):
	query = frappe.db.sql("""
		SELECT
			MAX(sle.posting_date) AS posting_date
		FROM
			`tabStock Ledger Entry` AS sle
		WHERE
			(sle.voucher_type = 'Sales Invoice' OR sle.voucher_type = 'Delivery Note')
			AND sle.item_code = %(item_code)s
		GROUP BY
			sle.voucher_type
		ORDER BY
			posting_date DESC
		LIMIT 1
	""", values=filters, as_dict=1)
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
            
        ORDER BY
            sle.creation DESC
	    LIMIT 1
    """, values=filters,as_dict=1)
	return query
	



