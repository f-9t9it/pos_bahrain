// Copyright (c) 2016, 	9t9it and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Item-wise Sales"] = {
	"filters": [
		_make_filter('posting_date', 'Posting Date', 'Date', frappe.datetime.now_date())
	]
};

function _make_filter(key, label, type, def) {
	return {
		label: __(label),
		fieldname: key,
		fieldtype: type,
		default: def
	};
}
