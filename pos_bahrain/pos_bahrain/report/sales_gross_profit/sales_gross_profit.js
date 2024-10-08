// Copyright (c) 2016, 	9t9it and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Gross Profit"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_start()
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_end()
		},

	],
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname == "outstanding" && data && data.outstanding > 0 ) {
			value = "<span style='color:red'>" + value + "</span>";
			// var $value = $(value).css("background-color", "red");;
			// value = $value.wrap("<p></p>").parent().html();
		}
		return value;
	}
};
