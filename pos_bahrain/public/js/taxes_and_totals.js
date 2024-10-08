
frappe.provide("erpnext.public");
frappe.provide("erpnext.controllers");

// erpnext.taxes_and_totals.prototype.update_paid_amount_for_return = function() {
// // update_paid_amount_for_return: function() {
//     var grand_total = this.frm.doc.rounded_total || this.frm.doc.grand_total;

//     if(this.frm.doc.party_account_currency == this.frm.doc.currency) {
//         var total_amount_to_pay = flt((grand_total - this.frm.doc.total_advance
//             - this.frm.doc.write_off_amount), precision("grand_total"));
//     } else {
//         var total_amount_to_pay = flt(
//             (flt(grand_total*this.frm.doc.conversion_rate, precision("grand_total"))
//                 - this.frm.doc.total_advance - this.frm.doc.base_write_off_amount),
//             precision("base_grand_total")
//         );
//     }

//     let existing_amount = 0
//     $.each(this.frm.doc.payments || [], function(i, row) {
//         existing_amount += row.amount;
//     })

    // if (existing_amount != total_amount_to_pay) {
    //     frappe.db.get_value('Sales Invoice Payment', {'parent': this.frm.doc.pos_profile, 'default': 1},
    //         ['mode_of_payment', 'account', 'type'], (value) => {
    //             if (this.frm.is_dirty()) {
    //                 frappe.model.clear_table(this.frm.doc, 'payments');
    //                 if (value) {
    //                     let row = frappe.model.add_child(this.frm.doc, 'Sales Invoice Payment', 'payments');
    //                     row.mode_of_payment = value.mode_of_payment;
    //                     row.type = value.type;
    //                     row.account = value.account;
    //                     row.default = 1;
    //                     row.amount = total_amount_to_pay;
    //                 } else {
    //                     this.frm.set_value('is_pos', 1);
    //                 }
    //                 this.frm.refresh_fields();
    //                 this.calculate_paid_amount();
    //             }
    //         }, 'Sales Invoice');
    // } else {
    //     this.calculate_paid_amount();
    // }
// }
const TaxesAndTotalsExtend = erpnext.taxes_and_totals.extend({
	// calculate_item_values: () => {
		update_paid_amount_for_return: function() {
            var grand_total = this.frm.doc.rounded_total || this.frm.doc.grand_total;
    
            if(this.frm.doc.party_account_currency == this.frm.doc.currency) {
                var total_amount_to_pay = flt((grand_total - this.frm.doc.total_advance
                    - this.frm.doc.write_off_amount), precision("grand_total"));
            } else {
                var total_amount_to_pay = flt(
                    (flt(grand_total*this.frm.doc.conversion_rate, precision("grand_total"))
                        - this.frm.doc.total_advance - this.frm.doc.base_write_off_amount),
                    precision("base_grand_total")
                );
            }
    
            let existing_amount = 0
            $.each(this.frm.doc.payments || [], function(i, row) {
                existing_amount += row.amount;
            })
    
            if (existing_amount != total_amount_to_pay) {
                frappe.db.get_value('Sales Invoice Payment', {'parent': this.frm.doc.pos_profile, 'default': 1},
                    ['mode_of_payment', 'account', 'type'], (value) => {
                        if (this.frm.is_dirty()) {
                            frappe.model.clear_table(this.frm.doc, 'payments');
                            if (value) {
                                let row = frappe.model.add_child(this.frm.doc, 'Sales Invoice Payment', 'payments');
                                row.mode_of_payment = value.mode_of_payment;
                                row.type = value.type;
                                row.account = value.account;
                                row.default = 1;
                                row.amount = total_amount_to_pay;
                            } else {
                                this.frm.set_value('is_pos', 1);
                            }
                            this.frm.refresh_fields();
                            this.calculate_paid_amount();
                        }
                    }, 'Sales Invoice');
            } else {
                this.calculate_paid_amount();
            }
        },
    
        set_default_payment: function(total_amount_to_pay, update_paid_amount) {
            var me = this;
            var payment_status = true;
            if(this.frm.doc.is_pos && (update_paid_amount===undefined || update_paid_amount)) {
                $.each(this.frm.doc['payments'] || [], function(index, data) {
                    if(data.default && payment_status && total_amount_to_pay > 0) {
                        data.base_amount = flt(total_amount_to_pay, precision("base_amount"));
                        data.amount = flt(total_amount_to_pay / me.frm.doc.conversion_rate, precision("amount"));
                        payment_status = false;
                    } else if(me.frm.doc.paid_amount) {
                        data.amount = 0.0;
                    }
                });
            }
        },
    
});

$.extend(
	cur_frm.cscript,
	new TaxesAndTotalsExtend({frm: cur_frm}),
);