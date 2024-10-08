import { set_rate_from_batch, set_uom, set_uom_query, set_fields } from './sales_invoice';

const sales_order_item = {
  batch_no: set_rate_from_batch,
  barcode: set_uom,
};

async function set_naming_series(frm) {
  const { os_branch: branch } = frm.doc;
  if (branch) {
    const {
      message: { os_sales_order_naming_series } = {},
    } = await frappe.db.get_value('Branch', branch, 'os_sales_order_naming_series');
    frm.set_value('naming_series', os_sales_order_naming_series);
  }
}

export default {
  sales_order_item,
  setup: set_uom_query,
  pb_branch: set_naming_series,
  refresh: function(frm) {
    if (frm.doc.__islocal) {
      set_fields(frm);
    }
  },
};
