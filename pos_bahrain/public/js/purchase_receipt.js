frappe.ui.form.on('Purchase Receipt Item', {
    item_code: function (frm, cdt, cdn) {
        get_total_stock_qty(frm, cdt, cdn)
    },
    pb_supplier_part_no:function (frm, cdt, cdn) {
    set_item_from_supplier_pn(frm, cdt, cdn)
    }
});

function get_total_stock_qty(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    if (d.item_code === undefined) {
        return;
    }
    frappe.call({
        method: "pos_bahrain.api.stock.get_total_stock_qty",
        args: {
            item_code: d.item_code
        },
        callback: function (r) {
            frappe.model.set_value(cdt, cdn, "total_available_qty", r.message);
        }
    })
}

async function set_item_from_supplier_pn(frm, cdt, cdn) {
  const { supplier } = frm.doc;
  const { pb_supplier_part_no: supplier_part_no } = frappe.get_doc(cdt, cdn);
  const { message: item } = await frappe.call({
    method: 'pos_bahrain.api.item.fetch_item_from_supplier_part_no',
    args: { supplier, supplier_part_no },
  });
  frappe.model.set_value(cdt, cdn, 'item_code', item && item.name);
}