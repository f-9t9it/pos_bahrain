import first from 'lodash/first';

// depends on withPaymentValidator
export default function withMultiCurrency(Pos) {
  return class PosExtended extends Pos {
    async init_master_data(r, freeze) {
      const pos_data = await super.init_master_data(r, freeze);
      const { exchange_rates } = pos_data;
      this.exchange_rates = exchange_rates;
      return pos_data;
    }
    _get_exchange_rate(mop) {
      const { mode_of_payment } =
        this.frm.doc.payments.find(({ idx, mode_of_payment }) =>
          mop ? mop === mode_of_payment : cint(idx) === cint(this.idx)
        ) || {};
      return (
        this.exchange_rates[mode_of_payment] || {
          conversion_rate: this.frm.doc.conversion_rate || 1,
          currency: this.frm.doc.currency,
        }
      );
    }
    show_payment_details() {
      const multimode_payments = $(this.$body).find('.multimode-payments')
        .html(`
        <ul class="nav nav-tabs" role="tablist">
          <li role="presentation" class="active">
            <a role="tab" data-toggle="tab" data-target="#multimode_loc">${__(
              'Base'
            )}</a>
          </li>
          <li role="presentation">
            <a role="tab" data-toggle="tab" data-target="#multimode_alt">${__(
              'Alternate'
            )}</a>
          </li>
        </ul>
        <div class="tab-content">
          <div role="tabpanel" class="tab-pane active" id="multimode_loc" />
          <div role="tabpanel" class="tab-pane" id="multimode_alt" />
        </div>
      `);
      const multimode_loc = multimode_payments.find('#multimode_loc');
      const multimode_alt = multimode_payments.find('#multimode_alt');
      if (this.frm.doc.payments.length) {
        this.frm.doc.payments.forEach(
          ({ mode_of_payment, amount, idx, type }) => {
            const { currency, conversion_rate } = this._get_exchange_rate(
              mode_of_payment
            );
            const in_alt_currency = Object.keys(this.exchange_rates).includes(
              mode_of_payment
            );
            const $payment = $(
              frappe.render_template('payment_details', {
                mode_of_payment,
                amount,
                idx,
                currency,
                type,
              })
            ).appendTo(in_alt_currency ? multimode_alt : multimode_loc);
            if (in_alt_currency) {
              $payment.find('div.col-xs-6:first-of-type').css({
                padding: '0 15px',
                display: 'flex',
                'flex-flow': 'column nowrap',
                height: '100%',
                'justify-content': 'center',
              }).html(`
                <div>${mode_of_payment}</div>
                <div style="font-size: 0.75em; color: #888;">
                  CR: ${flt(conversion_rate, this.precision).toFixed(3)}
                  /
                  <span class="local-currency-amount">${format_currency(
                    amount * flt(conversion_rate, this.precision),
                    this.frm.doc.currency
                  )}</span>
                </div>
              `);
            }
            if (type === 'Cash' && amount === this.frm.doc.paid_amount) {
              this.idx = idx;
              this.selected_mode = $(this.$body).find(
                `input[idx='${this.idx}']`
              );
              this.highlight_selected_row();
              this.bind_amount_change_event();
            }
          }
        );
      } else {
        $('<p>No payment mode selected in pos profile</p>').appendTo(
          multimode_payments
        );
      }
    }
    bind_amount_change_event() {
      this.selected_mode.off('change');
      this.selected_mode.on('change', e => {
        this.payment_val = flt(e.target.value, this.precision) || 0.0;
        this.idx = this.selected_mode.attr('idx');
        const { currency } = this._get_exchange_rate();
        this.selected_mode.val(format_currency(this.payment_val, currency));
        this.update_payment_amount();
      });
    }
    update_payment_amount() {
      const selected_payment = this.frm.doc.payments.find(
        ({ idx }) => cint(idx) === cint(this.idx)
      );
      if (selected_payment) {
        const {
          conversion_rate: mop_conversion_rate,
          currency: mop_currency,
        } = this._get_exchange_rate();
        const mop_amount = flt(this.selected_mode.val(), this.precision);
        const amount = flt(mop_amount * mop_conversion_rate, this.precision);
        Object.assign(selected_payment, {
          amount,
          mop_currency,
          mop_conversion_rate,
          mop_amount,
        });
        $(this.$body)
          .find('.selected-payment-mode .local-currency-amount')
          .text(format_currency(amount, this.frm.doc.currency));
      }
      this.calculate_outstanding_amount(false);
      this.show_amounts();
    }
    set_outstanding_amount() {
      this.selected_mode = $(this.$body).find(`input[idx='${this.idx}']`);
      this.highlight_selected_row();
      this.payment_val = 0.0;
      const { conversion_rate, currency } = this._get_exchange_rate();
      if (
        this.frm.doc.outstanding_amount > 0 &&
        flt(this.selected_mode.val(), this.precision) === 0.0
      ) {
        this.payment_val = flt(
          this.frm.doc.outstanding_amount / conversion_rate,
          this.precision
        );
        this.selected_mode.val(format_currency(this.payment_val, currency));
        this.update_payment_amount();
      } else if (flt(this.selected_mode.val(), this.precision) > 0) {
        this.payment_val = flt(this.selected_mode.val(), this.precision);
      }
      this.selected_mode.select();
      this.bind_amount_change_event();
    }
    payment_primary_action() {
      this.frm.doc.payments.forEach(payment => {
        const { mode_of_payment, amount } = payment;
        const {
          conversion_rate: mop_conversion_rate,
          currency: mop_currency,
        } = this._get_exchange_rate(mode_of_payment);
        const mop_amount = flt(amount / mop_conversion_rate, this.precision);
        Object.assign(payment, {
          mop_currency,
          mop_conversion_rate,
          mop_amount,
        });
      });
      super.payment_primary_action();
    }
  };
}
