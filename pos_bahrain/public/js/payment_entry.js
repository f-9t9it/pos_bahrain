frappe.ui.form.on('Payment Entry', {
    onload_post_render: function (frm) {
        add_pos_profile_and_branch_to_payment_entry(frm);
    }
});

function add_pos_profile_and_branch_to_payment_entry(frm) {
    if (cur_frm.doc.__islocal) {
        frappe.call({
            method: "pos_bahrain.api.payment_entry.add_pos_profile_and_branch_to_payment_entry",
            async: false,
            callback: function (r) {
                if (r.message != 0) {
                    frm.set_value("cost_center", r.message.b_form_cost_center)
                    frm.set_value("pb_branch", r.message.b_form_branch)
                    frm.set_value("pb_pos_profile", r.message.pos_profile)
                    if (!r.message.b_form_branch && r.message.b_employee_branch) {
                        frm.set_value("pb_branch", r.message.b_employee_branch)
                    }
                }
            }
        })
    }
}
