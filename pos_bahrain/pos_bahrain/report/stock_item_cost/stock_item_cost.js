// Copyright (c) 2016, 	9t9it and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Item Cost"] = {
	"filters": [
        {
          fieldname: 'company',
          label: __('Company'),
          fieldtype: 'Link',
          options: 'Company',
          default: frappe.defaults.get_user_default('Company'),
          reqd: 1,
        },
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
        }
	]
}
