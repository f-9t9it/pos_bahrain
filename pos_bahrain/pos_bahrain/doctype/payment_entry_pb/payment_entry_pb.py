# -*- coding: utf-8 -*-
# Copyright (c) 2020, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry


class PaymentEntryPB(PaymentEntry):
    def validate_account_type(self, account, account_types):
        if self.payment_type != "Internal Transfer":
            super().validate_account_type(account, account_types)
