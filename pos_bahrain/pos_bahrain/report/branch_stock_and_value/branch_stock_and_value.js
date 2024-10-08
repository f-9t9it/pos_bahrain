// Copyright (c) 2016, 9T9IT and contributors
// For license information, please see license.txt
/* eslint-disable */
frappe.query_reports["Branch Stock And Value"] = {
	  "filters": [
                {
                        "fieldname": "include_uom",
                        "label": __("Include UOM"),
                        "fieldtype": "Link",
                        "options":"UOM",
                        
                       
                },      
                {
                        "fieldname":"from_date",
                        "label": __("From Date"),
                        "fieldtype": "Date",
                        "width": "80",
                        "reqd": 1,
                        "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
                },
                {
                        "fieldname":"to_date",
                        "label": __("To Date"),
                        "fieldtype": "Date",
                        "width": "80",
                        "reqd": 1,
                        "default": frappe.datetime.get_today()
                },
                {
                        "fieldname": "item_group",
                        "label": __("Item Group"),
                        "fieldtype": "Link",
                        "width": "80",
                        "options": "Item Group"
                },
                {
                        "fieldname": "item_code",
                        "label": __("Item"),
                        "fieldtype": "Link",
                        "width": "80",
                        "options": "Item"
                },
                {
                        "fieldname": "warehouse",
                        "label": __("Warehouse"),
                        "fieldtype": "Link",
                        "width": "80",
                        "options": "Warehouse"
                },
                {
                        "fieldname": "filter_total_zero_qty",
                        "label": __("Filter Total Zero Qty"),
                        "fieldtype": "Check",
                        "default": 1
                },
               
        ]
}
