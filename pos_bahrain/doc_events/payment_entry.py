# -*- coding: utf-8 -*-
# Copyright (c) 2019, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import nowtime


def before_save(doc, method):
    if not doc.pb_posting_time:
        doc.pb_posting_time = nowtime()
    for ref in doc.references:
        if not ref.pb_invoice_date:
            date_field = (
                "transaction_date"
                if ref.reference_doctype == "Sales Order" or ref.reference_doctype == "Purchase Order" 
                else "posting_date"
            )
            ref.pb_invoice_date = frappe.db.get_value(
                ref.reference_doctype, ref.reference_name, date_field
            )
