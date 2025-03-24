frappe.ui.form.on('POS Invoice', {
    before_save: function(frm) { set_series(frm); },
    onload: function(frm) { set_series(frm); },
    pos_profile: function(frm) { set_series(frm); },
    is_pos: function(frm) { 
      setTimeout(() => { set_series(frm); }, 500); 
    }
  });
  
  function set_series(frm) {
    if (frm.doc.pos_profile && frm.doc.is_pos) {
      frappe.db.get_value('POS Profile', frm.doc.pos_profile, 'naming_series', (r) => {
        if (r && r.naming_series) {
          frm.set_value("naming_series", r.naming_series);
          frm.refresh_field("naming_series"); 
        }
      });
    }
  }