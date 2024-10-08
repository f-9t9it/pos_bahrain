import keyBy from 'lodash/keyBy';

export default function withPaymentReference(Pos) {
  return class PosExtended extends Pos {
    async init_master_data(r, freeze) {
      const pos_data = await super.init_master_data(r, freeze);
      const { mode_of_payment_details } = pos_data;
      this.mode_of_payment_details = mode_of_payment_details;
      return pos_data;
    }
    highlight_selected_row() {
      $(this.$body)
        .find('.multimode-payments .pb_ref_sec')
        .remove();
      this.selected_mode
        .parent()
        .parent()
        .parent()
        .css('height', '60px');
      super.highlight_selected_row();
      const payment =
        this.frm.doc.payments.find(
          ({ idx }) => idx.toString() === this.selected_mode.attr('idx')
        ) || {};
      const mop = this.mode_of_payment_details.find(
        ({ name }) => name === payment.mode_of_payment
      );
      if (mop) {
        const $wrap = $(
          '<div class="pb_ref_sec" style="padding: 0 15px;" />'
        ).on('click', e => {
          e.stopPropagation();
        });
        const { pb_reference_no, pb_reference_date } = payment;
        const { pb_bank_method: bank_method } = mop;
        const ref_no = new frappe.ui.form.ControlData({
          parent: $wrap,
          df: {
            label: 'Reference No',
            onchange: e => {
              payment.pb_reference_no = ref_no.value;
              this.show_amounts();
            },
          },
        });
        ref_no.set_value(pb_reference_no);
        ref_no.refresh();
        if (bank_method === 'Cheque') {
          const ref_date = new frappe.ui.form.ControlDate({
            parent: $wrap,
            df: {
              label: 'Reference Date',
              onchange: e => {
                payment.pb_reference_date = ref_date.value;
                this.show_amounts();
              },
            },
          });
          ref_date.set_value(pb_reference_date);
          ref_date.refresh();
        }
        $wrap.appendTo(
          this.selected_mode
            .parent()
            .parent()
            .parent()
            .css('height', 'auto')
        );
      }
    }
    actions_enabled() {
      const invalidated = this._get_invalid_mop_methods();
      return super.actions_enabled() && invalidated.length === 0;
    }
    payment_primary_action() {
      const invalidated = this._get_invalid_mop_methods();
      if (invalidated.length > 0) {
        frappe.throw(
          __(`Reference missing for method(s): ${invalidated.join(', ')}`)
        );
      }
      super.payment_primary_action();
    }
    _get_invalid_mop_methods() {
      const alt_mops = keyBy(this.mode_of_payment_details, 'name');
      return this.frm.doc.payments
        .filter(
          ({ mode_of_payment, amount, pb_reference_no, pb_reference_date }) => {
            if (amount === 0) {
              return false;
            }
            if (!alt_mops[mode_of_payment]) {
              return false;
            }
            return !verify_alt_mop({
              pb_bank_method: alt_mops[mode_of_payment].pb_bank_method,
              pb_reference_no,
              pb_reference_date,
            });
          }
        )
        .map(({ mode_of_payment }) => mode_of_payment);
    }
  };
}

function verify_alt_mop({
  pb_bank_method,
  pb_reference_no,
  pb_reference_date,
}) {
  if (pb_bank_method === 'Card') {
    return !!pb_reference_no;
  }
  if (pb_bank_method === 'Cheque') {
    return !!pb_reference_no && !!pb_reference_date;
  }
  return true;
}
