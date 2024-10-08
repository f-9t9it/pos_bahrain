// Copyright (c) 2016, 	9t9it and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports['Batch-wise Expiry Report'] = {
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
      fieldname: 'warehouse',
      label: __('Warehouse'),
      fieldtype: 'Link',
      options: 'Warehouse',
    },
    {
      fieldname: 'query_date',
      label: __('Query Date'),
      fieldtype: 'Date',
      default: frappe.datetime.get_today(),
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
