// Copyright (c) 2018, 	9t9it and contributors
// For license information, please see license.txt

frappe.ui.form.on('POS Closing Voucher', {
  onload: async function (frm) {
    const { period_to = frappe.datetime.now_datetime() } =
      frappe.route_options || {};
    if (frm.doc.docstatus === 0 && !frm.doc.period_to) {
      frm.set_value('period_to', period_to);
    }
    [
      'payments',
      'invoices',
      'returns',
      'taxes',
      'employees',
      'item_groups',
      'pcv_pe_table'
    ].forEach((field) => {
      frm.set_df_property(field, 'read_only', 1);
    });
  },
  refresh: function (frm) {
    if (frm.doc.docstatus === 0) {
      frm.add_custom_button('Fetch Invoices', function () {
        frm.trigger('set_report_details');
      });
    }
  },
  before_submit(frm) {
    const unsynced_docs = (
      JSON.parse(localStorage.getItem('sales_invoice_doc')) || []
    ).filter((x) => {
      const { docstatus } = Object.values(x)[0];
      return docstatus === 1;
    });
    if (unsynced_docs.length > 0) {
      frappe.throw(
        __(
          `${unsynced_docs.length} unsynced invoices present. Please resolve conflicts and try again.`
        )
      );
    }
    localStorage.setItem('sales_invoice_doc', '[]');
  },
  user: function (frm) {
    frm.trigger('set_report_details');
  },
  pos_profile: async function (frm) {
    const { pos_profile } = frm.doc;
    if (pos_profile) {
      const { message: { company } = {} } = await frappe.db.get_value(
        'POS Profile',
        pos_profile,
        'company'
      );
      frm.set_value('company', company);
    }
    frm.trigger('set_report_details');
  },
  period_from: function (frm) {
    frm.trigger('set_report_details');
  },
  period_to: function (frm) {
    frm.trigger('set_report_details');
  },
  set_report_details: async function (frm) {
    const { pos_profile, period_from } = frm.doc;
    if (pos_profile && period_from) {
      await frappe.call({
        method: 'set_report_details',
        doc: frm.doc,
      });
      frm.refresh();
      frm.trigger('set_closing_amount');
    }
  },
  opening_amount: function (frm) {
    frm.trigger('set_closing_amount');
  },
  set_closing_amount: function (frm) {
    const { opening_amount } = frm.doc;
    const { collected_amount = 0 } =
      frm.doc.payments.find(({ is_default }) => is_default === 1) || {};
    frm.set_value('closing_amount', opening_amount + collected_amount);
  },
});

frappe.ui.form.on('POS Voucher Payment', {
  collected_amount: async function (frm, cdt, cdn) {
    const {
      collected_amount,
      expected_amount,
      mop_conversion_rate,
      is_default,
    } = frappe.get_doc(cdt, cdn);
    frappe.model.set_value(
      cdt,
      cdn,
      'difference_amount',
      collected_amount - expected_amount
    );
    frappe.model.set_value(
      cdt,
      cdn,
      'base_collected_amount',
      collected_amount * flt(mop_conversion_rate)
    );
    if (is_default) {
      frm.trigger('set_closing_amount');
    }
  },
});
