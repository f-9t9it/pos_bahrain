// Copyright (c) 2018, 	9t9it and contributors
// For license information, please see license.txt

function updateTotalQty(frm)
{
  let totalQty = 0;
  (frm.doc.items || []).forEach((row)=>{
    totalQty += flt(row.qty)
  })
  frm.set_value("custom_total_qty", totalQty);
}

function setDifferenceAccount(frm, cdt, cdn) {
  setTimeout(() => {
  const row = frappe.get_doc(cdt, cdn);
  row.expense_account = frm.doc.custom_difference_acount;
  frm.refresh_field("items");
}, 1000);
}

frappe.ui.form.off('Stock Entry Detail', 'item_code');
frappe.ui.form.on('Stock Entry Detail', {
  item_code: function(frm, cdt, cdn){
    stock_entry_item_code(frm, cdt, cdn)
    setDifferenceAccount(frm, cdt, cdn);
  },
  s_warehouse: function (frm, cdt, cdn) {
    _set_cost_center('s_warehouse', cdt, cdn);
  },
  t_warehouse: function (frm, cdt, cdn) {
    _set_cost_center('t_warehouse', cdt, cdn);
  },
  qty: function(frm, cdt, cdn) {
    updateTotalQty(frm);
  },
  items_add: function(frm, cdt, cdn)
  {
    setDifferenceAccount(frm, cdt, cdn)
  }
});


frappe.ui.form.on('Stock Entry', {
  refresh: function (frm) {
    _set_repack_warehouses_read_only(frm);
     frm.set_query('custom_difference_acount', function() {
      return {
        filters: {
          company: frm.doc.company,
          is_group: 0
        }
      };
    });
  },
  before_save: function(frm)
  {
    updateTotalQty(frm);
  },
  custom_difference_acount(frm) {
    if (frm.doc.custom_difference_acount) {
        (frm.doc.items || []).forEach(row => {
            row.expense_account = frm.doc.custom_difference_acount;
        });

          frm.refresh_field("items");
      }
     
  }
});


function _set_cost_center(fieldname, cdt, cdn) {
  const data = locals[cdt][cdn];
  _get_cost_center(data[fieldname]).then((cost_center) => {
    if (cost_center) {
      frappe.model.set_value(cdt, cdn, 'cost_center', cost_center);
    }
  });
}


async function _get_cost_center(warehouse) {
  const { message: data } = await frappe.db.get_value('Warehouse', warehouse, 'pb_cost_center');
  return data.pb_cost_center ? data.pb_cost_center : null;
}


function _set_repack_warehouses_read_only(frm) {
  if (frm.doc.pb_repack_request) {
    frm.fields_dict["items"].grid.toggle_enable("s_warehouse", 0);
    frm.fields_dict["items"].grid.toggle_enable("t_warehouse", 0);
  }
}

// frappe.ui.form.on('Stock Entry', {
// 	setup: function(frm) {
//     frappe.db.get_single_value('POS Bahrain Settings', 'disable_serial_no_and_batch_selector')
// 		.then((value) => {
// 			if (value) {
// 				frappe.flags.hide_serial_batch_dialog = true;
// 			}
// 		});
//   },
// }) 

function stock_entry_item_code(frm, cdt, cdn)
{
  const d = frappe.get_doc(cdt, cdn);
  if (d.item_code) {
    // exists=frappe.db.get_single_value('POS Bahrain Settings', 'disable_serial_no_and_batch_selector')
    // if (!exists){
    const { company, doctype: voucher_type } = frm.doc;
    const {
      item_code,
      s_warehouse,
      t_warehouse,
      transfer_qty,
      serial_no,
      bom_no,
      expense_account,
      cost_center,
      qty,
      name: voucher_no,
    } = d;
    frappe.call({
      doc: frm.doc,
      method: 'get_item_details',
      callback: function(r) {
        if (r.message) {
          Object.keys(r.message).forEach(k => {
            if (r.message[k]) {
              d[k] = r.message[k];
            }
          });
          frm.refresh_field('items');
          return frappe.db.get_single_value('POS Bahrain Settings', 'disable_serial_no_and_batch_selector')
                          .then((value) => {
                            if (!value) {
                              erpnext.stock.select_batch_and_serial_no(frm, d);
                            }
                          });
                    
          
        }
    },
    error: function(r) {console.log(r)},
    freeze: true,
    async: true,
      args: {
        item_code,
        warehouse: cstr(s_warehouse) || cstr(t_warehouse),
        transfer_qty,
        serial_no,
        bom_no,
        expense_account,
        cost_center,
        company,
        qty,
        voucher_type,
        voucher_no,
        allow_zero_valuation: 1,
      },
    });
   
  }
}
