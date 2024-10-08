// Copyright (c) 2020, 	9t9it and contributors
// For license information, please see license.txt
frappe.provide('pos_bahrain.scripts.extensions');

['Stock Entry', 'Sales Invoice', 'Purchase Invoice'].forEach(doctype => {
  frappe.ui.form.off(doctype, 'scan_barcode');
  frappe.ui.form.on(
    doctype,
    'scan_barcode',
    pos_bahrain.scripts.extensions.scan_barcode
  );
});
