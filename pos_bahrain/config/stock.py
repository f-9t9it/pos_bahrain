from frappe import _


def get_data():
    return [
        {
            "label": _("Stock Transactions"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Stock Transfer",
                    "onboard": 1,
                    "dependencies": ["Item"],
                },
            ],
        },
    ]
