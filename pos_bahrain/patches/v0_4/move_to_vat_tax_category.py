# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from toolz.curried import pluck


def execute():
    if frappe.db.exists(
        "DocType", "POS Bahrain Settings Tax Exempt"
    ) and frappe.db.exists("DocType", "POS Bahrain Settings Tax Category"):
        settings = frappe.get_single("POS Bahrain Settings")
        for account in pluck(
            "account",
            frappe.get_all(
                "POS Bahrain Settings Tax Exempt",
                filters={
                    "parent": "POS Bahrain Settings",
                    "parentfield": "vat_exempt_account",
                },
                fields="account",
            ),
        ):
            settings.append(
                "vat_tax_categories", {"account": account, "category": "Exempt"}
            )

        settings.save(ignore_permissions=True)

    frappe.delete_doc_if_exists("DocType", "POS Bahrain Settings Tax Exempt")
