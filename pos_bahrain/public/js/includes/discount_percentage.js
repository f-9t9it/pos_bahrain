function _apply_pb_discount_percentage(doctype) {
  frappe.ui.form.on(doctype, {
    pb_discount_percentage: function (frm) {
      frm.doc.items.forEach(({ doctype, name }) => {
        frappe.model.set_value(
          doctype,
          name,
          'discount_percentage',
          frm.doc.pb_discount_percentage
        );
      });
    },
  });
}

function _apply_pb_discount_percentage_on_item_code(doctype) {
  frappe.ui.form.on(doctype, {
    item_code: function (frm, cdt, cdn) {
      frappe.model.set_value(
        cdt,
        cdn,
        'discount_percentage',
        frm.doc.pb_discount_percentage
      );
    },
  });
}

['Quotation', 'Sales Order', 'Sales Invoice'].forEach((doctype) =>
  _apply_pb_discount_percentage(doctype)
);
[
  'Quotation Item',
  'Sales Order Item',
  'Sales Invoice Item',
].forEach((doctype) => _apply_pb_discount_percentage_on_item_code(doctype));


function _apply_pricelist(doctype) {
  frappe.ui.form.on(doctype, {
    apply_offer: function (frm) {
      frm.doc.items.forEach(({ doctype, name }) => {
        frappe.model.set_value(
          doctype,
          name,
          'pb_price_list',
          frm.doc.customer_price_list
        );
      });
    },
  });
}
['Quotation', 'Sales Order', 'Sales Invoice'].forEach((doctype) =>
_apply_pricelist(doctype)
);

