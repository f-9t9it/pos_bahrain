# -*- coding: utf-8 -*-
# Copyright (c) 2019, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from pos_bahrain.doc_events.purchase_receipt import set_or_create_batch


def before_validate(doc, method):
    if doc.purpose == "Material Receipt":
        set_or_create_batch(doc, method)


def on_submit(doc, method):
    if doc.pb_repack_request:
        frappe.db.set_value("Repack Request", doc.pb_repack_request, "status", "Completed")
