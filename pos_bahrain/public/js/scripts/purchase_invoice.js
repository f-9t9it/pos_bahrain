import {
  set_uom_query,
  set_cost_center_query,
  set_table_cost_centers,
  set_item_cost_center,
} from './sales_invoice';

export async function set_item_from_supplier_pn(frm, cdt, cdn) {
  const { supplier } = frm.doc;
  const { pb_supplier_part_no: supplier_part_no } = frappe.get_doc(cdt, cdn);
  const { message: item } = await frappe.call({
    method: 'pos_bahrain.api.item.fetch_item_from_supplier_part_no',
    args: { supplier, supplier_part_no },
  });
  frappe.model.set_value(cdt, cdn, 'item_code', item && item.name);
}

export function add_print_label_action(frm) {
  frm.page.add_menu_item('Print Labels', () => {
    frappe.set_route('Form/Barcode Print');
  });
}

const purchase_invoice_item = {
  item_code: set_item_cost_center,
  pb_supplier_part_no: set_item_from_supplier_pn,
};

export default {
  purchase_invoice_item,
  setup: function (frm) {
    set_uom_query(frm);
    set_cost_center_query(frm);
  },
  refresh: add_print_label_action,
  pb_set_cost_center: set_table_cost_centers,
};
