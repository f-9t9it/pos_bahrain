frappe.ui.form.on(cur_frm.doc.doctype, {
refresh(frm) {
 frm.set_query('uom', 'items', function (doc, cdt, cdn) {
    const { item_code } = frappe.get_doc(cdt, cdn) || {};
    return {
      query: 'pos_bahrain.api.item.query_uom',
      filters: { item_code },
    };
  });
}
})