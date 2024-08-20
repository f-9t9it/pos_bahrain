# -*- coding: utf-8 -*-
# pylint: disable=no-member
# Copyright (c) 2020, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.accounts.general_ledger import make_gl_entries
from functools import partial
from toolz import compose, concat, merge


class GLPayment(AccountsController):
    def validate(self):
        account_type = frappe.db.get_value(
            "Account", self.payment_account, "account_type"
        )

        valid_account_types = ["Cash", "Bank"]
        if account_type not in valid_account_types:
            frappe.throw(
                frappe._("Account Type for {} must be one of {}").format(
                    self.payment_account, frappe.utils.comma_or(valid_account_types)
                )
            )

        if account_type == "Bank":
            if not self.reference_no or not self.reference_date:
                frappe.throw(
                    frappe._(
                        "Reference No and Reference Date is mandatory for bank transactions"
                    )
                )

    def on_submit(self):
        if not self.remarks:
            self._set_remarks()
        self._make_gl_entries()

    def on_cancel(self):
        self._make_gl_entries(cancel=1)
        gl_entry = frappe.db.get_list("GL Entry", filters={"voucher_no": self.name})
        for gl in gl_entry:
            frappe.db.delete("GL Entry", gl.name)

    def _set_remarks(self):
        get_remarks = compose(lambda x: "\n".join(x), partial(filter, None))
        self.remarks = get_remarks(
            [
                "Amount {} {} {}".format(
                    self.get_formatted("total_amount"),
                    "from" if self.payment_type == "Incoming" else "to",
                    self.party_name,
                )
                if self.party
                else "",
                "Transaction reference no {} dated {}".format(
                    self.reference_no, self.reference_date
                )
                if self.reference_no
                else "",
            ]
        )

    def get_gl_dict(self, x):
        gl_dict = super().get_gl_dict(x)
        gl_dict['cost_center'] = self.cost_center
        return gl_dict

    def _make_gl_entries(self, cancel=0):
        gl_entries = [
            self.get_gl_dict(x)
            for x in self._get_payment_gl_entries() + self._get_account_gl_entries()
            if x.get("account")
        ]
        make_gl_entries(gl_entries, cancel=cancel)

    def _get_payment_gl_entries(self):
        credit_or_debit = get_direction(self.payment_type)
        in_account_currency = "{}_in_account_currency".format(credit_or_debit)
        return [
            {
                "account": self.payment_account,
                credit_or_debit: self.total_amount,
                in_account_currency: self.total_amount,
                "against": self.party,
                "remarks": self.remarks,
            }
        ]

    def _get_account_gl_entries(self):
        credit_or_debit = get_direction(self.payment_type, reverse=True)
        in_account_currency = "{}_in_account_currency".format(credit_or_debit)
        list_concat = compose(list, concat)
        return list_concat(
            [
                [
                    {
                        "account": x.account,
                        credit_or_debit: x.net_amount,
                        in_account_currency: x.net_amount,
                        "against": self.party,
                        "cost_center": self.cost_center,
                        "remarks": x.remarks,
                    },
                    {
                        "account": x.account_head,
                        credit_or_debit: x.tax_amount,
                        in_account_currency: x.tax_amount,
                        "against": self.party,
                    },
                ]
                for x in self.items
            ]
        )


def get_direction(payment_type, reverse=False):
    if payment_type == "Incoming":
        return "debit" if not reverse else "credit"
    return "credit" if not reverse else "debit"
