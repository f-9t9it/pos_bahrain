# Copyright (c) 2026, 	9t9it and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = [], []
	columns = [
		{
			"fieldname": "item_code",
			"label": "Item Code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 150
		},
		{
			"fieldname": "item_name",
			"label": "Item Name",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "item_group",
			"label": "Item Group",
			"fieldtype": "Link",	
		"options": "Item Group",
			"width": 150
		},
		{
			"fieldname": "talabat",
			"label": "Talabat",
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "drn_no",
			"label": "DRN No",
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "Brand",
			"label": "Brand",
			"fieldtype": "Link",
			"options": "Brand",
			"width": 100
		},
		{
			"fieldname": "has_batch",
			"label": "Has Batch",
			"fieldtype": "Int",
			"width": 100
		},
		{
			"fieldname": "barcode",
			"label": "Barcode",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "selling_price_before_vat",
			"label": "Selling Price Before VAT",
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "item_tax_template",
			"label": "Item Tax Template",
			"fieldtype": "Link",
			"options": "Item Tax Template",
			"width": 100
		},
		{
			"fieldname": "selling_price_after_vat",
			"label": "Selling Price After VAT",
			"fieldtype": "Float",
			"width": 100
		},

			
	]
	data = frappe.db.sql(
		"""
		SELECT
			`tabItem`.item_code,
			`tabItem`.item_name,
			`tabItem`.item_group,	
			talabat,
			dur_drn_item as drn_no,
			`tabItem`.brand,
			has_batch_no as has_batch,
			ib.barcode,
			ip.price_list_rate as selling_price_before_vat,
			itx.item_tax_template,	
			(ip.price_list_rate * (1 + (itd.tax_rate / 100))
			) as selling_price_after_vat
		FROM
			`tabItem`
		LEFT  JOIN `tabItem Barcode` as ib ON `tabItem`.name = ib.parent
		LEFT  JOIN `tabItem Tax` as itx ON `tabItem`.name = itx.parent
		LEFT JOIN `tabItem Price` as ip ON `tabItem`.name = ip.item_code AND ip.price_list = 'Standard Selling'
		LEFT JOIN `tabItem Tax Template Detail` as itd ON itx.item_tax_template = itd.parent
		WHERE
			`tabItem`.disabled = 0 AND `tabItem`.creation BETWEEN %(from_date)s AND %(to_date)s
		ORDER BY
			item_code
			""", values=filters, as_dict=True)
	return columns, data

