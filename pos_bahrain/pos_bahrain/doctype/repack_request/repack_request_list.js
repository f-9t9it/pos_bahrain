frappe.listview_settings['Repack Request'] = {
	get_indicator: function(doc) {
		const status_color = {
			"Draft": "grey",
			"Pending": "orange",
			"Completed": "green",
			"Stopped": "red",
		};
		return [__(doc.status), status_color[doc.status], "status,=,"+doc.status];
	},
};
