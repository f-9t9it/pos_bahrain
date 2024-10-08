export default function withDiscountValidator(Pos) {
  return class PosExtended extends Pos {
    validate() {
      super.validate();
      const {
        allow_user_to_edit_discount,
        pb_max_discount: profile_max_discount = 0,
      } = this.pos_profile_data;
      if (allow_user_to_edit_discount) {
        const { customer, posting_date: transaction_date } = this.frm.doc;
        this.frm.doc.items.forEach(
          ({ item_code, uom, net_amount = 0, qty, idx }) => {
            const { item_group, max_discount: item_max_discount = 0 } =
              this.item_data.find(x => x.item_code === item_code) || {};
            const max_discount = item_max_discount || profile_max_discount;
            const {discount_percentage = 0 } = this.pricing_rules.find(pricing_rule => pricing_rule.item_group === item_group) || {}
            if (max_discount) {
              const net_rate = net_amount / qty;
              const price = this.get_item_price({
                item_code,
                uom,
                customer,
                min_qty: qty,
                transaction_date,
              });
              const discount = (1 - net_rate / price) * 100;
              if (discount.toFixed(2) > max_discount && discount_percentage === 0) {
                frappe.throw(
                  __(
                    `Discount for row #${idx}: ${discount }% cannot be greater than ${max_discount}%`
                  )
                );
              }
            }
          }
        );
      }
    }
  };
}
