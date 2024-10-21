// Copyright (c) 2024, 	9t9it and contributors
// For license information, please see license.txt
/* eslint-disable */
 
frappe.require("assets/erpnext/js/financial_statements.js", function () {
	frappe.query_reports["Profit & Loss Detailed Report"] = $.extend({}, erpnext.financial_statements);

	erpnext.utils.add_dimensions("Profit & Loss Detailed Report", 10);

	// frappe.query_reports["Profit & Loss Detailed Report"]["filters"].push({
	// 	fieldname: "selected_view",
	// 	label: __("Select View"),
	// 	fieldtype: "Select",
	// 	options: [
	// 		{ value: "Report", label: __("Report View") },
	// 		{ value: "Growth", label: __("Growth View") },
	// 		{ value: "Margin", label: __("Margin View") },
	// 	],
	// 	default: "Report",
	// 	reqd: 1,
	// });
	 
});
