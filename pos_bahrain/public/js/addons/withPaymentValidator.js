export default function withPaymentValidator(Pos) {
  return class PosExtended extends Pos {
    async init_master_data(r, freeze) {
      const pos_data = await super.init_master_data(r, freeze);
      const { do_not_allow_zero_payment, enforce_full_payment } = pos_data;
      this.do_not_allow_zero_payment = !!cint(do_not_allow_zero_payment);
      this.enforce_full_payment = !!cint(enforce_full_payment);
      return pos_data;
    }
    show_amounts() {
      super.show_amounts();
      this.dialog
        .get_primary_btn()
        .toggleClass('disabled', !this.actions_enabled());
    }
    actions_enabled() {
      if (this.do_not_allow_zero_payment) {
        return this.frm.doc.paid_amount !== 0;
      }
      if (this.enforce_full_payment) {
        return this.frm.doc.outstanding_amount === 0;
      }
      return true;
    }
    payment_primary_action() {
      this._validate_payment();
      this.dialog.hide();
      this.submit_invoice();
    }
    _validate_payment() {
      if (this.do_not_allow_zero_payment) {
        const paid_amount = this.frm.doc.payments.reduce(
          (a, { amount = 0 }) => a + amount,
          0
        );
        if (!paid_amount) {
          return frappe.throw(__('Paid Amount cannot be zero'));
        }
      }
      if (this.enforce_full_payment) {
        const paid_amount = this.frm.doc.payments.reduce(
          (a, { amount = 0 }) => a + amount,
          0
        );
        const bill_amount =
          this.frm.doc.rounded_total || this.frm.doc.grand_total || 0;
        if (paid_amount < bill_amount) {
          return frappe.throw(
            __(
              `Paid Amount cannot be less than Total Amount ${fmt_money(
                bill_amount
              )}`
            )
          );
        }
      }
    }
  };
}
