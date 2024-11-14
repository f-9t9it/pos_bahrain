frappe.ui.form.on('Quotation', {
  refresh: function (frm) {
    get_employee(frm);
    _create_custom_buttons(frm);
    // query_override(frm);
  },
  quotation_to: function(frm) {
    query_override(frm);
  }
});

frappe.ui.form.on('Quotation Item', {
  item_code: function (frm, cdt, cdn) {
      get_total_stock_qty(frm, cdt, cdn)
  },
});

function get_employee(frm) {
  if (!frm.doc.pb_sales_employee && frm.doc.__islocal) {
    frappe.call({
      method: "pos_bahrain.api.sales_invoice.get_logged_employee_id",
      callback: function (r) {
        if (r.message != 0) {
          frm.set_value("pb_sales_employee", r.message)
        }
      }
    })
  }
}
frappe.ui.form.on("Quotation", {
	refresh:function(frm){
    if (frm.doc.status =="Ordered" && frm.doc.status !== 'Lost') {
		cur_frm.custom_buttons["Sales Order"].hide()
    }
	},
	
})

function _create_custom_buttons(frm) {
  if (frm.doc.docstatus === 1 && frm.doc.status !== 'Lost') {
    if (
      !frm.doc.valid_till ||
      frappe.datetime.get_diff(
        frm.doc.valid_till,
        frappe.datetime.get_today()
      ) >= 0
    ) {
      frappe.call({
        method: 'frappe.client.get_value',
        args: {
          doctype: 'POS Bahrain Settings',
          filters: { name: frm.doc.pos_bahrain_settings },
          fieldname: 'show_custom_button',
        },
        callback: function (r) {
          console.log(r.message.show_custom_button)
          if (r.message.show_custom_button == 1) {
            frm.add_custom_button(
              __('Sales Invoice'),
              () => _make_sales_invoice(frm),
              __('Create')
            );
          }
        },
      });
    }
  }
}

function _make_sales_invoice(frm) {
  frappe.model.open_mapped_doc({
    method: 'pos_bahrain.api.quotation.make_sales_invoice',
    frm,
  });
}

// function query_override(frm){
//   if(cur_frm.doc.quotation_to == "Customer"){
//       frm.set_query("party_name", function(){
//       return {
//         query: "pos_bahrain.api.quotation.link_query_override",
//       };
//       });
//   }
// }

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
  })
}

frappe.ui.form.on('Packed Item', {
  packed_items_add(frm, cdt, cdn) {
    const fields = ["parent_item","item_code", "item_name", "qty"];
    const new_row = locals[cdt][cdn];
    frm.new_packed_item = new_row; // Store the newly added row in frm.new_packed_item

    fields.forEach(function(field) {
      const field_doc = frm.fields_dict['packed_items'].grid.get_docfield(field);
      field_doc.read_only = 0; 
      field_doc.hidden = 0;  
    });

    frm.refresh_field('packed_items');  
  },
});

frappe.ui.form.on('Quotation', {
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
  },
});