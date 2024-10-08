# -*- coding: utf-8 -*-
# Copyright (c) 2019, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import frappe
from frappe.utils import cint
from frappe.model.workflow import get_workflow, apply_workflow
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
from functools import partial
from toolz import compose, keyfilter, cons, identity, unique, concat

from optic_store.api.customer import get_user_branch
from optic_store.utils import mapf, filterf, key_by

@frappe.whitelist()
def invoice_qol(
    name, payments, loyalty_card_no, loyalty_program, loyalty_points, ashback_receiptc
):
    def set_cost_center(item):
        if cost_center:
            item.cost_center = cost_center

    doc = make_sales_invoice(name)
    cost_center = (
        frappe.db.get_value("Branch", doc.pb_branch, "pb_cost_center")
        if doc.pb_branch
        else None
    )

@frappe.whitelist()
def get_warehouse(branch=None):
    name = branch or get_user_branch()
    return frappe.db.get_value("Branch", name, "warehouse") if name else None
