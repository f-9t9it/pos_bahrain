import first from 'lodash/first';
import mapValues from 'lodash/mapValues';
import keyBy from 'lodash/keyBy';

function reduce_values_by(key, items) {
  return mapValues(items, values => keyBy(values, key));
}

export default function withUom(Pos) {
  return class PosExtended extends Pos {
    async init_master_data(r, freeze) {
      const pos_data = await super.init_master_data(r, freeze);
      const { uom_details, item_prices } = pos_data;
      if (!uom_details) {
        frappe.msgprint({
          indicator: 'orange',
          title: __('Warning'),
          message: __('Unable to load UOM details. Usage will be restricted.'),
        });
      }
      this.uom_details = uom_details;
      this.item_prices_by_uom = mapValues(item_prices, values =>
        keyBy(values, 'uom')
      );
      return pos_data;
    }
    add_new_item_to_grid() {
      super.add_new_item_to_grid();
      const { stock_uom, conversion_factor = 1 } = first(this.items) || {};
      Object.assign(this.child, { uom: stock_uom, conversion_factor });
    }
    _set_item_price_from_uom(item_code, uom) {
      const item = this.frm.doc.items.find(x => x.item_code === item_code);
      const uom_details = this.uom_details[item_code].find(x => x.uom === uom);
      if (item && uom_details) {
        const { conversion_factor = 1 } = uom_details;
        const {
          price_list_rate = this.price_list_data[item_code],
        } = this.item_prices_by_uom[item_code][uom];
        Object.assign(item, {
          uom,
          conversion_factor,
          rate: price_list_rate,
          price_list_rate,
          amount: flt(item.qty) * price_list_rate,
        });
        this.update_paid_amount_status(false);
      }
    }
    render_selected_item() {
      super.render_selected_item();
      $(`
        <div class="pos-list-row">
          <div class="cell">${__('UOM')}:</div>
          <select type="text" class="form-control cell pos-item-uom" />
        </div>
      `).prependTo(this.wrapper.find('.pos-selected-item-action'));
      const $select = this.wrapper.find('.pos-item-uom').off('change');
      const selected_item = this.frm.doc.items.find(
        ({ item_code }) => this.item_code === item_code
      );
      this.uom_details[this.item_code].forEach(({ uom }) => {
        $('<option />', {
          value: uom,
          selected: selected_item && uom === selected_item.uom,
        })
          .text(`${uom}`)
          .appendTo($select);
      });
      $select.on('change', e => {
        e.stopPropagation();
        this._set_item_price_from_uom(this.item_code, e.target.value);
        this.render_selected_item();
      });
    }
  };
}
