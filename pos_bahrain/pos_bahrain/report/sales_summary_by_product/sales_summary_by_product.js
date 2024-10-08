// Copyright (c) 2016, 	9t9it and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales summary by product"] = {
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
      fieldname: 'branches',
      label: __('Branch'),
      fieldtype: 'Link',
      options: 'Warehouse',
    },
    {
      fieldname: 'report_type',
      label: __('Report Type'),
      fieldtype: 'Select',
      options: ['Achieved','Collected'],
      default : 'Collected',
    },
  ],
};
// frappe.query_reports['Sales summary by product'] =
//   pos_bahrain.reports.sales_summary_by_product;