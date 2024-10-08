// Copyright (c) 2016, 	9t9it and contributors
// For license information, please see license.txt
/* eslint-disable */


frappe.query_reports["Cash Account"] = {
	"filters": [
		_make_filter('from_date', 'From Date', 'Date', frappe.datetime.month_start()),
		_make_filter('to_date', 'To Date', 'Date', frappe.datetime.month_end()),
		_make_filter('summary_view', 'Summary View', 'Check')
	]
};

function _make_filter(key, label, type, def) {
	return {
		fieldname: key,
		fieldtype: type,
		label: __(label),
		default: def
	};
}