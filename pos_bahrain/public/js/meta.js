if (frappe.boot.pos_bahrain.disable_standard_pf) {
  const _existing_print_formats = frappe.meta.get_print_formats;
  frappe.meta.get_print_formats = function (doctype) {
    const print_formats = _existing_print_formats(doctype);
    return print_formats.filter((print_format) => print_format !== "Standard");
  }
}
