// Copyright (c) 2021, 	9t9it and contributors
// For license information, please see license.txt

frappe.ui.form.on('Repack Request', {
  onload: function (frm) {
    frm.add_fetch('item_code', 'item_name', 'item_name');

    // item_code
    ['items', 'to_items'].forEach((item_table) => {
      frm.set_query('item_code', item_table, function (doc, cdt, cdn) {
        return {
          query: 'erpnext.controllers.queries.item_query',
          filters: {
            is_stock_item: 1,
          },
        };
      });
      frm.fields_dict[item_table].grid.get_field(
        'warehouse'
      ).get_query = function (doc) {
        return {
          filters: { company: doc.company },
        };
      };
    });

    if (frm.doc.company) {
      erpnext.queries.setup_queries(frm, 'Warehouse', function () {
        return erpnext.queries.warehouse(frm.doc);
      });
    }
  },
  refresh: function (frm) {
    if (frm.doc.company) {
      frm.trigger('toggle_display_account_head');
    }
    _make_custom_buttons(frm);
  },
  toggle_display_account_head: function (frm) {
    frm.toggle_display(
      ['expense_account', 'cost_center'],
      erpnext.is_perpetual_inventory_enabled(frm.doc.company)
    );
  },
  company: function (frm) {
    frm.trigger('toggle_display_account_head');
  },
  schedule_date: function (frm) {
    _set_schedule_date(frm);
  },
  scan_barcode: function (frm) {
    _scan_barcode(frm, 'scan_barcode', 'items');
  },
  to_scan_barcode: function (frm) {
    _scan_barcode(frm, 'to_scan_barcode', 'to_items');
  },
  warehouse: function (frm) {
    frm.doc.items.forEach((item) => _set_warehouse(frm, item.doctype, item.name));
    frm.doc.to_items.forEach((item) => _set_warehouse(frm, item.doctype, item.name));
  },
});

const item_script = {
  qty: function (frm, doctype, name) {
    var d = locals[doctype][name];
    if (flt(d.qty) < flt(d.min_order_qty)) {
      frappe.msgprint(
        __('Warning: Material Requested Qty is less than Minimum Order Qty')
      );
    }
    const item = locals[doctype][name];
    _get_item_data(frm, item);
  },

  rate: function (frm, doctype, name) {
    const item = locals[doctype][name];
    _get_item_data(frm, item);
  },

  item_code: function (frm, doctype, name) {
    const item = locals[doctype][name];
    item.rate = 0;
    _set_schedule_date(frm);
    _get_item_data(frm, item);
  },

  schedule_date: function (frm, cdt, cdn) {
    var row = locals[cdt][cdn];
    if (row.schedule_date) {
      if (!frm.doc.schedule_date) {
        erpnext.utils.copy_value_in_all_rows(
          frm.doc,
          cdt,
          cdn,
          'items',
          'schedule_date'
        );
      } else {
        _set_schedule_date(frm);
      }
    }
  },
};

frappe.ui.form.on('Repack Request Item From', item_script);
frappe.ui.form.on('Repack Request Item To', item_script);


