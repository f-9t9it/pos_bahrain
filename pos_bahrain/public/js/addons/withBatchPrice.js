import first from 'lodash/first';

// depends on withAsyncAddToCart
export default function withBatchPrice(Pos) {
  return class PosExtended extends Pos {
    async init_master_data(r, freeze) {
      const pos_data = await super.init_master_data(r, freeze);
      this.use_batch_price = !!cint(pos_data.use_batch_price);
      return pos_data;
    }
    _apply_batch_price(item) {
      if (this.use_batch_price && item && item.batch_no) {
        const {
          pb_price_based_on: based_on,
          pb_rate: rate,
          pb_discount: discount_percentage,
        } =
          this.batch_no_details[item.item_code].find(
            ({ name }) => name === item.batch_no
          ) || {};
        if (based_on === 'Based on Rate') {
          item.rate = rate * item.conversion_factor;
        } else if (based_on === 'Based on Discount') {
          item.discount_percentage = discount_percentage;
        } else {
          item.rate = item.price_list_rate;
          item.discount_percentage = 0;
        }
        this.update_paid_amount_status(false);
      }
    }
    async add_to_cart() {
      const item = await super.add_to_cart();
      this._apply_batch_price(item);
      return item;
    }
    render_selected_item() {
      super.render_selected_item();
      ['.pos-item-uom', '.pos-item-batch'].forEach(className => {
        this.wrapper.find(className).on('change', () => {
          this._apply_batch_price(first(this.child_doc));
        });
      });
    }
  };
}
