# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
import erpnext
from toolz.curried import pluck


def execute():
    for gle in frappe.db.sql(
        """
            SELECT
                name,
                company,
                account_currency,
                credit,
                credit_in_account_currency,
                debit,
                debit_in_account_currency
            FROM `tabGL Entry`
            WHERE
                voucher_type = 'GL Payment' AND (
                    credit != credit_in_account_currency OR
                    debit != debit_in_account_currency
                ) 
        """,
        as_dict=1,
    ):
        if erpnext.get_company_currency(gle.get("company")) == gle.get(
            "account_currency"
        ):
            if gle.get("credit") != gle.get("credit_in_account_currency"):
                frappe.db.set_value(
                    "GL Entry",
                    gle.get("name"),
                    "credit_in_account_currency",
                    gle.get("credit"),
                )
            if gle.get("debit") != gle.get("debit_in_account_currency"):
                frappe.db.set_value(
                    "GL Entry",
                    gle.get("name"),
                    "debit_in_account_currency",
                    gle.get("debit"),
                )
