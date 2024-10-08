import get from 'lodash/get';

function searchByUOM(args) {
  return ({ uom }) => [uom, null].includes(args.uom);
}

function searchByCustomer(args) {
  return ({ customer }) =>
    args.hasOwnProperty('customer') ? customer === args.customer : !customer;
}

function searchByMinQty(args) {
  return ({ min_qty }) =>
    args.hasOwnProperty('min_qty') ? (min_qty || 0) <= args.min_qty : true;
}

function searchByTransactionDate(args) {
  return ({ valid_from, valid_upto }) => {
    if (!args.hasOwnProperty('transaction_date')) {
      return true;
    }
    const transaction_date = new frappe.datetime.datetime(
      args.transaction_date
    );
    return transaction_date.moment.isBetween(
      valid_from || '2000-01-01',
      valid_upto || '2100-12-31'
    );
  };
}

// depends on withBase
export default function withExtendedItemPrice(Pos) {
  return class PosExtended extends Pos {
    onload() {
      super.onload();
      this.precision =
        frappe.defaults.get_default('currency_precision') ||
        frappe.defaults.get_default('float_precision');
    }
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
      this.detailed_item_prices = item_prices;
      this.uom_details = uom_details;
      return pos_data;
    }
    add_new_item_to_grid() {
      super.add_new_item_to_grid();
      const { customer, posting_date: transaction_date } = this.frm.doc;
      const { item_code, stock_uom: uom, qty: min_qty } = this.child;
      const rate = this.get_item_price({
        item_code,
        uom,
        customer,
        min_qty,
        transaction_date,
      });
      Object.assign(this.child, {
        rate,
        price_list_rate: rate,
      });
    }
    _get_price(args) {
      const [price, ...rest] = get(
        this.detailed_item_prices,
        args.item_code,
        []
      )
        .filter(searchByUOM(args))
        .filter(searchByCustomer(args))
        .filter(searchByMinQty(args))
        .filter(searchByTransactionDate(args));
      return price;
    }
    get_item_price({
      item_code,
      uom = null,
      customer = null,
      min_qty = 1,
      transaction_date = null,
    }) {
      if (!item_code) {
        frappe.throw(
          __('<code>get_item_price</code> requires <em>item_code</em>')
        );
      }

      // using new core fields like uom, customer, min_qty and transaction_date
      const prices =
        this._get_price({
          item_code,
          uom,
          customer,
          min_qty,
          transaction_date,
        }) || this._get_price({ item_code, uom, transaction_date });
      const { conversion_rate } = this.frm.doc;
      if (prices && prices.price_list_rate) {
        return prices.price_list_rate;
      }

      const conversion_factor = uom
        ? this.get_conversion_factor({ item_code, uom })
        : 1;

      // using older customer-wise price list
      const customer_price_list = this.customer_wise_price_list[
        this.frm.doc.customer
      ];
      if (customer_price_list && customer_price_list[item_code]) {
        return (
          flt(
            customer_price_list[item_code] * conversion_factor,
            this.precision
          ) / flt(conversion_rate, this.precision)
        );
      }

      // fallback to use core item price based on just stock uom
      return (
        flt(
          this.price_list_data[item_code] * conversion_factor,
          this.precision
        ) / flt(conversion_rate, this.precision)
      );
    }
    get_conversion_factor({ item_code, uom }) {
      const { conversion_factor = 1 } =
        this.uom_details[item_code].find(x => x.uom === uom) || {};
      return conversion_factor;
    }
  };
}