function _scan_barcode(frm, barcode_field, child_table) {
  let scan_barcode_field = frm.fields_dict[barcode_field];

  let show_description = function (idx, exist = null) {
    let message = '';
    if (exist) {
      message = __('Row #{0}: Qty increased by 1', [idx]);
    } else {
      message = __('Row #{0}: Item added', [idx]);
    }
    scan_barcode_field.set_new_description(message);
    frappe.show_alert({
      message: message,
      indicator: 'green',
    });
  };

  if (frm.doc[barcode_field]) {
    frappe
      .call({
        method:
          'erpnext.selling.page.point_of_sale.point_of_sale.search_serial_or_batch_or_barcode_number',
        args: { search_value: frm.doc[barcode_field] },
      })
      .then((r) => {
        const data = r && r.message;
        if (!data || Object.keys(data).length === 0) {
          scan_barcode_field.set_new_description(
            __('Cannot find Item with this barcode')
          );
          frappe.show_alert({
            message: 'Cannot find Item with this barcode',
            indicator: 'red',
          });
          return;
        }

        let cur_grid = frm.fields_dict[child_table].grid;

        let row_to_modify = null;
        const existing_item_row = frm.doc[child_table].find(
          (d) => d.item_code === data.item_code && d.batch_no === data.batch_no
        );
        const blank_item_row = frm.doc[child_table].find((d) => !d.item_code);

        if (existing_item_row) {
          row_to_modify = existing_item_row;
        } else if (blank_item_row) {
          row_to_modify = blank_item_row;
        }

        if (!row_to_modify) {
          // add new row
          row_to_modify = frappe.model.add_child(
            frm.doc,
            cur_grid.doctype,
            'items'
          );
        }

        show_description(row_to_modify.idx, row_to_modify.item_code);

        frm.from_barcode = true;
        frappe.model.set_value(row_to_modify.doctype, row_to_modify.name, {
          item_code: data.item_code,
          qty: (row_to_modify.qty || 0) + 1,
        });

        ['serial_no', 'batch_no', 'barcode'].forEach((field) => {
          if (
            data[field] &&
            frappe.meta.has_field(row_to_modify.doctype, field)
          ) {
            frappe.model.set_value(
              row_to_modify.doctype,
              row_to_modify.name,
              field,
              data[field]
            );
          }
        });

        if (frm.doc.warehouse) {
          frappe.model.set_value(
            row_to_modify.doctype,
            row_to_modify.name,
            'warehouse',
            frm.doc.warehouse
          );
        }

        scan_barcode_field.set_value('');
        refresh_field(child_table);
      });
  }
  return false;
}


function _make_custom_buttons(frm) {
  if (frm.doc.docstatus === 1 && frm.doc.status != "Stopped" && frappe.user.has_role('Stock Manager') || frappe.user.has_role('Store Keeper')) {
    frm.add_custom_button(__('Repack Entry'), () => {
      frappe.model.open_mapped_doc({
        method:
          'pos_bahrain.pos_bahrain.doctype.repack_request.repack_request.make_stock_entry',
        frm: frm,
      });
    });
    frm.add_custom_button(__('Stop'), () => _update_status(frm, 'Stopped'));
  }
  if (frm.doc.docstatus == 1 && frm.doc.status == 'Stopped') {
    frm.add_custom_button(__('Re-open'), () => _update_status(frm, 'Pending'));
  }
}


// https://github.com/frappe/erpnext/blob/version-11/erpnext/stock/doctype/material_request/material_request.js#L361
function _set_schedule_date(frm) {
  if (frm.doc.schedule_date) {
    ['items', 'to_items'].forEach((item_table) => {
      erpnext.utils.copy_value_in_all_rows(
        frm.doc,
        frm.doc.doctype,
        frm.doc.name,
        item_table,
        'schedule_date'
      );
    });
  }
}


function _get_item_data(frm, item) {
  frm.call({
    method:
      'pos_bahrain.pos_bahrain.doctype.repack_request.repack_request.get_item_details',
    child: item,
    args: {
      args: {
        item_code: item.item_code,
        warehouse: item.warehouse,
        doctype: frm.doc.doctype,
        child_doctype: item.doctype,
        buying_price_list: frappe.defaults.get_default('buying_price_list'),
        currency: frappe.defaults.get_default('Currency'),
        name: frm.doc.name,
        qty: item.qty || 1,
        stock_qty: item.stock_qty,
        company: frm.doc.company,
        conversion_rate: 1,
        material_request_type: frm.doc.material_request_type,
        plc_conversion_rate: 1,
        rate: item.rate,
        conversion_factor: item.conversion_factor,
      },
    },
    callback: function (r) {
      const d = item;
      if (!r.exc) {
        $.each(r.message, function (k, v) {
          if (!d[k]) d[k] = v;
        });
      }
    },
  });
}


function _set_warehouse(frm, cdt, cdn) {
  frappe.model.set_value(cdt, cdn, 'warehouse', frm.doc.warehouse);
};


function _update_status(frm, status) {
  frappe.call({
    method: 'pos_bahrain.api.repack_request.update_status',
    args: { name: frm.doc.name, status },
    callback: function (r) {
      if (!r.exc) {
        frm.reload_doc();
      }
    }
  });
}
