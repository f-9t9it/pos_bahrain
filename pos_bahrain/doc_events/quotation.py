from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, today
from functools import partial
from toolz import first, compose, pluck, unique
from erpnext.stock.doctype.packed_item.packed_item import make_packing_list
from .sales_invoice import set_location

def validate(doc, method):
    custom_update_current_stock(doc)
    custom_after_save(doc, method)

def custom_update_current_stock(doc):
    if doc.get('packed_items'):
        for d in doc.get('packed_items'):
            bin = frappe.db.sql("SELECT actual_qty, projected_qty FROM `tabBin` WHERE item_code = %s AND warehouse = %s", 
                                (d.item_code, d.warehouse), as_dict=1)
            d.actual_qty = bin and flt(bin[0]['actual_qty']) or 0
            d.projected_qty = bin and flt(bin[0]['projected_qty']) or 0

            if not d.parent_item:
                linked_item = next((item.item_code for item in doc.items if item.item_code == d.item_code), None)
                d.parent_item = linked_item or doc.items[0].item_code

def custom_after_save(doc, method):
    if doc.is_new():
        make_packing_list(doc)
    else:
        for item in doc.get("items", []):
            if not any(d.parent_item == item.item_code for d in doc.get("packed_items", [])):
                make_packing_list(doc)