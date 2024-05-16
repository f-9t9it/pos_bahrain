// Copyright (c) 2016, 	9t9it and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Zero Stock Report"] = {
	"filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 1
        },
		{
            "fieldname": "date",
            "label": __("Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "item",
            "label": __("Item"),
            "fieldtype": "Link",
            "options":"Item",
        },
		{
            "fieldname": "item_group",
            "label": __("Item Group"),
            "fieldtype": "Link",
            "options":"Item Group",
        },
		{
            "fieldname": "warehouse",
            "label": __("Warehouse"),
            "fieldtype": "Link",
            "options":"Warehouse",
        },
		{
            "fieldname": "show_item_in_stock",
            "label": __("Show item in stock"),
            "fieldtype": "Check",
        },

	]
};
