import { set_uom_query } from './sales_invoice';
import {
  set_item_from_supplier_pn,
  add_print_label_action,
} from './purchase_invoice';
import pb_scan_barcode from './extensions/scan_barcode.js';

const purchase_receipt_item = {
  pb_supplier_part_no: set_item_from_supplier_pn,
};

export default {
  purchase_receipt_item,
  setup: set_uom_query,
  refresh: add_print_label_action,
  pb_scan_barcode,
};
