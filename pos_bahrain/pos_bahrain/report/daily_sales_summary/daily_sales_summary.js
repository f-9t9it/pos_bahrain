// Copyright (c) 2016, 	9t9it and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports['Daily Sales Summary'] = {
  filters: [
    {
      fieldname: 'from_date',
      label: __('From Date'),
      fieldtype: 'Date',
      default: frappe.datetime.add_days(
        frappe.datetime.add_months(frappe.datetime.get_today(), -1),
        1
      ),
    },
    {
      fieldname: 'to_date',
      label: __('To Date'),
      fieldtype: 'Date',
      default: frappe.datetime.get_today(),
    },
    {
      fieldname: 'company',
      label: __('Company'),
      fieldtype: 'Link',
      options: 'Company',
      default: frappe.defaults.get_user_default('Company')
    },
    {
	fieldname:'warehouse',
	label: __('Warehouse'),
	fieldtype: 'MultiSelectList',
	options: 'Warehouse',
	get_data: function(txt) {
	return frappe.db.get_link_options('Warehouse', txt,{
	company: frappe.query_report.get_filter_value("company")
        });
			}
		},
  ],
};
