// Copyright (c) 2018, 	9t9it and contributors
// For license information, please see license.txt

async function set_retail_price(frm, cdt, cdn) {
  const { item_code } = frappe.get_doc(cdt, cdn);
  if (item_code) {
    const { message: retail_price } = await frappe.call({
      method: 'pos_bahrain.api.item.get_retail_price',
      args: { item_code },
    });
    frappe.model.set_value(cdt, cdn, 'retail_price', retail_price);
  } else {
    frappe.model.set_value(cdt, cdn, 'retail_price', null);
  }
}

function supplier_part_no_prompt() {
  return new Promise(function(resolve, reject) {
    frappe.prompt([
      {'fieldname': 'supplier_part_no', 'fieldtype': 'Data', 'label': 'Supplier Part No', 'reqd': 1}
    ], function(values) {
      resolve(values.supplier_part_no);
    }, 'Fetch from Supplier Part No');
  });
}

frappe.ui.form.on('Purchase Invoice Item', {
  item_code: set_retail_price,
});
frappe.ui.form.on('Purchase Order Item', {
  item_code: set_retail_price,
});

frappe.ui.form.on('Purchase Invoice', {
  pb_fetch_item_from_supplier_part_no: async function(frm) {
    const supplier_part_no = await supplier_part_no_prompt();
    const { message: item } = await frappe.call({
      method: 'pos_bahrain.api.item.fetch_item_from_supplier_part_no',
      args: { supplier_part_no }
    });

    if (!item) {
      frappe.throw(
          __('No Item with the given Supplier Part No')
      );
    }

    const item_child = frm.add_child("items");
    frappe.model.set_value(item_child.doctype, item_child.name, "item_code", item.name);
    frm.refresh_field("items");
  }
});
