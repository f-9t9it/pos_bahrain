function handle_onload(frm) {
  handle_price_list_fields(frm);
  handle_daily_email(frm);
}

function handle_price_list_fields(frm) {
  const { discount_on_retail } = frm.doc;
  frm.toggle_reqd(
    ['retail_price_list', 'wholesale_price_list'],
    discount_on_retail
  );
}

function handle_daily_email(frm) {
  const { use_daily_email } = frm.doc;
  frm.set_df_property('manager_email', 'disabled', !use_daily_email);
}

export default {
  onload: handle_onload,
  setup: function (frm) {
    frm.set_query('account', 'vat_tax_categories', {
      filters: { account_type: 'Tax', is_group: 0 },
    });
  },
  discount_on_retail: handle_price_list_fields,
  use_daily_email: handle_daily_email,
  valuation_price_list: function (frm) {
    const { valuation_price_list } = frm.doc;
    frm.toggle_reqd('valuation_warehouse', !!valuation_price_list);
    if (!valuation_price_list) {
      frm.set_value('valuation_warehouse', null);
    }
  },
};
