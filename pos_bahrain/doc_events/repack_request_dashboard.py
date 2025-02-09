import frappe
from frappe import _

def get_data(**kwargs):
    return {
        "fieldname": "pb_repack_request",
        "transactions": [
            {
                "label": _("Stock Transactions"),
                "items": ["Stock Entry"]
            }
        ]
    }
