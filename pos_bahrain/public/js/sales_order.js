frappe.ui.form.on('Sales Order Item', {
    item_code: function (frm, cdt, cdn) {
        get_total_stock_qty(frm, cdt, cdn)
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


frappe.ui.form.on("Sales Order", {
    refresh: function(frm) {
        // Remove the "Sales Invoice" sub-button from the "Create" button after a delay of 1 second
        setTimeout(function() {
            frm.remove_custom_button('Sales Invoice', 'Create');
        }, 500);

        // Add new custom button
        frm.add_custom_button(__('Sales Invoice '), function() {
            frm.trigger('custom_make_sales_invoice');
        }, __("Create"));
    },

    custom_make_sales_invoice: function(frm) {
        frappe.model.open_mapped_doc({
            method: "pos_bahrain.api.sales_order.make_sales_invoice",
            frm: frm
        });
    }
});


