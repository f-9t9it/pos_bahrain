// Copyright (c) 2024, 	9t9it and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Report"] = {
	"filters": [
		{
			"fieldname": 'company',
			"label": "The Company Name",
			"fieldtype":"Link",
			"options":"Company",
			"default": frappe.defaults.get_user_default('company')
		},
		{
			"fieldname":"item_code",
			"label":"Item Code",
			"fieldtype":"Link",
			"options":"Item",

		},
		{
			"fieldname":"warehouse",
			"label":"Warehouse",
			"fieldtype":"Link",
			"options":"Warehouse",
			
		}
	]
};


