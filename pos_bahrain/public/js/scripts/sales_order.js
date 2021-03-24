import { set_rate_from_batch, set_uom, set_uom_query, set_fields } from './sales_invoice';

const sales_order_item = {
  batch_no: set_rate_from_batch,
  barcode: set_uom,
};

export default {
  sales_order_item,
  setup: set_uom_query,
  refresh: function(frm) {
    if (frm.doc.__islocal) {
      set_fields(frm);
    }
  },
};
