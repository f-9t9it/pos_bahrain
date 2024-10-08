from frappe import _


def get_data():
    return [
        {
            "label": _("General Ledger"),
            "items": [
                {"type": "doctype", "name": "GL Payment", "label": _("GL Payment")}
            ],
        }
    ]
