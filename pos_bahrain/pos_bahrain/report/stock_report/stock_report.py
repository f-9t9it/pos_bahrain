# Copyright (c) 2024, 	9t9it and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	data = []
	columns = [
		{
			"fieldname":"item",
			"label":"Item Column",
			"fieldtype":"Link",
			"options":"Item"
		},
		{
			"fieldname":"warehouse",
			"label":"Warehouse Column",
			"fieldtype":"Link",
			"options":"Warehouse"
		}
	]
	custom_filters = {}
	if filters.item_code != None:
		custom_filters["item_code"] = filters.item_code
	if filters.warehouse != None:
		custom_filters["warehouse"] = filters.warehouse
	stock_ledger = frappe.db.get_list("Stock Ledger Entry", filters = custom_filters,  fields= ["*"])
	for stock in stock_ledger:
		data.append({
			"item":stock.item_code,
			"warehouse": stock.warehouse
		})
	# frappe.throw(f"{stock_ledger}")
	return columns, data
