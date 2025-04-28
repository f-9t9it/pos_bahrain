export default async function(frm) {
  const scan_fieldname = ['Purchase Receipt'].includes(frm.doc.doctype)
    ? 'pb_scan_barcode'
    : 'scan_barcode';
  function set_description(msg) {
    frm.fields_dict[scan_fieldname].set_new_description(__(msg));
  }

  const search_value = frm.doc[scan_fieldname];
  const { items } = frm.doc;

  if (search_value) {
    const { message: data } = await frappe.call({
      method:
        'erpnext.selling.page.point_of_sale.point_of_sale.search_for_serial_or_batch_or_barcode_number',
      args: { search_value },
    });
    if (!data || Object.keys(data).length === 0) {
      set_description('Cannot find Item with this barcode');
      return;
    }
    const row =
      items.find(({ item_code, batch_no }) => {
        if (batch_no) {
          return item_code == data.item_code && batch_no == data.batch_no;
        }
        return item_code === data.item_code;
      }) ||
      items.find(({ item_code }) => !item_code) ||
      frappe.model.add_child(
        frm.doc,
        frm.fields_dict['items'].grid.doctype,
        'items'
      );

    if (row.item_code) {
      set_description(`Row #${row.idx}: Qty increased by 1`);
    } else {
      set_description(`Row #${row.idx}:Item added`);
    }

    frm.from_barcode = true;

    const { qty = 0 } = row;
    await frappe.model.set_value(
      row.doctype,
      row.name,
      Object.assign(
        data,
        {
          qty: cint(frm.doc.is_return) ? qty - 1 : qty + 1,
        },
        frm.doc.doctype === 'Stock Entry' && {
          s_warehouse: frm.doc.from_warehouse,
          t_warehouse: frm.doc.to_warehouse,
        }
      )
    );

    // this is necessary because the upstream `item_code` event unsets the `batch_no` via `get_item_details`
    // https://github.com/frappe/erpnext/blob/926150bccbf1d93bacebcf36dc33a3d116173138/erpnext/stock/get_item_details.py#L23
    // https://github.com/frappe/erpnext/blob/926150bccbf1d93bacebcf36dc33a3d116173138/erpnext/public/js/controllers/transaction.js#L400
    // should monitor changes to `get_item_details` and its callback and remove when necessary
    if (data.batch_no) {
      const wait_for_item_code_event = setInterval(() => {
        const { doctype: cdt, name: cdn } = row;
        const { batch_no } = frappe.get_doc(cdt, cdn);
        if (batch_no === null) {
          frappe.model.set_value(cdt, cdn, 'batch_no', data.batch_no);
          clearInterval(wait_for_item_code_event);
        }
      }, 300);
    }

    frm.fields_dict[scan_fieldname].set_value('');
  }
  return false;
}
