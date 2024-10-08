# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.utils import now


@frappe.whitelist()
def create_opening(opening_amount, company, pos_profile, user=None, posting=None):
    pv = frappe.get_doc(
        {
            "doctype": "POS Closing Voucher",
            "period_from": posting or now(),
            "company": company,
            "pos_profile": pos_profile,
            "user": user or frappe.session.user,
            "opening_amount": opening_amount,
        }
    ).insert(ignore_permissions=True)
    return pv.name


@frappe.whitelist()
def get_unclosed(user, pos_profile, company):
    return frappe.db.exists(
        "POS Closing Voucher",
        {"user": user, "pos_profile": pos_profile, "company": company, "docstatus": 0},
    )
