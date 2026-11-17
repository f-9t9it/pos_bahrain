# -*- coding: utf-8 -*-
# Copyright (c) 2019, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from pos_bahrain.api.item import get_conversion_factor


def before_save(doc, method):
    if doc.price_list_rate <= 0:
        frappe.throw(f"Price List Rate must be greater than 0 for Item {doc.item_code} in Price List {doc.price_list}")
    doc.pb_conversion_factor = get_conversion_factor(doc.item_code, doc.uom)
    if doc.customer and not doc.pb_customer_name:
        doc.pb_customer_name = frappe.db.get_value(
            "Customer", doc.customer, "customer_name"
        )
