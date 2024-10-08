import keyBy from 'lodash/keyBy';

// depends on withIdx
export default function withBase(Pos) {
  return class PosExtended extends Pos {
    onload() {
      super.onload();
      this.precision =
        frappe.defaults.get_default('currency_precision') ||
        frappe.defaults.get_default('float_precision');
    }
    async init_master_data(r, freeze) {
      const pos_data = await super.init_master_data(r, freeze);
      this.items_by_item_code = keyBy(this.item_data, 'name');
      return pos_data;
    }
    set_payment_primary_action() {
      this.dialog.set_primary_action(
        __('Submit'),
        this.payment_primary_action.bind(this)
      );
    }
    payment_primary_action() {
      // callback for the 'Submit' button in the payment modal. copied from upstream.
      // implemented as a class method to make the callback extendable from
      // subsequent hocs

      // Allow no ZERO payment
      $.each(this.frm.doc.payments, (index, data) => {
        if (data.amount != 0) {
          this.dialog.hide();
          this.submit_invoice();
          return;
        }
      });
    }
    make_new_cart() {
      super.make_new_cart();
      this.items = this.item_data;
      this.search_item.$input.val('');
      this.make_item_list();
    }
    set_item_details(item_code, field, value, remove_zero_qty_items) {
      // this method is a copy of the original with discount fixes and uses
      // `selected_cart_idx` to find the item to be be operated on.
      if (value < 0) {
        frappe.throw(__('Enter value must be positive'));
      }

      this.remove_item = [];
      const item = this.frm.doc.items[this.selected_cart_idx];
      if (item) {
        if (item.serial_no && field == 'qty') {
          this.validate_serial_no_qty(item, item_code, field, value);
        }

        item[field] = flt(value, this.precision);
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
      if (field === 'qty') {
        this.remove_zero_qty_items_from_cart();
      }
      this.update_paid_amount_status(false);
    }
  };
}
