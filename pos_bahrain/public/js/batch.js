frappe.ui.form.on("Batch", {
    refresh: (frm) => {
        if (!frm.is_new()) {
            if(frappe.user_roles.includes("System Manager") || frappe.user_roles.includes("Accounts Manager") || frappe.user_roles.includes("Stock User")) {
            frm.add_custom_button(__("Recalculate Batch Quantity"), () => {
				frappe.call({
					method: "pos_bahrain.api.batch_recall.recalculate_batch_quantities",
					args:{doc: frm.doc},
					freeze: true,
					callback: () => {
						frm.reload_doc();
					},
				});
            
			});
        
        }
    }
    

}});

