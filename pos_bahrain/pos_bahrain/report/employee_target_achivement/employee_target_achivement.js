// Copyright (c) 2024, 	9t9it and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Target Achivement"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_start(),
			reqd: 1,

		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_end(),
			reqd: 1,
		},
		{
			fieldname: 'company',
			label: __('Company'),
			fieldtype: 'Link',
			options: 'Company',
			reqd: 1,
		},
		{
			fieldname: 'calculation_based_on',
			label: __('Calculation Based On'),
			fieldtype: 'Select',
			options: 'Sales Order\nSales Invoice',
			reqd: 1,
		},
		
		{
			fieldname: 'country',
			label: __('Country'),
			fieldtype: 'Link',
			options: 'Country',
		},
		{
			"fieldname": "show_variance",
			"label": "Show Variance",
			"fieldtype": "Check",
			"default": 0
		},
	]
	
};

