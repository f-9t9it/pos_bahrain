# -*- coding: utf-8 -*-
# Copyright (c) 2019, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.utils import cint
from frappe.model.document import Document
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
import frappe


class POSBahrainSettings(Document):
    def on_update(self):
        if(self.add_pos_profile_and_branch_to_payment_entry):
            make_property_setter("Payment Entry", "pb_pos_profile", "hidden", 0, "Check")
            make_property_setter("Payment Entry", "pb_branch", "hidden", 0, "Check")

        if(not self.add_pos_profile_and_branch_to_payment_entry):
            make_property_setter("Payment Entry", "pb_pos_profile", "hidden", 1, "Check")
            make_property_setter("Payment Entry", "pb_branch", "hidden", 1, "Check")

        if(self.enable_custom_item_description_fields):
            make_property_setter("Item", "pb_description", "hidden", 0, "Check")
            make_property_setter("Item", "description", "hidden", 1, "Check")

            make_property_setter("Purchase Invoice Item", "pb_description", "hidden", 0, "Check")
            make_property_setter("Purchase Invoice Item", "description", "default", "NA" , "Check")
            make_property_setter("Purchase Invoice Item", "description", "hidden", 1, "Check")

            make_property_setter("Purchase Order Item", "pb_description", "hidden", 0, "Check")
            make_property_setter("Purchase Order Item", "description", "default", "NA" , "Check")
            make_property_setter("Purchase Order Item", "description", "hidden", 1, "Check")

            make_property_setter("Purchase Receipt Item", "pb_description", "hidden", 0, "Check")
            make_property_setter("Purchase Receipt Item", "description", "default", "NA" , "Check")
            make_property_setter("Purchase Receipt Item", "description", "hidden", 1, "Check")

            make_property_setter("Quotation Item", "pb_description", "hidden", 0, "Check")
            make_property_setter("Quotation Item", "description", "default", "NA" , "Check")
            make_property_setter("Quotation Item", "description", "hidden", 1, "Check")

            make_property_setter("Sales Invoice Item", "pb_description", "hidden", 0, "Check")
            make_property_setter("Sales Invoice Item", "description", "default", "NA" , "Check")
            make_property_setter("Sales Invoice Item", "description", "hidden", 1, "Check")

            make_property_setter("Sales Order Item", "pb_description", "hidden", 0, "Check")
            make_property_setter("Sales Order Item", "description", "default", "NA" , "Check")
            make_property_setter("Sales Order Item", "description", "hidden", 1, "Check")

        if (not self.enable_custom_item_description_fields):
            make_property_setter("Item", "pb_description", "hidden", 1, "Check")
            make_property_setter("Item", "description", "hidden", 0, "Check")

            make_property_setter("Purchase Invoice Item", "pb_description", "hidden", 1, "Check")
            make_property_setter("Purchase Invoice Item", "description", "hidden", 0, "Check")
            make_property_setter("Purchase Invoice Item", "description", "default", "" , "Check")

            make_property_setter("Purchase Order Item", "pb_description", "hidden", 1, "Check")
            make_property_setter("Purchase Order Item", "description", "hidden", 0, "Check")
            make_property_setter("Purchase Order Item", "description", "default", "" , "Check")

            make_property_setter("Purchase Receipt Item", "pb_description", "hidden", 1, "Check")
            make_property_setter("Purchase Receipt Item", "description", "hidden", 0, "Check")
            make_property_setter("Purchase Receipt Item", "description", "default", "" , "Check")
            
            make_property_setter("Quotation Item", "pb_description", "hidden", 1, "Check")
            make_property_setter("Quotation Item", "description", "hidden", 0, "Check")
            make_property_setter("Quotation Item", "description", "default", "" , "Check")

            make_property_setter("Sales Invoice Item", "pb_description", "hidden", 1, "Check")
            make_property_setter("Sales Invoice Item", "description", "hidden", 0, "Check")
            make_property_setter("Sales Invoice Item", "description", "default", "" , "Check")

            make_property_setter("Sales Order Item", "pb_description", "hidden", 1, "Check")
            make_property_setter("Sales Order Item", "description", "hidden", 0, "Check")
            make_property_setter("Sales Order Item", "description", "default", "" , "Check")

        if(self.enable_custom_customer_contact_details):
            make_property_setter("Customer", "pb_contact_person", "hidden", 0, "Check")
            make_property_setter("Customer", "pb_mobile_number", "hidden", 0, "Check")
            make_property_setter("Customer", "pb_email_address", "hidden", 0, "Check")
            make_property_setter("Customer", "pb_address", "hidden", 0, "Check")
            make_property_setter("Customer", "pb_city", "hidden", 0, "Check")
            make_property_setter("Customer", "pb_country", "hidden", 0, "Check")

        if(not self.enable_custom_customer_contact_details):
            make_property_setter("Customer", "pb_contact_person", "hidden", 1, "Check")
            make_property_setter("Customer", "pb_mobile_number", "hidden", 1, "Check")
            make_property_setter("Customer", "pb_email_address", "hidden", 1, "Check")
            make_property_setter("Customer", "pb_address", "hidden", 1, "Check")
            make_property_setter("Customer", "pb_city", "hidden", 1, "Check")
            make_property_setter("Customer", "pb_country", "hidden", 1, "Check")

        hide_batch_price = not cint(self.use_batch_price)
        make_property_setter(
            "Batch", "pb_price_sec", "hidden", hide_batch_price, "Check"
        )
        make_property_setter(
            "Batch", "pb_price_sec", "print_hide", hide_batch_price, "Check"
        )

        hide_barcode_uom = not cint(self.use_barcode_uom)
        make_property_setter(
            "Item Barcode", "pb_uom", "hidden", hide_barcode_uom, "Check"
        )

        hide_sales_employee = not cint(self.show_sales_employee)
        make_property_setter(
            "Sales Invoice",
            "pb_sales_employee",
            "reqd" if hide_sales_employee else "hidden",
            False,
            "Check",
        )
        make_property_setter(
            "Sales Invoice",
            "pb_sales_employee",
            "hidden" if hide_sales_employee else "reqd",
            True,
            "Check",
        )
