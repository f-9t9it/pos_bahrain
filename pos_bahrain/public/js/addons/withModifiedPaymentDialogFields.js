export default function withModifiedPaymentDialogFields(Pos) {
  return class PosExtended extends Pos {
    make_payment() {
      if (this.dialog) {
        this.dialog.$wrapper.remove();
      }
      super.make_payment();
      ['.change_amount', '.write_off_amount'].forEach(selector => {
        this.dialog.$body
          .find(selector)
          .parent()
          .parent()
          .addClass('hidden');
      });
      $(
        `<div class="col-xs-6 col-sm-3 text-center">
          <p style="font-size: 16px;">Change</p>
          <h3 class="change_amount_static">${format_currency(
            this.frm.doc.change_amount,
            this.frm.doc.currency
          )}</h3>
        </div>`
      ).appendTo(this.dialog.$body.find('.amount-row'));
    }
    show_payment_details() {
      super.show_payment_details();

      // hack to focus on first mop. need to find a better method instead of
      // relying on timer
      setTimeout(() => {
        this.dialog.$body.find('div.pos-payment-row[idx="1"]').click();
      }, 500);
    }
    show_amounts() {
      super.show_amounts();
      $(this.$body)
        .find('.change_amount_static')
        .text(
          format_currency(this.frm.doc.change_amount, this.frm.doc.currency)
        );
    }
    print_dialog() {
      super.print_dialog();
      if (this.msgprint) {
        $(
          `<div style="display: inline; float: right;">
            <span style="font-size: 16px;">Change</span>
            <span style="font-size: 18px; font-weight: bold;">${format_currency(
              this.frm.doc.change_amount,
              this.frm.doc.currency
            )}</span>
          </div>`
        ).appendTo(this.msgprint.$body.find('.msgprint'));
      }
    }
  };
}
