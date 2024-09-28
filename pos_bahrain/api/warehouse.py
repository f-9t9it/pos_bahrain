from __future__ import unicode_literals
import frappe
import json
from collections import defaultdict
from frappe.utils import cint, flt


@frappe.whitelist()
def get_warehouse_list():
    warehouse_list = frappe.db.sql("""SELECT name as warehouse_code,warehouse_name From `tabWarehouse` """, as_dict = 1)
    return warehouse_list


@frappe.whitelist()
def add_node():
	from frappe.desk.treeview import make_tree_args

	args = make_tree_args(**frappe.form_dict)

	if cint(args.is_root):
		args.parent_warehouse = None

	frappe.get_doc(args).insert()


@frappe.whitelist()
def get_children(doctype, parent=None, company=None, is_root=False):
	if is_root:
		parent = ""

	fields = ["name as value", "is_group as expandable"]
	filters = [
		["docstatus", "<", "2"],
		['ifnull(`parent_warehouse`, "")', "=", parent],
		["company", "in", (company, None, "")],
	]

	warehouses = frappe.get_list(doctype, fields=fields, filters=filters, order_by="name")

	company_currency = ""
	if company:
		company_currency = frappe.get_cached_value("Company", company, "default_currency")

	warehouse_wise_value = get_warehouse_wise_stock_value(company)

	# return warehouses
	for wh in warehouses:
		wh["balance"] = warehouse_wise_value.get(wh.value)
		if company_currency:
			wh["company_currency"] = company_currency
	return warehouses


def get_warehouse_wise_stock_value(company):
	warehouses = frappe.get_all(
		"Warehouse", fields=["name", "parent_warehouse"], filters={"company": company}
	)
	parent_warehouse = {d.name: d.parent_warehouse for d in warehouses}

	filters = {"warehouse": ("in", [data.name for data in warehouses])}
	bin_data = frappe.get_all(
		"Bin",
		fields=["sum(stock_value) as stock_value", "warehouse"],
		filters=filters,
		group_by="warehouse",
	)

	warehouse_wise_stock_value = defaultdict(float)
	for row in bin_data:
		if not row.stock_value:
			continue

		warehouse_wise_stock_value[row.warehouse] = row.stock_value
		update_value_in_parent_warehouse(
			warehouse_wise_stock_value, parent_warehouse, row.warehouse, row.stock_value
		)

	return warehouse_wise_stock_value


def update_value_in_parent_warehouse(
	warehouse_wise_stock_value, parent_warehouse_dict, warehouse, stock_value
):
	parent_warehouse = parent_warehouse_dict.get(warehouse)
	if not parent_warehouse:
		return

	warehouse_wise_stock_value[parent_warehouse] += flt(stock_value)
	update_value_in_parent_warehouse(
		warehouse_wise_stock_value, parent_warehouse_dict, parent_warehouse, stock_value
	)

