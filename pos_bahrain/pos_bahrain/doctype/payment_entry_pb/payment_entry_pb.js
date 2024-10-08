// Copyright (c) 2020, 	9t9it and contributors
// For license information, please see license.txt

{% include "erpnext/accounts/doctype/payment_entry/payment_entry.js" %}

frappe.provide("pos_bahrain.scripts.payment_entry_pb")

frappe.ui.form.handlers['Payment Entry PB'] =
  frappe.ui.form.handlers['Payment Entry'];

Object.entries(frappe.ui.form.handlers['Payment Entry PB']).forEach(
  ([field, events]) => {
    cur_frm.events[field] = events[events.length - 1];
  }
);

frappe.ui.form.on('Payment Entry PB', pos_bahrain.scripts.payment_entry_pb);
