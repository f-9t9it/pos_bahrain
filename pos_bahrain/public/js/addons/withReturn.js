export default function withReturn(Pos) {
  return class PosExtended extends Pos {
    async init_master_data(r, freeze) {
      const pos_data = await super.init_master_data(r, freeze);
      const { allow_returns } = pos_data;
      this.allow_returns = !!cint(allow_returns);
      if (this.allow_returns) {
        this._after_get_data_from_server();
      }
      return pos_data;
    }
    _after_get_data_from_server() {
      this.make_control();
      this.create_new();
      this.make();
    }
    create_new() {
      super.create_new();
      if (this.allow_returns) {
        this.wrapper
          .find('.pos-bill-wrapper .return-row #is_return_check')
          .prop('checked', false);
      }
    }
    set_item_details(item_code, field, value, remove_zero_qty_items) {
      if (this.allow_returns && value < 0) {
        frappe.throw(__('Enter value must be positive'));
      }

      // this method is a copy of the original without the negative value validation
      // and return invoice feature added.
      const idx = this.wrapper.find('.pos-bill-item.active').data('idx');
      this.remove_item = [];

      (this.frm.doc.items || []).forEach((item, id) => {
        if (item.item_code === item_code && id === idx) {
          if (item.serial_no && field === 'qty') {
            this.validate_serial_no_qty(item, item_code, field, value);
          }
          if (field === 'qty') {
            item.qty = (this.frm.doc.is_return ? -1 : 1) * Math.abs(value);
          } else {
            item[field] = flt(value, this.precision);
          }
          item.amount = flt(item.rate * item.qty, this.precision);
          if (item.qty === 0 && remove_zero_qty_items) {
            this.remove_item.push(item.idx);
          }
          if (field === 'discount_percentage' && value === 0) {
            item.rate = item.price_list_rate;
          }
          if (field === 'rate') {
            const discount_percentage = flt(
              (1.0 - value / item.price_list_rate) * 100.0,
              this.precision
            );
            if (discount_percentage > 0) {
              item.discount_percentage = discount_percentage;
            }
          }
        }
      });
      if (field === 'qty') {
        this.remove_zero_qty_items_from_cart();
      }
      this.update_paid_amount_status(false);
    }
    make_control() {
      super.make_control();
      if (this.allow_returns) {
        this._make_return_control();
      }
    }
    _make_return_control() {
      this.numeric_keypad
        .parent()
        .css('margin-top', 0)
        .before(
          `
          <div class="return-row form-check text-right" style="margin-top: 30px">
            <input class="form-check-input" type="checkbox" id="is_return_check">
            <label class="form-check-label" for="is_return_check">${__(
              'Is Return'
            )}</label>
          </div>
          `
        );
      this.wrapper
        .find('.pos-bill-wrapper .return-row #is_return_check')
        .on('change', e => {
          this.frm.doc.is_return = e.target.checked ? 1 : 0;
          (this.frm.doc.items || []).forEach(item => {
            item.qty = (this.frm.doc.is_return ? -1 : 1) * Math.abs(item.qty);
          });
          this.update_paid_amount_status(false);
        });
    }
    calculate_outstanding_amount(update_paid_amount) {
      super.calculate_outstanding_amount();
      if (this.frm.doc.is_return) {
        const total_amount_to_pay = this._get_amount_to_pay();
        this.set_default_payment(total_amount_to_pay, update_paid_amount);
        this.calculate_paid_amount();
      }
    }
    set_default_payment(total_amount_to_pay, update_paid_amount) {
      super.set_default_payment(total_amount_to_pay, update_paid_amount);
      if (
        this.frm.doc.is_return &&
        [undefined, true].includes(update_paid_amount)
      ) {
        this.frm.doc.payments.forEach(p => {
          p.amount = 0;
        });
        if (total_amount_to_pay < 0) {
          const default_payment = this.frm.doc.payments.find(p => p.default);
          default_payment.base_amount = flt(
            total_amount_to_pay,
            this.precision
          );
          default_payment.amount = flt(
            total_amount_to_pay / this.frm.doc.conversion_rate,
            this.precision
          );
        }
      }
    }
    _get_amount_to_pay() {
      const grand_total =
        this.frm.doc.rounded_total || this.frm.doc.grand_total;
      if (this.frm.doc.party_account_currency === this.frm.doc.currency) {
        return flt(
          grand_total -
            this.frm.doc.total_advance -
            this.frm.doc.write_off_amount,
          this.precision
        );
      }
      return flt(
        flt(grand_total * this.frm.doc.conversion_rate, this.precision) -
          this.frm.doc.total_advance -
          this.frm.doc.base_write_off_amount,
        this.precision
      );
    }
  };
}
