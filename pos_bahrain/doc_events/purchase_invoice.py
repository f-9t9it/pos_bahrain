# -*- coding: utf-8 -*-
# Copyright (c) 2019, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe 

from pos_bahrain.doc_events.purchase_receipt import set_or_create_batch
from pos_bahrain.doc_events.sales_invoice import set_cost_center


def before_validate(doc, method):
    set_or_create_batch(doc, method)


def before_save(doc, method):
    set_cost_center(doc)
    
def check_invoice_no(doc, method):
    if frappe.db.exists("Purchase Invoice", {"bill_no":doc.bill_no, "supplier":doc.supplier, "docstatus":['!=', 2]}):
        frappe.throw(f"Cannot make Supplier Invoice No:{doc.bill_no} unique cause other supplier may have same invoice numbers")
