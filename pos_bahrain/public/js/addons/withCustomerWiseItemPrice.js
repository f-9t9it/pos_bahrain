import mapValues from 'lodash/mapValues';
import groupBy from 'lodash/groupBy';
import get from 'lodash/get';
import keyBy from 'lodash/keyBy';
import merge from 'lodash/merge';

export default function withCustomerWiseItemPrice(Pos) {
  return class PosExtended extends Pos {
    async init_master_data(r, freeze) {
      const pos_data = await super.init_master_data(r, freeze);
      const { item_prices } = pos_data;

      const customer_wise_price_list = mapValues(
        groupBy(
          Object.values(item_prices)
            .flat()
            .filter(({ customer }) => !!customer),
          'customer'
        ),
        values =>
          mapValues(
            keyBy(values, 'item_code'),
            ({ price_list_rate }) => price_list_rate
          )
      );
      this.customer_wise_price_list = merge(
        this.customer_wise_price_list,
        customer_wise_price_list
      );
      this.make_item_list(this.default_customer);
      return pos_data;
    }
  };
}
