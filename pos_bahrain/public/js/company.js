// Copyright (c) 2018, 	9t9it and contributors
// For license information, please see license.txt

frappe.ui.form.on('Company', {
  setup: function(frm) {
    frm.set_query('default_warehouse', { company: frm.doc.name });
  },
});
