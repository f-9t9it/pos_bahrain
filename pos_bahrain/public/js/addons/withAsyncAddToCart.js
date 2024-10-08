// depends on withExtendedBatchSelector
export default function withAsyncAddToCart(Pos) {
  return class PosExtended extends Pos {
    async add_to_cart() {
      this.validate_add_to_cart && this.validate_add_to_cart();
      this.customer_validate();

      const { has_batch_no } = this.items[0];
      const batch_no = await this.mandatory_batch_no();
      if (has_batch_no && !batch_no) {
        return;
      }

      this.validate_serial_no();
      this.validate_warehouse();
      this._add_or_update_cart();
      return this._get_matched_items_in_cart({
        item_code: this.items[0].item_code,
        uom: this.items[0].uom || this.items[0].stock_uom,
        batch_no,
      });
    }
    _get_matched_items_in_cart(item_to_match = {}) {
      return (this.frm.doc['items'] || []).find(x =>
        Object.keys(item_to_match).every(
          field => x[field] === item_to_match[field]
        )
      );
    }
    _add_or_update_cart() {
      const { item_code, uom, stock_uom } = this.items[0];
      const batch_no = this.item_batch_no[item_code];
      const item = this._get_matched_items_in_cart({
        item_code,
        batch_no,
        uom: uom || stock_uom,
      });
      if (item) {
        item.qty += this.frm.doc.is_return ? -1 : 1;
        item.amount = flt(item.rate * item.qty, this.precision);
        if (this.item_serial_no[item.item_code]) {
          item.serial_no += '\n' + this.item_serial_no[item.item_code][0];
          item.warehouse = this.item_serial_no[item.item_code][1];
        }
      } else {
        this.add_new_item_to_grid();
      }
      this.item_batch_no[item_code] = null;
      this.update_paid_amount_status(false);
      this.wrapper.find('.item-cart-items').scrollTop(1000);
    }
  };
}
