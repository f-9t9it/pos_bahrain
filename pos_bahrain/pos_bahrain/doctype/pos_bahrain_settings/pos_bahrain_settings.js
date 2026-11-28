// Copyright (c) 2019, 	9t9it and contributors
// For license information, please see license.txt
frappe.provide("pos_bahrain.scripts.pos_bahrain_settings")

frappe.ui.form.on(
  'POS Bahrain Settings',
  pos_bahrain.scripts.pos_bahrain_settings
);

frappe.ui.form.on('POS Bahrain Settings', {
    setup(frm) {
        frm.set_query("pb_doctype", "pb_naming_series_settings", function() {
            return {
                filters: {
                    name: ["in", [
                        "Quotation",
                        "Sales Invoice",
                        "Sales Order",
                        "Purchase Invoice",
                        "Purchase Order",
                        "Purchase Receipt",
                        "Stock Entry",
                        "Material Request",
                        "Delivery Note"
                    ]]
                }
            };
        });
    },
	cancel_credit_note_jv(frm) {
	       frappe.call({
                      method:"pos_bahrain.events.jv_cancel.jv_cancel",
                    //   args: { 
                    //       name: d.parent,
                         
                    //   },
                      callback: function(r) {
                        // var pi = r.message
                        // frappe.db.set_value(cdt, cdn, "gl_payment", pi);
                        //   frm.reload_doc();
                      }
                      
          });
        }   
	
})

frappe.ui.form.on('PB Naming Series Settings', {

  pb_doctype: function(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    frappe.call({
      method: "pos_bahrain.api.pos_bahrain_settings.get_doctype_naming_series",
      args: {
        doctype: row.pb_doctype,
      },
      callback: function(r) {
        if (r.message) {
          frm.fields_dict['pb_naming_series_settings'].grid.update_docfield_property('pb_naming_series', 'options', r.message);
          frm.refresh_field("pb_naming_series_settings");
        }
      }
    });
  },

});