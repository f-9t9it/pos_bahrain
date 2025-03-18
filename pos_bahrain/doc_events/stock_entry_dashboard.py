from __future__ import unicode_literals
from frappe import _

def get_data(data):
    return {
        "fieldname": "stock_entry",  
        "non_standard_fieldnames": {
            "Material Request": "name",
            "Purchase Receipt": "name"
        },
        "internal_links": {
            "Material Request": ["items", "material_request"],
            "Purchase Receipt": ["items", "reference_purchase_receipt"]
        },
        "transactions": [
            {
                "label": _("Reference"),
                "items": [
                    "Material Request",
                    "Purchase Receipt",
                    "Repack Request"
                ]
            }
        ]
    }
