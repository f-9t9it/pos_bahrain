import first from 'lodash/first';
import mapValues from 'lodash/mapValues';
import keyBy from 'lodash/keyBy';
import get from 'lodash/get';

// depends on withIdx, withExtendedItemPrice
export default function withUom(Pos) {
  return class PosExtended extends Pos {
    _set_item_price_from_uom(item_code, uom) {
      const item = this._get_active_item_ref_from_doc();
      const uom_details = this.uom_details[item_code].find(x => x.uom === uom);
      if (item && uom_details) {
        const { conversion_factor = 1 } = uom_details;
        const { customer, posting_date: transaction_date } = this.frm.doc;
        const { qty: min_qty } = item;
        const price_list_rate = this.get_item_price({
          item_code,
          uom,
          customer,
          min_qty,
          transaction_date,
        });
        Object.assign(item, {
          uom,
          conversion_factor,
          rate: price_list_rate,
          price_list_rate,
          amount: flt(item.qty * price_list_rate, this.precision),
        });
        this.update_paid_amount_status(false);
      }
    }
    _get_active_item_ref_from_doc() {
      return this.frm.doc.items[this.selected_cart_idx];
    }
    render_selected_item() {
      super.render_selected_item();
      $(`
        <div class="pos-list-row">
          <div class="cell">${__('UOM')}:</div>
          <select type="text" class="form-control cell pos-item-uom" />
        </div>
      `).prependTo(this.wrapper.find('.pos-selected-item-action'));
      const $select = this.wrapper.find('.pos-item-uom');
      const selected_item = this._get_active_item_ref_from_doc();
      this.uom_details[unescape(this.item_code)].forEach(({ uom }) => {
        $('<option />', {
          value: uom,
          selected: selected_item && uom === selected_item.uom,
        })
          .text(`${uom}`)
          .appendTo($select);
      });
      $select.on('change', e => {
        e.stopPropagation();
        this._set_item_price_from_uom(unescape(this.item_code), e.target.value);
        this.render_selected_item();
      });
    }
  };
}
