frappe.ui.form.on("Stock Reconciliation", {
    refresh: function(frm) {
        // Your code here
    },
    set_warehouse: function(frm) {
        let transaction_controller = new erpnext.TransactionController({frm:frm});
        transaction_controller.autofill_warehouse(frm.doc.items, "warehouse", frm.doc.set_warehouse);
    },
});
