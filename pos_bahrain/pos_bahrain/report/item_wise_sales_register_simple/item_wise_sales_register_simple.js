// Copyright (c) 2016, 	9t9it and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports['Item-wise Sales Register Simple'] = {
  filters: [
    {
      fieldname: 'from_date',
      label: __('From Date'),
      fieldtype: 'Date',
      width: '80',
      reqd: 1,
      default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
    },
    {
      fieldname: 'to_date',
      label: __('To Date'),
      fieldtype: 'Date',
      width: '80',
      reqd: 1,
      default: frappe.datetime.get_today(),
    },
    {
      fieldname: 'customer',
      label: __('Customer'),
      fieldtype: 'Link',
      options: 'Customer',
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
