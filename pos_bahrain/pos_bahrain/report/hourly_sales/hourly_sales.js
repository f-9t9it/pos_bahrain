// Copyright (c) 2016, 	9t9it and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports['Hourly Sales'] = {
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
      fieldname: 'start_time',
      label: __('Start Time'),
      fieldtype: 'Time',
      width: '80',
      default: '00:00:00',
    },
    {
      fieldname: 'end_time',
      label: __('End Time'),
      fieldtype: 'Time',
      width: '80',
      default: '23:59:59',
    },
    {
      fieldname: 'sales_option',
      label: __('Sales Option'),
      fieldtype: 'Select',
      width: '80',
      options: [
        'All',
        'POS Sales',
        'Invoice Sales',
      ],
      default: 'All',
    },
    {
      fieldname: 'cost_centers',
      label: __('Cost Centers'),
      fieldtype: 'MultiSelect',
      get_data: function() {
        const names = frappe.query_report.get_filter_value('cost_centers') || '';
        const values = names.split(/\s*,\s*/).filter(d => d);
        const txt = names.match(/[^,\s*]*$/)[0] || '';
        let data = [];
        frappe.call({
          type: 'GET',
          method: 'frappe.desk.search.search_link',
          async: false,
          no_spinner: true,
          args: {
            doctype: 'Cost Center',
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
  ],
};
