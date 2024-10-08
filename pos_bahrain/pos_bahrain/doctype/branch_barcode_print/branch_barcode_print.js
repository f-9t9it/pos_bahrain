// Copyright (c) 2021, 	9t9it and contributors
// For license information, please see license.txt

frappe.provide('pos_bahrain.scripts')


frappe.ui.form.on('Branch Barcode Print', pos_bahrain.scripts.barcode_print);
frappe.ui.form.on( 'Barcode Print Item', pos_bahrain.scripts.barcode_print_item );
