async function show_prices(frm) {
    if (frm.doc.__islocal || !frappe.user_roles.includes('Accounts Manager')) {
      return;
    }
    const { item_code } = frm.doc;
    const { message: { selling_price, buying_price, selling_price_with_vat } = {} } = await frappe.call({
      method: 'pos_bahrain.api.item.get_standard_prices',
      args: { item_code },
    });
  
  
    const section = frm.dashboard.add_section(
      `<h5 style="margin-top: 0px;">${__('Standard Prices')}</h5>`
    ).append(`
      <div class="row">
        <div class="col-xs-4 small">
          ${__('Standard Selling')}: ${format_currency(selling_price)}
        </div>
        <div class="col-xs-4 small">
          ${__('Standard Buying')}: ${format_currency(buying_price)}
        </div>
        <div class="col-xs-4 small">
          ${__('Standard Margin')}: ${
            selling_price
              ? (((selling_price - (buying_price || 0)) / selling_price) * 100).toFixed(2) + '%'
              : 'N/A'
          }
        </div>
        <div class="col-xs-4 small">
          ${__('Selling Price with VAT')}: ${format_currency(selling_price_with_vat)}
        </div>
      </div>
    `);
  }
  
  

async function hide_storage_location(frm) {
  const use_item_storage_location = await frappe.db.get_single_value('POS Bahrain Settings', 'use_item_storage_location');
  if (!use_item_storage_location) {
    frm.set_df_property('pb_storage_location_sb', 'hidden', 1);
  }
}

export default {
  refresh: function(frm) {

    show_prices(frm);
    hide_storage_location(frm);
  },
};
