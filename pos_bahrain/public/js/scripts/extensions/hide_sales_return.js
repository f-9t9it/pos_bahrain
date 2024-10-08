export default async function(name, group) {
  const { message: data } = await frappe.call({
    method: 'pos_bahrain.api.pos_bahrain_settings.hide_sales_return',
  });
  if (data && !frappe.user.has_role(data)) {
    setTimeout(() => {
      const encoded_text = encodeURIComponent(name);
      const query = ".btn-group[data-label='" + group +"'] li > a[data-label='" + encoded_text + "']";
      $(query).hide();
    }, 600);
  }
}
