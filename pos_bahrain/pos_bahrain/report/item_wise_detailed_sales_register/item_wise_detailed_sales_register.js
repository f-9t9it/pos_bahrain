// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Item wise detailed sales register"] = {
	"filters": [
		{
			"fieldname": "date_range",
			"label": __("Date Range"),
			"fieldtype": "DateRange",
			"default": [frappe.datetime.add_months(frappe.datetime.get_today(),-1), frappe.datetime.get_today()],
			"reqd": 1
		},
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname": "mode_of_payment",
			"label": __("Mode of Payment"),
			"fieldtype": "Link",
			"options": "Mode of Payment"
		},
		{
			"fieldname": "warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse"
		},
		{
			"fieldname": "brand",
			"label": __("Brand"),
			"fieldtype": "Link",
			"options": "Brand"
		},
		{
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group"
		},
		{
			"fieldname": "pb_sales_employee",
			"label": __("Sales Employee"),
			"fieldtype": "Link",
			"options": "Employee",
		},
		{
			"fieldname": "pb_discount_percentage",
			"label": __("Discount (%)"),
			"fieldtype": "Percent",
		},
		{
			"label": __("Group By"),
			"fieldname": "group_by",
			"fieldtype": "Select",
			"options": ["Customer Group", "Customer", "Item Group", "Item", "Territory", "Invoice"]
		},
		{
			fieldname: 'supplier',
			label: __('Default Supplier'),
			fieldtype: 'Link',
			options: 'Supplier',
		},
		{
			"label": __("Show only discounted sales"),
			"fieldname": "show_only_discounted_sales",
			"fieldtype": "Check"
		},
		{
			"label": __("Show buying price"),
			"fieldname": "show_buying_price",
			"fieldtype": "Check"
		}
	],
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (data && data.bold) {
			value = value.bold();

		}
		return value;
	}
}