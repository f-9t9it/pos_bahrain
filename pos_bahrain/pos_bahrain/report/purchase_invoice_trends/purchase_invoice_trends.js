// Copyright (c) 2016, 	9t9it and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.require("assets/erpnext/js/purchase_trends_filters.js", function() {
	frappe.query_reports["Purchase Invoice Trends"] = {
		filters: erpnext.get_purchase_trends_filters()
	}
});
