frappe.ui.form.on("POS Profile", "onload", function(frm) {
	frm.call({
		method: "pos_bahrain.doc_events.pos_profile.get_series",
		callback: function(r) {
			if(!r.exc) {
				set_field_options("naming_series", r.message);
			}
		}
	});
});