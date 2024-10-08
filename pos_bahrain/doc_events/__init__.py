# -*- coding: utf-8 -*-
# Copyright (c) 2018, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def _get_user_companies(user):
    return frappe.db.sql(
        """
            SELECT for_value FROM `tabUser Permission`
            WHERE allow='Company' AND user=%(user)s
        """,
        values={'user': user},
    )


def set_user_defaults(login_manager):
    if frappe.session.user:
        company = frappe.defaults.get_user_default('company')
        allowed_companies = _get_user_companies(frappe.session.user)
        if allowed_companies and company not in allowed_companies:
            frappe.defaults.set_user_default('company', allowed_companies[0])
