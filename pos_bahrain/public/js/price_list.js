function _setup_queries(frm) {
  if (frm.fields_dict['items'].grid.get_field('item_code')) {
    frm.set_query('pb_price_list', 'items', function (doc, cdt, cdn) {
      const child = locals[cdt][cdn];
      return {
        query: 'pos_bahrain.api.price_list.price_list_query',
        filters: {
          item_code: child.item_code,
          currency: frm.doc.currency,
          selling: 1,
        },
      };
    });
  }
}

function _set_price_list_rate(frm, cdt, cdn) {
  const child = locals[cdt][cdn];
  _get_selling_rate(
    child.item_code,
    child.pb_price_list,
    frm.doc.currency
  ).then((selling_rate) => {
    if (selling_rate) {
      frappe.model.set_value(cdt, cdn, 'price_list_rate', selling_rate);
    }
  });
}

async function _get_selling_rate(item, price_list, currency) {
  const { message: data } = await frappe.call({
    method: 'pos_bahrain.api.price_list.get_selling_rate',
    args: { item, price_list, currency },
  });
  return data.price_list_rate;
}

frappe.ui.form.on('Sales Order', { onload: _setup_queries });
frappe.ui.form.on('Sales Invoice', { onload: _setup_queries });
frappe.ui.form.on('Sales Order Item', { pb_price_list: _set_price_list_rate });
frappe.ui.form.on('Sales Invoice Item', {
  pb_price_list: _set_price_list_rate,
});