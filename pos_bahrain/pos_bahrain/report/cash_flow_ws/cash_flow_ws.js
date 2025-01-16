// Copyright (c) 2016, 	9t9it and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Cash Flow WS"] = {
	"filters": [
		{
			fieldname: 'from_date',
			label: __('From Date'),
			fieldtype: 'Date',
			reqd: 1,
			default:frappe.datetime.month_start(),
		  },
		  {
			fieldname: 'to_date',
			label: __('To Date'),
			fieldtype: 'Date',
			reqd: 1,
			default:frappe.datetime.month_end(),
		  },
		  {
			fieldname: 'support_amount',
			label: __('Support Amount'),
			fieldtype: 'Currency',
		  },
		  {
			fieldname: 'estimated',
			label: __('Estimated Sales %'),
			fieldtype: 'Percent',
		  },
	]
};
