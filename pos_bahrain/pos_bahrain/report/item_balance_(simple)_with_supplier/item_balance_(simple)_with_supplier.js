// Copyright (c) 2016, 	9t9it and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports['Item Balance (Simple) with Supplier'] = {
  filters: [
    {
      fieldname: 'company',
      label: __('Company'),
      fieldtype: 'Link',
      options: 'Company',
      reqd: 1,
      default: frappe.defaults.get_user_default('company'),
    },
    {
      fieldname: 'item_codes',
      label: __('Items'),
      fieldtype: 'MultiSelect',
      get_data: function() {
        const names = frappe.query_report.get_filter_value('item_codes') || '';
        const values = names.split(/\s*,\s*/).filter(d => d);
        const txt = names.match(/[^,\s*]*$/)[0] || '';
        let data = [];
        frappe.call({
          type: 'GET',
          method: 'frappe.desk.search.search_link',
          async: false,
          no_spinner: true,
          args: {
            doctype: 'Item',
            txt: txt,
            filters: { name: ['not in', values] },
          },
          callback: function({ results }) {
            data = results;
          },
        });
        return data;
      },
    },
    {
      fieldname: 'warehouse',
      label: __('Warehouse'),
      fieldtype: 'Link',
      options: 'Warehouse',
      get_query: { filters: { is_group: 0 } },
    },
    {
      fieldname: 'hide_zero_stock',
      label: __('Hide Zero Stock'),
      fieldtype: 'Check',
    },
    {
      fieldname: 'show_alt_uoms',
      label: __('Show Alternate UOMs'),
      fieldtype: 'Check',
    },
  ],
};
