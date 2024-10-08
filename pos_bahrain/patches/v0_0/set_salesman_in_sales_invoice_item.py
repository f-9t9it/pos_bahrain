# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from toolz import pluck


def execute():
    if (
        frappe.db.has_column("Item", "salesman")
        and frappe.db.has_column("Sales Invoice Item", "salesman")
        and frappe.db.has_column("Sales Invoice Item", "salesman_name")
    ):
        for name in pluck("name", frappe.get_all("Sales Invoice Item")):
            item = frappe.get_doc("Sales Invoice Item", name)
            if not item.salesman:
                salesman = frappe.db.get_value("Item", item.item_code, "salesman")
                if salesman:
                    frappe.db.set_value(
                        "Sales Invoice Item", name, "salesman", salesman
                    )
                    frappe.db.set_value(
                        "Sales Invoice Item",
                        name,
                        "salesman_name",
                        frappe.db.get_value("User", salesman, "full_name"),
                    )
        frappe.db.commit()
