const TaxesAndTotalsExtend = erpnext.taxes_and_totals.extend({
	calculate_outstanding_amount(update_paid_amount) {
		// NOTE:
		// paid_amount and write_off_amount is only for POS/Loyalty Point Redemption Invoice
		// total_advance is only for non POS Invoice
		if(in_list(["Sales Invoice", "POS Invoice"], this.frm.doc.doctype) && this.frm.doc.is_return){
			this.calculate_paid_amount();
		}

		if ((this.frm.doc.is_return && this.frm.doctype != 'Sales Invoice') || (this.frm.doc.docstatus > 0)) return;

		frappe.model.round_floats_in(this.frm.doc, ["grand_total", "total_advance", "write_off_amount"]);

		if(in_list(["Sales Invoice", "POS Invoice", "Purchase Invoice"], this.frm.doc.doctype)) {

			let grand_total = this.frm.doc.rounded_total || this.frm.doc.grand_total;
			let base_grand_total = this.frm.doc.base_rounded_total || this.frm.doc.base_grand_total;

			if(this.frm.doc.party_account_currency == this.frm.doc.currency) {
				var total_amount_to_pay = flt((grand_total - this.frm.doc.total_advance
					- this.frm.doc.write_off_amount), precision("grand_total"));
			} else {
				var total_amount_to_pay = flt(
					(flt(base_grand_total, precision("base_grand_total"))
						- this.frm.doc.total_advance - this.frm.doc.base_write_off_amount),
					precision("base_grand_total")
				);
			}

			frappe.model.round_floats_in(this.frm.doc, ["paid_amount"]);
			this.set_in_company_currency(this.frm.doc, ["paid_amount"]);

			if(this.frm.refresh_field){
				this.frm.refresh_field("paid_amount");
				this.frm.refresh_field("base_paid_amount");
			}

			if(in_list(["Sales Invoice", "POS Invoice"], this.frm.doc.doctype)) {
				let total_amount_for_payment = (this.frm.doc.redeem_loyalty_points && this.frm.doc.loyalty_amount)
					? flt(total_amount_to_pay - this.frm.doc.loyalty_amount, precision("base_grand_total"))
					: total_amount_to_pay;
				this.set_default_payment(total_amount_for_payment, update_paid_amount);
				this.calculate_paid_amount();
			}
			this.calculate_change_amount();

			var paid_amount = (this.frm.doc.party_account_currency == this.frm.doc.currency) ?
				this.frm.doc.paid_amount : this.frm.doc.base_paid_amount;
			this.frm.doc.outstanding_amount =  flt(total_amount_to_pay - flt(paid_amount) +
				flt(this.frm.doc.change_amount * this.frm.doc.conversion_rate), precision("outstanding_amount"));
		}
	},
    
});
$.extend(
	cur_frm.cscript,
	new TaxesAndTotalsExtend({frm: cur_frm}),
);