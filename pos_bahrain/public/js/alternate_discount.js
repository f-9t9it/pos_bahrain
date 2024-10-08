// Copyright (c) 2018, 	9t9it and contributors
// For license information, please see license.txt

const alternate_discount = {
  doc: {
    selling_price_list: async function(frm) {
      const { selling_price_list } = frm.doc;
      const { message: settings = {} } = await frappe.db.get_value(
        'POS Bahrain Settings',
        null,
        ['discount_on_retail', 'retail_price_list']
      );
      frm.set_value(
        'discount_on_retail_price',
        settings.discount_on_retail &&
        settings.retail_price_list &&
        settings.retail_price_list !== selling_price_list
          ? 1
          : 0
      );
    },
  },
  items: {
    item_code: async function(frm, cdt, cdn) {
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
    },
    discount_percentage_on_retail: function(frm, cdt, cdn) {
      frm.script_manager.trigger('set_discount_from_retail', cdt, cdn);
    },
    retail_price: function(frm, cdt, cdn) {
      frm.script_manager.trigger('set_discount_from_retail', cdt, cdn);
    },
    set_discount_from_retail: function(frm, cdt, cdn) {
      const {
        retail_price,
        discount_percentage_on_retail,
        price_list_rate,
      } = frappe.get_doc(cdt, cdn);
      frappe.model.set_value(
        cdt,
        cdn,
        'rate',
        discount_percentage_on_retail && retail_price
          ? retail_price * (1 - flt(discount_percentage_on_retail) / 100)
          : price_list_rate
      );
    },
  },
};

frappe.ui.form.on('Sales Invoice', alternate_discount.doc);
frappe.ui.form.on('Sales Order', alternate_discount.doc);

frappe.ui.form.on('Sales Invoice Item', alternate_discount.items);
frappe.ui.form.on('Sales Order Item', alternate_discount.items);
