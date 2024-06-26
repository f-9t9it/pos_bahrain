# Copyright (c) 2013, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, date_diff
from frappe.utils import flt, cint, getdate
from erpnext.stock.report.stock_balance.stock_balance import (get_item_details,
	get_item_reorder_details, get_item_warehouse_map, get_items, get_stock_ledger_entries)
from erpnext.stock.report.stock_ageing.stock_ageing import get_fifo_queue, get_average_age
from six import iteritems

def execute(filters=None):
	if not filters: filters = {}

	validate_filters(filters)
	companies = frappe.get_all("Company")

	columns = None
	data = []

	for comp in companies:
		filters["company"] = comp.name

		columns = get_columns(filters)

		items = get_items(filters)
		sle = get_stock_ledger_entries(filters, items)

		item_map = get_item_details(items, sle, filters)
		iwb_map = get_item_warehouse_map(filters, sle)
		warehouse_list = get_warehouse_list(filters)
		item_ageing = get_fifo_queue(filters)
		#data = []
		item_balance = {}
		item_value = {}

		for (company, item, warehouse) in sorted(iwb_map):
			if not item_map.get(item):  continue

			row = []
			qty_dict = iwb_map[(company, item, warehouse)]
			item_balance.setdefault((item, item_map[item]["item_group"]), [])
			total_stock_value = 0.00
			for wh in warehouse_list:
				row += [qty_dict.bal_qty] if wh.name == warehouse else [0.00]
				total_stock_value += qty_dict.bal_val if wh.name == warehouse else 0.00

			item_balance[(item, item_map[item]["item_group"])].append(row)
			item_value.setdefault((item, item_map[item]["item_group"]),[])
			item_value[(item, item_map[item]["item_group"])].append(total_stock_value)


		# sum bal_qty by item
		for (item, item_group), wh_balance in iteritems(item_balance):
			if not item_ageing.get(item):  continue

			total_stock_value = sum(item_value[(item, item_group)])
			row = [item, item_group, total_stock_value]

			fifo_queue = item_ageing[item]["fifo_queue"]
			
			latest_age, earliest_age, average_age = get_purchase_ages(item, filters)
			row += [average_age,earliest_age, latest_age]
			
			bal_qty = [sum(bal_qty) for bal_qty in zip(*wh_balance)]
			total_qty = sum(bal_qty)
			# Valuation_rate = total_stock_value/total_qty
			if len(warehouse_list) > 1:
				row += [total_qty]
				if total_qty > 0:
					Valuation_rate = total_stock_value/total_qty
					row +=[Valuation_rate]	
				
			row += bal_qty
			
			if total_qty > 0:
				data.append(row)
				
			elif not filters.get("filter_total_zero_qty"):
				data.append(row)

		add_warehouse_column(columns, warehouse_list)
		
	return columns, data

def get_columns(filters):
	"""return columns"""

	columns = [
		_("Item")+":Link/Item:180",
		_("Item Group")+"::100",
		_("Value")+":Currency:100",
        _("Average Age") + ":Data:100",
        _("Earliest Age") + ":Data:100",
        _("Latest Age") + ":Data:100",
		# _("Age")+":Float:60",
		# _("Valuation Rate")+":Float:60",
	]
	return columns

def validate_filters(filters):
	if not (filters.get("item_code") or filters.get("warehouse")):
		sle_count = flt(frappe.db.sql("""select count(name) from `tabStock Ledger Entry`""")[0][0])
		if sle_count > 500000:
			frappe.throw(_("Please set filter based on Item or Warehouse"))

def get_warehouse_list(filters):
	from frappe.core.doctype.user_permission.user_permission import get_permitted_documents

	condition = ''
	user_permitted_warehouse = get_permitted_documents('Warehouse')
	value = ()
	if user_permitted_warehouse:
		condition = "and name in %s"
		value = set(user_permitted_warehouse)
	elif not user_permitted_warehouse and filters.get("warehouse"):
		condition = "and name = %s"
		value = filters.get("warehouse")

	return frappe.db.sql("""select name
		from `tabWarehouse` where is_group = 0
		{condition}""".format(condition=condition), value, as_dict=1)

def add_warehouse_column(columns, warehouse_list):
	if len(warehouse_list) > 1:
		columns += [_("Total Qty")+":Int:80"]
		columns += [_("Valuation Rate")+":Currency:120"]

	for wh in warehouse_list:
		columns += [_(wh.name)+":Int:100"]


def get_purchase_ages(item, filters):
    # Fetch purchase entries from Stock Ledger Entry
    sle = frappe.db.sql("""
        SELECT posting_date
        FROM `tabStock Ledger Entry` sle
        WHERE item_code = %s AND company = %s 
        AND (
            voucher_type IN ('Purchase Invoice', 'Purchase Receipt') 
            OR (
                voucher_type = 'Stock Entry' 
                AND EXISTS (
                    SELECT 1 
                    FROM `tabStock Entry` se 
                    WHERE se.name = sle.voucher_no 
                    AND se.stock_entry_type = 'Material Receipt'
                )
            )
        )
        ORDER BY posting_date ASC
    """, (item, filters["company"]), as_dict=True)

    if not sle:
        return 0.00, 0.00, 0.00

    earliest_entry = sle[0].posting_date
    latest_entry = sle[-1].posting_date

    to_date = getdate(filters["to_date"])
    earliest_age = date_diff(to_date, earliest_entry)
    latest_age = date_diff(to_date, latest_entry)

    total_days = sum([date_diff(to_date, entry.posting_date) for entry in sle])
    average_purchase_age = total_days / len(sle) if sle else 0.00

    return latest_age, earliest_age, average_purchase_age
