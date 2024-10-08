import first from 'lodash/first';

// depends on withUom
export default function withBarcodeUom(Pos) {
  return class PosExtended extends Pos {
    async init_master_data(r, freeze) {
      const pos_data = await super.init_master_data(r, freeze);
      const { use_barcode_uom, barcode_details } = pos_data;
      this.use_barcode_uom = !!cint(use_barcode_uom);
      this.barcode_details = barcode_details;
      this.barcode = null;
      return pos_data;
    }
    make_item_list(customer) {
      this.barcode =
        this.use_barcode_uom &&
        this.barcode_details &&
        this.barcode_details[this.search_item.$input.val()];
      super.make_item_list(customer);
    }
    _apply_barcode_uom(item) {
      if (this.use_barcode_uom && this.barcode) {
        const { item_code } = item;
        const { uom, barcode } = this.barcode;
        const { conversion_factor = 1 } =
          (this.uom_details[item_code] || []).find(x => x.uom === uom) || {};
        const price_list_rate = this.get_item_price({ item_code, uom });
        Object.assign(item, {
          barcode,
          conversion_factor,
          rate: price_list_rate,
          price_list_rate,
          amount: flt(item.qty * price_list_rate, this.precision),
        });
        this.update_paid_amount_status(false);
      }
    }
    async add_to_cart() {
      if (this.use_barcode_uom && this.barcode) {
        const { uom } = this.barcode;
        this.items[0].uom = uom;
      }
      const item = await super.add_to_cart();
      this._apply_barcode_uom(item);
      return item;
    }
    add_new_item_to_grid() {
      super.add_new_item_to_grid();
      if (this.use_barcode_uom && this.barcode) {
        const { uom } = this.barcode;
        this.child.uom = uom;
      }
    }
  };
}
