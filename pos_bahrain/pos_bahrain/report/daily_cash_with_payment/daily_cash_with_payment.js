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
			on_change: function() {
				if (frappe.query_report.get_filter("query_doctype").get_value() === "Warehouse") {
					frappe.db.get_list('User Permission', {
						filters: {
							user: frappe.session.user,
							applicable_for: 'Sales Invoice',
							allow:"Warehouse"
						},
						fields: ['for_value']
					}).then(user_permissions => {
						const allowed_warehouses = user_permissions.map(perm => perm.for_value);
						if (allowed_warehouses.length > 0)
						{
							frappe.query_report.get_filter('query_doc').df.get_query = () => {
							return {
								filters: {
									name: ['in', allowed_warehouses]
								}
							};
						};
						}
						
					});
				}
			}
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
		{
			fieldname: 'restrict_from_date',
			label: __('	Allow From Date More Than 3 Days'),
			fieldtype: 'Check',
			hidden: !frappe.user.has_role('Daily Cash Report Manager'),
			
		},
		{
			fieldname: 'edit_from_date',
			label: __('Edit date'),
			fieldtype: 'Check',
			hidden: !frappe.user.has_role('Daily Cash Report Manager'),
			on_change: function () {
                let filter_date = frappe.query_report.get_filter("from_date");
                let edit_check = frappe.query_report.get_filter("edit_from_date").get_value();
				
				console.log(edit_check)
                if (edit_check) {
					console.log(edit_check)
                    filter_date.df.read_only = 0; // Make date editable
                } else {
                    filter_date.df.read_only = 1; // Lock the date field
                    filter_date.set_value(frappe.datetime.add_days(frappe.datetime.get_today(), 3));
                }
                
				filter_date.refresh()
            }
		},
	]
}
