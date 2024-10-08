export default async function(frm, cdt, cdn) {
  // rewrite of the stock entry detail item_code
  // this prevents 'empty' values from the 'get_item_details' to be set into
  // the item row.
  // this is necessary to stop the 'select_batch_and_serial_no' from showing when
  // a batch_no is already used in the scan_barcode field.

  const d = frappe.get_doc(cdt, cdn);
  if (d.item_code) {
    // exists=frappe.db.get_single_value('POS Bahrain Settings', 'disable_serial_no_and_batch_selector')
    // if (!exists){
    const { company, doctype: voucher_type } = frm.doc;
    const {
      item_code,
      s_warehouse,
      t_warehouse,
      transfer_qty,
      serial_no,
      bom_no,
      expense_account,
      cost_center,
      qty,
      name: voucher_no,
    } = d;
    const { message: details } = await frappe.call({
      doc: frm.doc,
      method: 'get_item_details',
      args: {
        item_code,
        warehouse: cstr(s_warehouse) || cstr(t_warehouse),
        transfer_qty,
        serial_no,
        bom_no,
        expense_account,
        cost_center,
        company,
        qty,
        voucher_type,
        voucher_no,
        allow_zero_valuation: 1,
      },
    });
    if (details) {
      Object.keys(details).forEach(k => {
        if (details[k]) {
          d[k] = details[k];
        }
      });
      refresh_field('items');
      return frappe.db.get_single_value('POS Bahrain Settings', 'disable_serial_no_and_batch_selector')
											.then((value) => {
												if (!value) {
													erpnext.stock.select_batch_and_serial_no(frm, d);
												}
											});
								
      
    }
  }
}
// }