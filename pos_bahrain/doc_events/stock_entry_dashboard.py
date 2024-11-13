from __future__ import unicode_literals
from frappe import _


# Todo: non_standard_fieldnames is to be decided
def get_data(data):
	return {
		"fieldname": "stock_entry",
		"non_standard_fieldnames": {
			# "DocType Name": "Reference field name",
			"Repack Request":"name",
			"Material Request":"name",
			"Purchase Receipt":"name"
		},
		"internal_links": {
			"Material Request": ["items", "material_request"],
			"Purchase Receipt": ["items", "reference_purchase_receipt"],
			 
		},
		"transactions": [
			{
				"label": _("Reference"),
				"items": [
					"Material Request",
					"Purchase Receipt",
					 
					"Repack Request"
				],
			},
		],
	}
