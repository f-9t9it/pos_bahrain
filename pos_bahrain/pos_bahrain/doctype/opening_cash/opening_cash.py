# -*- coding: utf-8 -*-
# Copyright (c) 2018, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class OpeningCash(Document):
    def validate(self):
        opening_voucher = frappe.db.sql(
            """
          SELECT name FROM `tabOpening Cash`
          WHERE date=%s AND pos_profile=%s AND docstatus=1
          """,
            (self.date, self.pos_profile),
        )
        if opening_voucher:
            pos_closing_voucher = frappe.db.sql(
                """
              SELECT name FROM `tabPOS Closing Voucher`
              WHERE period_start_date=%s AND pos_profile=%s AND docstatus=1
              """,
                (self.date, self.pos_profile),
            )
        if not pos_closing_voucher:
            frappe.throw("POS Closing Voucher is not submitted yet")
