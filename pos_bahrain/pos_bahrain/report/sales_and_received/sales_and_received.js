frappe.query_reports["Sales and Received"] = {
	"filters": [
		{
			"fieldname": "calculation_based_on",
			"label": __("Calculation Based On"),
			"fieldtype": "Select",
			"options": 'Sales Order\nSales Invoice',
			"default": "Sales Order",
			"reqd": 1,
		},
		{
			"fieldname": "report_type",
			"label": __("Report Type"),
			"fieldtype": "Select",
			"options": 'Yearly',
			"default": "Yearly",
			"reqd": 1,
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.year_start(),
			"reqd": 1,
			"depends_on": "eval: doc.report_type == 'Date Range'"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.year_end(),
			"reqd": 1,
			"depends_on": "eval: doc.report_type == 'Date Range'"
		},
		{
			"fieldname": "year",
			"label": __("Year"),
			"fieldtype": "Select",
			"options": get_years(),
			"default": new Date().getFullYear(),
			"reqd": 0,
			"depends_on": "eval: doc.report_type == 'Yearly'"
		}
	]
};

function get_years() {
    var currentYear = new Date().getFullYear();
    var years = [];
    
    for (var year = currentYear; year >= 2010; year--) {
        years.push(year);
    }
    
    return years.join("\n");
}
