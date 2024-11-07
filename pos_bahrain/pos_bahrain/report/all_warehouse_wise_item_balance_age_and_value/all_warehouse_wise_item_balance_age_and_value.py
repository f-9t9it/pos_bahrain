from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt
from erpnext.stock.report.stock_balance.stock_balance import (
    get_item_details,
    get_item_warehouse_map,
    get_items,
    get_stock_ledger_entries,
)
from erpnext.stock.report.stock_ageing.stock_ageing import get_fifo_queue, get_average_age

def execute(filters=None):
    if not filters:
        filters = {}

    warehouse_list = get_warehouse_list(filters)
    columns = get_columns(filters)

    item_summary = {}

    for warehouse in warehouse_list:
        filters["warehouse"] = str(warehouse.name)
        validate_filters(filters)

        items = get_items(filters)
        sle = get_stock_ledger_entries(filters, items)

        item_map = get_item_details(items, sle, filters)
        iwb_map = get_item_warehouse_map(filters, sle)
        item_ageing = get_fifo_queue(filters)

        for (company, item, wh) in sorted(iwb_map):
            if item not in item_map:
                continue

            qty_dict = iwb_map[(company, item, wh)]
            item_group = item_map[item]["item_group"]
            total_stock_value = qty_dict.bal_val

            if item not in item_summary:
                item_summary[item] = {
                    "item_group": item_group,
                    "total_stock_value": 0.0,
                    "total_qty": 0,
                    "fifo_queue": [],
                    "warehouse_qty": {wh.name: 0 for wh in warehouse_list}
                }

            item_summary[item]["total_stock_value"] += total_stock_value
            item_summary[item]["total_qty"] += qty_dict.bal_qty
            item_summary[item]["warehouse_qty"][wh] += qty_dict.bal_qty

             
            if item in item_ageing and "fifo_queue" in item_ageing[item]:
                item_summary[item]["fifo_queue"].extend(item_ageing[item]["fifo_queue"])
         

    data = []
    for item, summary in item_summary.items():
        row = [
            item,
            summary["item_group"],
            summary["total_stock_value"],
            get_average_age(summary["fifo_queue"], filters.get("to_date", None)),
            summary["total_qty"]
        ] + [summary["warehouse_qty"].get(wh.name, 0) for wh in warehouse_list]

        data.append(row)

    add_warehouse_column(columns, warehouse_list)

    return columns, data


def get_columns(filters):
    columns = [
        _("Item") + ":Link/Item:180",
        _("Item Group") + "::100",
        _("Value") + ":Currency:100",
        _("Age") + ":Float:60",
    ]
    return columns

def get_warehouse_list(filters):
    from frappe.core.doctype.user_permission.user_permission import get_permitted_documents
    user_permitted_warehouse = get_permitted_documents('Warehouse')
    
    condition = ''
    value = {}

    if user_permitted_warehouse:
        condition = "AND name IN %(warehouses)s"
        value = {'warehouses': tuple(user_permitted_warehouse)}  
    elif filters.get("warehouse"):
        condition = "AND name IN %(warehouse)s"
        value = {'warehouse': filters["warehouse"]}

    return frappe.db.sql(
        """SELECT name FROM tabWarehouse WHERE is_group = 0 {condition}""".format(condition=condition), 
        value, as_dict=1
    )

def validate_filters(filters):
    if not (filters.get("item_code") or filters.get("warehouse")):
        sle_count = flt(frappe.db.sql("""SELECT COUNT(name) FROM `tabStock Ledger Entry`""")[0][0])
        if sle_count > 500000:
            frappe.throw(_("Please set filter based on Item or Warehouse"))
    if not filters.get("company"):
        filters["company"] = frappe.defaults.get_user_default("Company")

def add_warehouse_column(columns, warehouse_list):
    if len(warehouse_list) > 1:
        columns.append(_("Total Qty") + ":Int:50")
    
    for wh in warehouse_list:
        columns.append(_(wh.name) + ":Int:54")












 


