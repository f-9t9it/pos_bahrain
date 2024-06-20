from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, date_diff
from erpnext.stock.report.stock_balance.stock_balance import (get_item_details,
    get_item_reorder_details, get_item_warehouse_map, get_items, get_stock_ledger_entries)
from erpnext.stock.report.stock_ageing.stock_ageing import get_fifo_queue, get_average_age
from pos_bahrain.pos_bahrain.report.branch_stock_and_value.branch_stock_and_value import get_warehouse_list
from pos_bahrain.pos_bahrain.report.branch_stock_and_value.branch_stock_and_value import validate_filters
from pos_bahrain.pos_bahrain.report.branch_stock_and_value.branch_stock_and_value import add_warehouse_column
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
        item_balance = {}
        item_value = {}

        for (company, item, warehouse) in sorted(iwb_map):
            if not item_map.get(item): continue

            row = []
            qty_dict = iwb_map[(company, item, warehouse)]
            item_balance.setdefault((item, item_map[item]["item_group"]), [])
            total_stock_value = 0.00
            for wh in warehouse_list:
                row += [flt(qty_dict.bal_qty, precision=1)] if wh.name == warehouse else [flt(0.00, precision=1)]
                total_stock_value += flt(qty_dict.bal_val, precision=1) if wh.name == warehouse else flt(0.00, precision=1)

            item_balance[(item, item_map[item]["item_group"])].append(row)
            item_value.setdefault((item, item_map[item]["item_group"]), [])
            item_value[(item, item_map[item]["item_group"])].append(total_stock_value)

        for (item, item_group), wh_balance in iteritems(item_balance):
            if not item_ageing.get(item): continue

            total_stock_value = sum(item_value[(item, item_group)])
            row = [item, item_group, total_stock_value]

            latest_age, earliest_age, average_age = get_purchase_ages(item, filters)
            row += [flt(average_age, precision=1), flt(earliest_age, precision=1), flt(latest_age, precision=1)]

            bal_qty = [sum(bal_qty) for bal_qty in zip(*wh_balance)]
            total_qty = sum(bal_qty)
            if len(warehouse_list) > 1:
                row += [total_qty]
                if total_qty > 0:
                    valuation_rate = total_stock_value / total_qty
                    row += [flt(valuation_rate, precision=1)]

            row += [flt(qty, precision=1) for qty in bal_qty]

            if total_qty > 0:
                data.append(row)
            elif not filters.get("filter_total_zero_qty"):
                data.append(row)

        add_warehouse_column(columns, warehouse_list)

    return columns, data

def get_columns(filters):
    """return columns"""

    columns = [
        _("Item") + ":Link/Item:180",
        _("Item Group") + "::100",
        _("Value") + ":Currency:100",
        _("Average Age") + ":Data:100",
        _("Earliest Age") + ":Data:100",
        _("Latest Age") + ":Data:100",
        # _("Age") + ":Data:100",
    ]
    return columns

def get_purchase_ages(item, filters):
    frappe.log_error(item, title="item")
    frappe.log_error(filters, title="filters")

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
