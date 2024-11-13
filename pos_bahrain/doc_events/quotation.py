from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, today
from functools import partial
from toolz import first, compose, pluck, unique
from .sales_invoice import set_location

def validate(doc, method):
    custom_update_current_stock(doc)
    custom_after_save(doc, method)

def custom_update_current_stock(doc):
    for d in doc.get('packed_items'):
        bin = frappe.db.sql("SELECT actual_qty, projected_qty FROM `tabBin` WHERE item_code = %s AND warehouse = %s", 
                             (d.item_code, d.warehouse), as_dict=1)
        d.actual_qty = bin and flt(bin[0]['actual_qty']) or 0
        d.projected_qty = bin and flt(bin[0]['projected_qty']) or 0

        if not d.parent_item:
            if doc.items:

                d.parent_item = doc.items[0].item_code 

def custom_after_save(doc, method):
    if doc.is_new():
        from erpnext.stock.doctype.packed_item.packed_item import make_packing_list
        make_packing_list(doc)
    else:
        pass


    
