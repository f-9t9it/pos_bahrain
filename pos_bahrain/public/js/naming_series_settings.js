async function set_series(frm){
    frappe.db.get_single_value("POS Bahrain Settings", "enable_naming_series_settings").then(async (enable_naming_series_settings) => {
    if(enable_naming_series_settings == 1){
    var naming_series = '';
    await frappe.call({
        method: "pos_bahrain.api.pos_bahrain_settings.get_naming_series_settings",
        args: {
            doctype: frm.doc.doctype,
            pos_profile: frm.doc.doctype == "Sales Invoice" ? frm.doc.pos_profile : null,
            company: frm.doc.company
        },
        callback: function (r) {
            if (r.message && r.message.length > 0) {
                var naming_series_settings = r.message[0];
                if (frm.is_new() && frm.doc.company) {
                if (naming_series_settings.company == frm.doc.company) {
                    naming_series = naming_series_settings.pb_naming_series;
                    
                }
            }
            }
        }
    })
    frm.set_value("naming_series", naming_series);
    frm.refresh_field("naming_series");
}
});
}



frappe.ui.form.on(cur_frm.doc.doctype,  
    { company: function(frm) {
    setTimeout(() => { set_series(frm); }, 500); 
    },
    pos_profile: function(frm) {
    setTimeout(() => { set_series(frm); }, 500); 
    },
    onload_post_render: function(frm){
    setTimeout(() => { set_series(frm); }, 500); 
    },
})


