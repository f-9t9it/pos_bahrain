frappe.ui.form.on('Sales Order Item', {
  item_code: function (frm, cdt, cdn) {
      get_total_stock_qty(frm, cdt, cdn)
  },
});

function get_total_stock_qty(frm, cdt, cdn) {
  var d = locals[cdt][cdn];

  if (d.item_code === undefined) {
      return;
  }
  frappe.call({
      method: "pos_bahrain.api.stock.get_total_stock_qty",
      args: {
          item_code: d.item_code
      },
      callback: function (r) {
          frappe.model.set_value(cdt, cdn, "total_available_qty", r.message);
      }
  });
}

frappe.ui.form.on("Sales Order", {
  refresh: function(frm) {
      setTimeout(function() {
          frm.remove_custom_button('Sales Invoice', 'Create');
      }, 500);


      frm.add_custom_button(__('Sales Invoice '), function() {
          frm.trigger('custom_make_sales_invoice');
      }, __("Create"));
  },

  custom_make_sales_invoice: function(frm) {
      frappe.model.open_mapped_doc({
          method: "pos_bahrain.api.sales_order.make_sales_invoice",
          frm: frm
      });
  },

  onload: function(frm) {
      frm.set_df_property("packed_items", "read_only", 0); 
  }
});

frappe.ui.form.on('Packed Item', {
  packed_items_add(frm, cdt, cdn) {
      const fields = ["parent_item", "item_code", "item_name", "qty"];
      const new_row = locals[cdt][cdn];
      frm.new_packed_item = new_row; 

      fields.forEach(function(field) {
          const field_doc = frm.fields_dict['packed_items'].grid.get_docfield(field);
          field_doc.read_only = 0; 
          field_doc.hidden = 0;  
      });

      frm.refresh_field('packed_items');  
  }
});

frappe.ui.form.on('Sales Order', {
  validate(frm) {
      if (frm.new_packed_item) {
          const new_packed_item = frm.new_packed_item;
          let exists = false;

          frm.doc.packed_items.forEach(item => {
              if (item.item_code === new_packed_item.item_code) {
                  exists = true;
              }
          });

          if (!exists) {
              let new_row = frm.add_child('packed_items', {
                  parent_item: new_packed_item.parent_item,
                  item_code: new_packed_item.item_code,
                  item_name: new_packed_item.item_name,
                  qty: new_packed_item.qty
              });

              new_row.item_name = new_packed_item.item_name; 
              new_row.qty = new_packed_item.qty; 

              frm.refresh_field('packed_items'); 
          }

          frm.new_packed_item = null; 
      }
  }
});