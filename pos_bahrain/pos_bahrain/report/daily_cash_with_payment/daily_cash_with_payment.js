// Copyright (c) 2016, 	9t9it and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Cash with Payment"] = {
	"filters": [
		{
			fieldname: 'from_date',
			label: __('From Date'),
			fieldtype: 'Date',
			reqd: 1,
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: 'to_date',
			label: __('To Date'),
			fieldtype: 'Date',
			reqd: 1,
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: 'query_doctype',
			label: __('Query By'),
			fieldtype: 'Link',
			options: 'DocType',
			get_query: { filters: [['name', 'in', ['POS Profile', 'Warehouse']]] },
			reqd: 1,
			only_select: 1,
			default: 'POS Profile',
		},
		{
			fieldname: 'query_doc',
			label: __('Query Document'),
			fieldtype: 'Dynamic Link',
			options: 'query_doctype',
			reqd: 1,
		},
		{
			fieldname: 'show_customer_info',
			label: __('Show Customer Info'),
			fieldtype: 'Check',
		},
		{
			fieldname: 'show_reference_info',
			label: __('Show Reference Info'),
			fieldtype: 'Check',
		},
		{
			fieldname: 'summary_view',
			label: __('Summary View'),
			fieldtype: 'Check'
		},
		{
			fieldname: 'show_creator',
			label: __('Show Creator'),
			fieldtype: 'Check'
		},
	]
}
