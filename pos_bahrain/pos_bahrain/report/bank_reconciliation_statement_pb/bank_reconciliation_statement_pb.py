# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.accounts.report.bank_reconciliation_statement.bank_reconciliation_statement import (
    execute as bank_reconciliation_statement,
    get_balance_row,
)
from toolz.curried import compose, merge, map

from pos_bahrain.pos_bahrain.doctype.gl_payment.gl_payment import get_direction


def execute(filters=None):
    columns, data = bank_reconciliation_statement(filters)
    return columns, _extend_data(filters, data)


def _extend_data(filters, data):
    account_currency = frappe.db.get_value(
        "Account", filters.account, "account_currency"
    )

    def make_row(row, reverse):
        return merge(
            row,
            {
                "payment_document": "GL Payment",
                get_direction(row.payment_type, reverse): row.total_amount,
                get_direction(row.payment_type, reverse=(not reverse)): 0,
                "account_currency": account_currency,
            },
        )
    gl_payments = [
        make_row(x, reverse=False)
        for x in frappe.db.sql(
            """
                SELECT
                    name AS payment_entry,reference_no,reference_date AS ref_date,
                    payment_type,
                    total_amount,
                    posting_date,
                    IFNULL(party, (
                        SELECT GROUP_CONCAT(gpi.account SEPARATOR ', ')
                        FROM `tabGL Payment Item` AS gpi WHERE gpi.parent = gp.name
                    )) AS against_account,
                    clearance_date
                FROM `tabGL Payment` AS gp
                WHERE
                    payment_account = %(account)s AND
                    docstatus = 1 AND
                    posting_date <= %(report_date)s AND
                    IFNULL(clearance_date, '4000-01-01') > %(report_date)s
            """,
            values=filters,
            as_dict=1,
        )
    ]
    gl_payment_items = [
        make_row(x, reverse=True)
        for x in frappe.db.sql(
            """
                SELECT
                    gp.name AS payment_entry,
                    gp.reference_no,
                    gp.reference_date AS ref_date,
                    gp.payment_type,
                    (gpi.net_amount + gpi.tax_amount) AS total_amount,
                    gp.posting_date,
                    IFNULL(gp.party, gp.payment_account) AS against_account,
                    gp.clearance_date
                FROM `tabGL Payment Item` AS gpi
                LEFT JOIN `tabGL Payment` AS gp ON gp.name = gpi.parent
                WHERE
                    gpi.account = %(account)s AND
                    gp.docstatus = 1 AND
                    gp.posting_date <= %(report_date)s AND
                    IFNULL(gp.clearance_date, '4000-01-01') > %(report_date)s
            """,
            values=filters,
            as_dict=1,
        )
    ]

    items = data[:-6]
    summary = data[-6:]
    balance_per_gl = summary[0]
    outstanding = summary[2]
    incorrect = summary[3]
    balance_calculated = summary[5]

    total_debit = sum([x.get("debit", 0) for x in gl_payments]) + sum(
        [x.get("debit", 0) for x in gl_payment_items]
    )
    total_credit = sum([x.get("credit", 0) for x in gl_payments]) + sum(
        [x.get("credit", 0) for x in gl_payment_items]
    )

    amounts_not_reflected_in_system = _get_invalid_gl_payments(filters)

    return sorted(
        items + gl_payments + gl_payment_items,
        key=lambda k: k["posting_date"] or frappe.utils.getdate(frappe.utils.nowdate()),
    ) + [
        balance_per_gl,
        {},
        merge(
            outstanding,
            {
                "debit": outstanding.get("debit") + total_debit,
                "credit": outstanding.get("credit") + total_credit,
            },
        ),
        get_balance_row(
            incorrect.get("payment_entry"),
            incorrect.get("debit")
            - incorrect.get("credit")
            + amounts_not_reflected_in_system,
            incorrect.get("account_currency"),
        ),
        {},
        get_balance_row(
            balance_calculated.get("payment_entry"),
            balance_calculated.get("debit")
            - balance_calculated.get("credit")
            - total_debit
            + total_credit
            + amounts_not_reflected_in_system,
            balance_calculated.get("account_currency"),
        ),
    ]


def _get_invalid_gl_payments(filters):
    def make_row(row, reverse):
        return {
            get_direction(row.payment_type, reverse): row.total_amount,
            get_direction(row.payment_type, reverse=(not reverse)): 0,
        }

    amounts = (
        [
            make_row(x, reverse=False)
            for x in frappe.db.sql(
                """
                    SELECT total_amount, payment_type FROM `tabGL Payment`
                    WHERE
                        payment_account = %(account)s AND
                        docstatus = 1 AND
                        posting_date > %(report_date)s AND
                        clearance_date <= %(report_date)s
                """,
                values=filters,
                as_dict=1,
            )
        ]
        + [
            make_row(x, reverse=True)
            for x in frappe.db.sql(
                """
                    SELECT
                        (gpi.net_amount + gpi.tax_amount) AS total_amount,
                        gp.payment_type
                    FROM `tabGL Payment Item` AS gpi
                    LEFT JOIN `tabGL Payment` AS gp ON gp.name = gpi.parent
                    WHERE
                        gpi.account = %(account)s AND
                        gp.docstatus = 1 AND
                        gp.posting_date > %(report_date)s AND
                        gp.clearance_date <= %(report_date)s
                """,
                values=filters,
                as_dict=1,
            )
        ]
    )

    return sum([x.get("debit") - x.get("credit") for x in amounts])
