frappe.ui.form.on("Print Format", {
  refresh: function (frm) {
    _create_disable_btn(frm);
  },
});


function _create_disable_btn(frm) {
  frm.add_custom_button(__('Toggle Disabled'), function () {
    frappe.call({
      method: 'pos_bahrain.api.print_format.toggle_disable_print_format',
      args: { name: frm.doc.name },
      callback: function (res) {
        const { message: disabled } = res;
        frm.reload_doc();
      },
    });
  });
}
