// Copyright (c) 2016, 	9t9it and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Product Purchase Summary"] = {
	"filters": [
		{
			"fieldname": "start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.get_today(),
					},
					{
			"fieldname": "end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.get_today(),
					},
				{
					"fieldname": "company",
					"label": __("Company"),
					"fieldtype": "Link",
					"reqd": 1,
					"options":"Company",
					"default":frappe.defaults.get_user_default("Company")
							},
							{
					"fieldname": "warehouse",
					"label": __("Warehouse"),
					"fieldtype": "Link",
					"options":"Warehouse"
							},
	]
};
