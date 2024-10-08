# -*- coding: utf-8 -*-
# Copyright (c) 2019, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def boot_session(bootinfo):
    bootinfo.pos_bahrain = frappe._dict()
    settings = frappe.get_single("POS Bahrain Settings")
    bootinfo.pos_bahrain.use_batch_price = settings.use_batch_price
    bootinfo.pos_bahrain.use_barcode_uom = settings.use_barcode_uom
    bootinfo.pos_bahrain.disable_standard_pf = settings.disable_standard_pf
