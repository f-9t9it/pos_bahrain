// Copyright (c) 2024, 	9t9it and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Supplier Target Achivement"] = {
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
			fieldname: 'supplier',
			label: __('Supplier'),
			fieldtype: 'Link',
			options: 'Supplier',
			reqd: 1,
		},
		
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "MultiSelectList",
			options: "Company",
			default:"Analytica One Medical Company",
			reqd: 1,
			get_data: function(txt) {
				return frappe.db.get_link_options("Company", txt)
			},
		},
		{
			"fieldname": "show_variance",
			"label": "Show Variance",
			"fieldtype": "Check",
			"default": 0
		},

	],
	 
	
};
