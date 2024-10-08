// Copyright (c) 2018, 	9t9it and contributors
// For license information, please see license.txt

frappe.ui.form.on('Opening Cash', {
	refresh: function(frm) {

	}
});

cur_frm.cscript.on_submit = function(doc) {
        frappe.set_route('pos');
}

