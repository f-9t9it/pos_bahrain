async function set_invoice_date(frm, cdt, cdn) {
  const { reference_doctype, reference_name } = frappe.get_doc(cdt, cdn) || {};
  if (reference_name) {
    const date_field = ['Sales Order', 'Purchase Order'].includes(
      reference_doctype
    )
      ? 'transaction_date'
      : 'posting_date';
    const { message: doc = {} } = await frappe.db.get_value(
      reference_doctype,
      reference_name,
      date_field
    );
    return frappe.model.set_value(cdt, cdn, 'pb_invoice_date', doc[date_field]);
  }
}

const payment_entry_reference = {
  refresh: set_invoice_date,
  reference_name: set_invoice_date,
};

export default {
  payment_entry_reference,
};
