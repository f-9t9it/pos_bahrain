# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe


def execute():
    _set_missing_conversion_factor()
    _set_missing_customer_name()


def _set_missing_conversion_factor():
    if not frappe.db.exists("Custom Field", "Item Price-pb_conversion_factor"):
        frappe.get_doc(
            {
                "doctype": "Custom Field",
                "dt": "Item Price",
                "fieldname": "pb_conversion_factor",
                "fieldtype": "Float",
                "insert_after": "item_name",
                "label": "UOM Conversion Factor",
                "read_only": 1,
            }
        ).insert()

    docs = frappe.db.sql(
        """
            SELECT name, item_code, uom FROM `tabItem Price`
            WHERE IFNULL(uom, '') != '' AND IFNULL(pb_conversion_factor, 0) = 0
        """,
        as_dict=1,
    )
    for doc in docs:
        value = frappe.db.get_value(
            "UOM Conversion Detail",
            filters={"parent": doc.get("item_code"), "uom": doc.get("uom")},
            fieldname="conversion_factor",
        )
        if value:
            frappe.db.set_value(
                "Item Price", doc.get("name"), "pb_conversion_factor", value
            )


def _set_missing_customer_name():
    if not frappe.db.exists("Custom Field", "Item Price-pb_customer_name"):
        frappe.get_doc(
            {
                "doctype": "Custom Field",
                "dt": "Item Price",
                "fieldname": "pb_customer_name",
                "fieldtype": "Data",
                "insert_after": "customer",
                "label": "Customer Name",
                "fetch_from": "customer.customer_name",
                "translatable": 0,
                "read_only": 1,
            }
        ).insert()

    docs = frappe.db.sql(
        """
            SELECT name, customer FROM `tabItem Price`
            WHERE IFNULL(customer, '') != '' AND IFNULL(pb_customer_name, '') = ''
        """,
        as_dict=1,
    )
    for doc in docs:
        value = frappe.db.get_value("Customer", doc.get("customer"), "customer_name")
        if value:
            frappe.db.set_value(
                "Item Price", doc.get("name"), "pb_customer_name", value
            )
