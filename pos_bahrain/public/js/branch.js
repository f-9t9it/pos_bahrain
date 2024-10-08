function _setup_queries(frm) {
  if (frm.fields_dict['items'].grid.get_field('pb_branch')) {
    frm.set_query('pb_branch', 'items', function (doc, cdt, cdn) {
      const child = locals[cdt][cdn];
      return {
        query: 'pos_bahrain.api.branch.branch_query',
        filters: { item_code: child.item_code },
      };
    });
  }
}

function _set_data(frm, cdt, cdn) {
  const child = locals[cdt][cdn];
  _get_data(child.pb_branch, child.item_code).then((item_data) => {
    if (item_data) {
      frappe.model.set_value(cdt, cdn, 'pb_branch_qty', item_data.qty);
    }
  });
}

async function _get_data(branch, item) {
  const { message: data } = await frappe.call({
    method: 'pos_bahrain.api.branch.get_branch_qty',
    args: { branch, item },
  });
  return data;
}

frappe.ui.form.on('Sales Order', { onload: _setup_queries });
frappe.ui.form.on('Sales Invoice', { onload: _setup_queries });
frappe.ui.form.on('Purchase Invoice', { onload: _setup_queries });

frappe.ui.form.on('Sales Order Item', { pb_branch: _set_data });
frappe.ui.form.on('Sales Invoice Item', { pb_branch: _set_data });
frappe.ui.form.on('Purchase Invoice Item', { pb_branch: _set_data });
