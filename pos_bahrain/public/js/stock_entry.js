// Copyright (c) 2018, 	9t9it and contributors
// For license information, please see license.txt
frappe.provide("pos_bahrain.scripts.extensions.stock_entry_item_code")

frappe.ui.form.off('Stock Entry Detail', 'item_code');
frappe.ui.form.on('Stock Entry Detail', {
  item_code: pos_bahrain.scripts.extensions.stock_entry_item_code,
  s_warehouse: function (frm, cdt, cdn) {
    _set_cost_center('s_warehouse', cdt, cdn);
  },
  t_warehouse: function (frm, cdt, cdn) {
    _set_cost_center('t_warehouse', cdt, cdn);
  },
});


frappe.ui.form.on('Stock Entry', {
  refresh: function (frm) {
    _set_repack_warehouses_read_only(frm);
  },
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
