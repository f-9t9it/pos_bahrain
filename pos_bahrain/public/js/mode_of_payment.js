// Copyright (c) 2018, 	9t9it and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mode of Payment', {
  in_alt_currency: function(frm) {
    const { in_alt_currency } = frm.doc;
    if (!in_alt_currency) {
      frm.set_value('alt_currency', null);
    }
  },
});
