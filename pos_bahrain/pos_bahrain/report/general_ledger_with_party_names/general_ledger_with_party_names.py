# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.accounts.report.utils import get_currency, convert_to_presentation_currency
from erpnext.accounts.report.general_ledger import general_ledger
from functools import reduce


def execute(filters=None):
    col, res = general_ledger.execute(filters)

    # Add new column to the existing General Ledger
    # insert after [index] + 1
    party_index = [i for i, d in enumerate(col) if "party" in d.values()][0]
    col.insert(
        party_index + 1,
        {"label": _("Party Name"), "fieldname": "party_name", "width": 180},
    )

    party_names = _get_party_names(res)
    for row in res:
        if row.get("party", None) in party_names:
            row["party_name"] = party_names[row.get("party")]

    return col, res


def _get_party_names(data):
    """
    Get [dict] of party names matched with name
    :param data:
    :return:
    """

    def make_list(party_type):
        return list(
            set(
                map(
                    lambda x: x["party"],
                    filter(lambda y: y.get("party_type", None) == party_type, data),
                )
            )
        )

    supplier_list = make_list("Supplier")
    suppliers = _make_dict(
        frappe.get_list(
            "Supplier",
            filters=[["name", "in", supplier_list]],
            fields=["name", "supplier_name"],
        ),
        "name",
        "supplier_name",
    )

    customer_list = list(filter(lambda x: x, make_list("Customer")))
    customers = _make_dict(
        frappe.get_all(
            "Customer",
            filters=[["name", "in", customer_list]],
            fields=["name", "customer_name"],
        ),
        "name",
        "customer_name",
    )

    return {**suppliers, **customers}


def _make_dict(data, key, value):
    def make_data(x, row):
        if row.get(key) not in x:
            x[row.get(key)] = row.get(value)
        return x

    return reduce(make_data, data, {})