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
