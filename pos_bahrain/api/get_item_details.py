# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
import json
from six import string_types


@frappe.whitelist()
def get_item_details(args):
    from erpnext.stock.get_item_details import get_item_details

    out = get_item_details(args)
    args_dict = (
        frappe._dict(json.loads(args)) if isinstance(args, string_types) else args
    )
    default_warehouse = (
        frappe.db.get_value("Company", args_dict.company, "default_warehouse")
        if args_dict.company
        else None
    )
    if default_warehouse and not out.warehouse:
        out.warehouse = default_warehouse
    return out
