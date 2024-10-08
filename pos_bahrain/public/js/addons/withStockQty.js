export default function withStockQty(Pos) {
  return class PosExtended extends Pos {
    submit_invoice() {
      super.submit_invoice();
      this._update_stock_qty();
    }
    _update_stock_qty() {
      const me = this;
      $.each(this.frm.doc.items || [], function (i, item) {
        const bin_data = me.bin_data[item.item_code];
        if (bin_data) {
          const bin_qty = bin_data[item.warehouse];
          const qty = item.qty * item.conversion_factor;
          me.bin_data[item.item_code][item.warehouse] = bin_qty - qty;
          const batch_details = me.batch_no_details[item.item_code];
          const batch_detail = batch_details.find(batch => batch.name === item.batch_no);
          if (batch_detail) {
            batch_detail.qty = batch_detail.qty - qty;
          }
        }
      });
      this.items = this.get_items();
      this.make_item_list();
    }
  };
}
