frappe.ui.form.on('Material Request', {
  setup: function (frm) {
   
   

    frm.set_query('pb_to_warehouse', function () {
      return {
        filters: {
          company: frm.doc.company,
          is_group: 0,
        },
      };
    });
  },
  refresh: function (frm) {
    let item_exists = false;

    frappe.call({
      "method":"pos_bahrain.doc_events.material_request.check_material_request_repack_items",
      "args": {"items": frm.doc.items},
      "callback": (r)=>{
        console.log(r.message)
        item_exists = r.message
         // add button to create stock entry when type is Repack
     if (frm.doc.docstatus == 1 && frm.doc.material_request_type == "Repack" && frm.doc.status != "Transferred" && frm.doc.status != "Received" && item_exists == false)
      {
       
        frm.add_custom_button(__("Create Stock Entry"), function() {
          frappe.run_serially([
         ()=>{
          var stock_entry = frappe.model.get_new_doc('Stock Entry');
		      stock_entry.stock_entry_type = frm.doc.material_request_type
          stock_entry.company = frm.doc.company
          frm.doc.items.forEach(function(item) {
          var st_item = frappe.model.add_child(stock_entry, "Item", "items", item.idx);
          st_item.item_code = item.item_code;
          st_item.item_name = item.item_name;
           st_item.item_group=item.item_group;
           st_item.set_basic_rate_manually = 1
           st_item.qty= item.qty;
           st_item.transfer_qty = item.qty
           st_item.basic_rate= item.rate;
           st_item.description = item.description;
           st_item.uom= item.uom;
           st_item.stock_uom = item.stock_uom;
           st_item.conversion_factor = item.conversion_factor;
           st_item.t_warehouse=item.warehouse;
           st_item.actual_qty = item.actual_qty
           st_item.cost_center = item.cost_center;
           st_item.transferred_qty = item.qty;
           st_item.material_request= frm.doc.name
           st_item.material_request_item = item.name
          })
		      frappe.set_route('Form',"Stock Entry",stock_entry.name);
          
            setTimeout(function(){cur_frm.call("get_stock_and_rate")}, 1000)
          
          
          
         } 
          ])
         }).css({"color":"white", "background-color": "#5E64FF", "font-weight": "800"});


         
      }
      }
    })
    
    

    _make_custom_buttons(frm);
  },
  pb_to_warehouse: function (frm) {
    _set_items_warehouse(frm);
  },
});

function _make_custom_buttons(frm) {
  if (frm.doc.docstatus !== 1) {
    return;
  }
  if (
    frm.doc.material_request_type === 'Material Transfer' &&
    frm.doc.status !== 'Transferred' &&
    frappe.user.has_role('Stock Manager')
  ) {
    frm.add_custom_button(__('Stock Transfer'), () =>
      _make_stock_transfer(frm)
    );
  }
}

function _make_stock_transfer(frm) {
  frappe.model.open_mapped_doc({
    method: 'pos_bahrain.api.material_request.make_stock_entry',
    frm: frm,
  });
}

function _set_items_warehouse(frm) {
  for (const item of frm.doc.items) {
    frappe.model.set_value(
      item.doctype,
      item.name,
      'warehouse',
      frm.doc.pb_to_warehouse
    );
  }
}

