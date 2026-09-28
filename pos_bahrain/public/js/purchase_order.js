frappe.ui.form.on('Purchase Order', {	
	validate: function(frm) {   
         if (frm.doc.items) {
            frm.doc.items.forEach(row => {
                if (row.item_code) {
                    update_additional_qty(frm, row.doctype, row.name);
                }
            });
        }
    },
	additional_warehouse: function(frm) {
        if (frm.doc.items) {
            frm.doc.items.forEach(row => {
                if (row.item_code) {
                    update_additional_qty(frm, row.doctype, row.name);
                }
            });
        }
    }
	
})

frappe.ui.form.on('Purchase Order Item', {
    item_code: function (frm, cdt, cdn) {
        get_total_stock_qty(frm, cdt, cdn);
        update_additional_qty(frm, cdt, cdn);
    },
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

function update_additional_qty(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    
    if (row.item_code && frm.doc.additional_warehouse) {
        frappe.db.get_value("Bin", {
            "item_code": row.item_code,
            "warehouse": frm.doc.additional_warehouse
        }, "actual_qty", (r) => {
            if (r && r.actual_qty) {
                frappe.model.set_value(cdt, cdn, 'additional_qty', r.actual_qty);
            } else {
                frappe.model.set_value(cdt, cdn, 'additional_qty', 0);
            }
        });
    } else {
        frappe.model.set_value(cdt, cdn, 'additional_qty', 0);
    }
}