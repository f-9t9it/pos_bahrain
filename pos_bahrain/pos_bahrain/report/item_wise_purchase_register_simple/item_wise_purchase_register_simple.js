// Copyright (c) 2016, 	9t9it and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports['Item-wise Purchase Register Simple'] = {
  filters: [
    {
      fieldname: 'date_range',
      label: __('Date Range'),
      fieldtype: 'DateRange',
      default: [
        frappe.datetime.add_months(frappe.datetime.get_today(), -1),
        frappe.datetime.get_today(),
      ],
      reqd: 1,
    },
    {
      fieldname: 'supplier',
      label: __('Supplier'),
      fieldtype: 'Link',
      options: 'Supplier',
    },
    {
      fieldname: 'company',
      label: __('Company'),
      fieldtype: 'Link',
      options: 'Company',
      default: frappe.defaults.get_user_default('Company'),
      reqd: 1,
    },
    {
      fieldname: 'warehouse',
      label: __('Warehouse'),
      fieldtype: 'Link',
      options: 'Warehouse',
      get_query: { filters: { is_group: 0 } },
    },
    {
      fieldname: 'item_group',
      label: __('Item Group'),
      fieldtype: 'Link',
      options: 'Item Group',
      get_query: { filters: { is_group: 0 } },
    },
    {
      fieldname: 'item_code',
      label: __('Item Code'),
      fieldtype: 'Link',
      options: 'Item',
    },
    {
      fieldname: 'item_name',
      label: __('Item Name'),
      fieldtype: 'Data',
    },
  ],
};
