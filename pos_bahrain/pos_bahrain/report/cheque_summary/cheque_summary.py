# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from functools import partial
from toolz import compose, pluck, merge, groupby

from pos_bahrain.utils import pick


def execute(filters=None):
    columns = _get_columns(filters)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)
    data = _get_data(clauses, values, keys)
    return columns, data


def _get_columns(filters):
    def make_column(key, label=None, type="Data", options=None, width=120):
        return {
            "label": _(label or key.replace("_", " ").title()),
            "fieldname": key,
            "fieldtype": type,
            "options": options,
            "width": width,
        }

    return [
        make_column("doctype", "Document Type"),
        make_column("docname", "Document No", type="Dynamic Link", options="doctype"),
        make_column("posting_date", "Date", type="Date", width=90),
        make_column("party_type"),
        make_column("party", type="Dynamic Link", options="party_type"),
        make_column("party_name", width=150),
        make_column("cheque_no"),
        make_column("cheque_date", type="Date", width=90),
        make_column("amount", type="Currency", width=90),
        make_column("remarks"),
    ]


def _get_filters(filters):
    pe_clauses = [
        "pe.docstatus = 1",
        "pe.posting_date BETWEEN %(from_date)s AND %(to_date)s",
        "pe.mode_of_payment = 'Cheque'",
    ]
    je_clauses = [
        "je.docstatus = 1",
        "je.posting_date BETWEEN %(from_date)s AND %(to_date)s",
        "je.pb_is_cheque = 1",
    ]
    values = merge(
        pick(["customer", "branch"], filters),
        {"from_date": filters.from_date, "to_date": filters.to_date},
    )
    return (
        {
            "pe_clauses": " AND ".join(pe_clauses),
            "je_clauses": " AND ".join(je_clauses),
        },
        values,
    )


def _get_data(clauses, values, keys):
    payment_entries = frappe.db.sql(
        """
            SELECT
                'Payment Entry' AS doctype,
                pe.name AS docname,
                pe.posting_date AS posting_date,
                pe.paid_from AS paid_from,
                pe.party_type AS party_type,
                pe.party AS party,
                pe.party_name AS party_name,
                pe.reference_no AS cheque_no,
                pe.reference_date AS cheque_date,
                pe.paid_amount AS amount,
                pe.remarks AS remarks
            FROM `tabPayment Entry` AS pe
            WHERE {pe_clauses}
        """.format(
            **clauses
        ),
        values=values,
        as_dict=1,
    )
    journal_entries = frappe.db.sql(
        """
            SELECT
                'Journal Entry' AS doctype,
                je.name AS docname,
                je.posting_date AS posting_date,
                je.cheque_no AS cheque_no,
                je.cheque_date AS cheque_date,
                je.total_debit AS amount,
                je.remark AS remarks
            FROM `tabJournal Entry` AS je
            WHERE {je_clauses}
        """.format(
            **clauses
        ),
        values=values,
        as_dict=1,
    )

    journal_entry_accounts = (
        groupby(
            "parent",
            frappe.db.sql(
                """
                    SELECT parent, account, party_type, party, credit
                    FROM `tabJournal Entry Account`
                    WHERE parent IN %(parents)s
                """,
                values={"parents": [x.get("docname") for x in journal_entries]},
                as_dict=1,
            ),
        )
        if journal_entries
        else {}
    )

    def set_party(row):
        if row.get("doctype") == "Journal Entry":
            for detail in journal_entry_accounts.get(row.get("docname"), []):
                party_type = detail.get("party_type")
                party = detail.get("party")
                if party and party_type in [
                    "Customer",
                    "Supplier",
                    "Employee",
                    "Member",
                ]:
                    name_field = "{}_name".format(party_type.lower())
                    return merge(
                        row,
                        {
                            "party_type": party_type,
                            "party": party,
                            "party_name": frappe.db.get_value(
                                party_type, party, name_field
                            ),
                        },
                    )
        return row

    def negated(row):
        return merge(row, {"amount": -1 * row.get("amount")})

    def set_sign(row):
        if row.get("doctype") == "Payment Entry":
            if (
                frappe.db.get_value("Account", row.get("paid_from"), "account_type")
                == "Bank"
            ):
                return negated(row)

        if row.get("doctype") == "Journal Entry":
            for detail in journal_entry_accounts.get(row.get("docname"), []):
                if (
                    detail.get("credit")
                    and frappe.db.get_value(
                        "Account", detail.get("account"), "account_type"
                    )
                    == "Bank"
                ):
                    return negated(row)

        return row

    make_row = compose(partial(pick, keys), set_sign, set_party)
    return [
        make_row(x)
        for x in sorted(
            payment_entries + journal_entries, key=lambda x: x["posting_date"]
        )
    ]
