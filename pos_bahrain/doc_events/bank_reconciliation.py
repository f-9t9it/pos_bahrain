# -*- coding: utf-8 -*-
# Copyright (c) 2020, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from toolz.curried import concatv, merge, dissoc

from pos_bahrain.pos_bahrain.doctype.gl_payment.gl_payment import get_direction


def get_payment_entries(doc, method):
    # account_currency = frappe.db.get_value(
    #     "Account", doc.bank_account, "account_currency"
    # )
    account_currency = frappe.db.get_value(
        "Account", doc.account, "account_currency"
    )
    def make_entry(entry, reverse):
        return merge(
            entry,
            {
                "payment_document": "GL Payment",
                get_direction(entry.payment_type, reverse): entry.total_amount,
                get_direction(entry.payment_type, reverse=(not reverse)): 0,
                "account_currency": account_currency,
            },
        )

    def make_row(row):
        amount = frappe.utils.flt(row.get("debit", 0)) - frappe.utils.flt(
            row.get("credit", 0)
        )
        return merge(
            row,
            {
                "amount": "{} {}".format(
                    frappe.utils.fmt_money(abs(amount), 3, row.get("account_currency")),
                    frappe._("Dr") if amount > 0 else frappe._("Cr"),
                )
            },
        )

    # values = {"account": doc.bank_account, "from": doc.from_date, "to": doc.to_date}
    values = {"account": doc.account, "from": doc.from_date, "to": doc.to_date}
    gl_payments1 = (
        [
            make_entry(x, reverse=False)
            for x in frappe.db.sql(
                """
            SELECT
                name AS payment_entry,
                reference_no AS cheque_number,
                reference_date AS cheque_date,
                payment_type,
                total_amount,
                posting_date,
                IFNULL(party, (
                    SELECT GROUP_CONCAT(gpi.account SEPARATOR ', ')
                    FROM `tabGL Payment Item` AS gpi WHERE gpi.parent = gp.name
                )) AS against_account,
                clearance_date
            FROM `tabGL Payment` AS gp
            # WHERE {conditions} 
            WHERE {conditions} and gp.clearance_date IS NULL
        """.format(
                    conditions=_get_conditions(
                        ["gp.payment_account = %(account)s"]#,
                        # [
                        #     "(gp.clearance_date IS NULL OR gp.clearance_date = '0000-00-00')"
                        # ]
                        # if doc.include_reconciled_entries 
                        #  else [],
                    )
                ),
                values=values,
                as_dict=1,
            )
        ]
        # + [
        #     make_entry(x, reverse=True)
        #     for x in frappe.db.sql(
        #         """
        #         SELECT
        #             gp.name AS payment_entry,
        #             gp.reference_no AS cheque_number,
        #             gp.reference_date AS cheque_date,
        #             gp.payment_type,
        #             (gpi.net_amount + gpi.tax_amount) AS total_amount,
        #             gp.posting_date,
        #             IFNULL(gp.party, gp.payment_account) AS against_account,
        #             gp.clearance_date
        #         FROM `tabGL Payment Item` AS gpi
        #         LEFT JOIN `tabGL Payment` AS gp ON gp.name = gpi.parent
        #         WHERE {conditions} and gp.clearance_date IS NULL
        #     """.format(
        #             conditions=_get_conditions(
        #                 ["gp.payment_account = %(account)s"]#,
        #                 # [
        #                 #     "(gp.clearance_date IS NULL OR gp.clearance_date = '0000-00-00')"
        #                 # ]
        #                 # if not doc.include_reconciled_entries
        #                 # else [],
        #             )
        #         ),
        #         values=values,
        #         as_dict=1,
        #     )
        # ]
    )
    gl_payments2 = (
        [
            make_entry(x, reverse=False)
            for x in frappe.db.sql(
                """
            SELECT
                name AS payment_entry,
                reference_no AS cheque_number,
                reference_date AS cheque_date,
                payment_type,
                total_amount,
                posting_date,
                IFNULL(party, (
                    SELECT GROUP_CONCAT(gpi.account SEPARATOR ', ')
                    FROM `tabGL Payment Item` AS gpi WHERE gpi.parent = gp.name
                )) AS against_account,
                clearance_date
            FROM `tabGL Payment` AS gp
            # WHERE {conditions} 
            WHERE {conditions} and gp.clearance_date IS NOT NULL
        """.format(
                    conditions=_get_conditions(
                        ["gp.payment_account = %(account)s"]#,
                        # [
                        #     "(gp.clearance_date IS NULL OR gp.clearance_date = '0000-00-00')"
                        # ]
                        # if doc.include_reconciled_entries 
                        #  else [],
                    )
                ),
                values=values,
                as_dict=1,
            )
        ]
        + [
            make_entry(x, reverse=True)
            for x in frappe.db.sql(
                """
                SELECT
                    gp.name AS payment_entry,
                    gp.reference_no AS cheque_number,
                    gp.reference_date AS cheque_date,
                    gp.payment_type,
                    (gpi.net_amount + gpi.tax_amount) AS total_amount,
                    gp.posting_date,
                    IFNULL(gp.party, gp.payment_account) AS against_account,
                    gp.clearance_date
                FROM `tabGL Payment Item` AS gpi
                LEFT JOIN `tabGL Payment` AS gp ON gp.name = gpi.parent
                WHERE {conditions} and gp.clearance_date IS NULL
            """.format(
                    conditions=_get_conditions(
                        ["gp.payment_account = %(account)s"]#,
                        # [
                        #     "(gp.clearance_date IS NULL OR gp.clearance_date = '0000-00-00')"
                        # ]
                        # if not doc.include_reconciled_entries
                        # else [],
                    )
                ),
                values=values,
                as_dict=1,
            )
        ]
    )



    if doc.include_reconciled_entries:
        gl_payments=gl_payments2
        payment_entries = sorted(
            [dissoc(x.as_dict(), "idx") for x in doc.payment_entries]
            + [make_row(x) for x in gl_payments],
            key=lambda k: k["posting_date"] or frappe.utils.getdate(frappe.utils.nowdate()),
        )

        doc.set("payment_entries", [])
        for row in payment_entries:
            doc.append("payment_entries", row)

        doc.total_amount += sum(
            [
                frappe.utils.flt(x.get("debit", 0)) - frappe.utils.flt(x.get("credit", 0))
                for x in gl_payments
            ]
        )
    if not doc.include_reconciled_entries:
        gl_payments=gl_payments1   
        payment_entries = sorted(
            [dissoc(x.as_dict(), "idx") for x in doc.payment_entries]
            + [make_row(x) for x in gl_payments],
            key=lambda k: k["posting_date"] or frappe.utils.getdate(frappe.utils.nowdate()),
        )

        doc.set("payment_entries", [])
        for row in payment_entries:
            doc.append("payment_entries", row)

        doc.total_amount += sum(
            [
                frappe.utils.flt(x.get("debit", 0)) - frappe.utils.flt(x.get("credit", 0))
                for x in gl_payments
            ]
        )


def update_clearance_date(doc, method):
    get_payment_entries(doc, method)


def _get_conditions(*conditions):
    return " AND ".join(
        concatv(
            [
                "gp.docstatus = 1",
                "gp.posting_date >= %(from)s",
                "gp.posting_date <= %(to)s",
            ],
            *conditions,
        )
    )
