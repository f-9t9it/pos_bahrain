# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial
from toolz import compose, pluck, merge

from pos_bahrain.pos_bahrain.report.vat_on_sales_per_gcc.vat_on_sales_per_gcc import (
    make_report,
    VatCategoryNotFound,
)
from pos_bahrain.utils import sum_by
from pos_bahrain.utils.report import make_column


def execute(filters=None):
    columns = _get_columns(filters)
    data = _get_data(filters)
    return columns, data


def _get_columns(filters):
    return [
        make_column("description", "Description", width=480),
        make_column("taxable_amount", "Amount (BHD)", type="Float"),
        make_column("vat_amount", "VAT amount (BHD)", type="Float"),
    ]


def _get_filters(filters):
    values = merge(
        {"from_date": filters.date_range[0], "to_date": filters.date_range[1],"company":filters.company},
    )
    return "", values


def _get_data(filters):
    sales_standard = _get_vat_row("Sales Invoice", filters, "Standard Rated")
    sales_zero = _get_vat_row("Sales Invoice", filters, "Zero Rated")
    sales_exempt = _get_vat_row("Sales Invoice", filters, "Exempted")
    sales_total = _merge_sum([sales_standard, sales_zero, sales_exempt])
    purchase_standard = _get_vat_row("Purchase Invoice", filters, "Standard Rated")
    purchase_zero = _get_vat_row("Purchase Invoice", filters, "Zero Rated")
    purchase_exempt = _get_vat_row("Purchase Invoice", filters, "Exempted")
    purchase_import = _get_vat_row("Purchase Invoice", filters, "Imported")
    purchase_na = _get_vat_row("Purchase Invoice", filters, "Out of Scope")
    purchase_total = _merge_sum(
        [
            purchase_standard,
            purchase_zero,
            purchase_exempt,
            purchase_import,
            purchase_na,
        ]
    )
    vat_total = sales_total.get("vat_amount", 0) - purchase_total.get("vat_amount", 0)
    return [
        {"description": frappe._("VAT on sales"), "bold": True},
        merge(
            {"description": frappe._("Standard rated sales"), "indent": 1},
            sales_standard,
        ),
        {
            "description": frappe._(
                "Sales to registered customers in other GCC States"
            ),
            "indent": 1,
        },
        {
            "description": frappe._(
                "Sales subject to domestic reverse charge mechanism "
            ),
            "indent": 1,
        },
        merge(
            {"description": frappe._("Zero rated domestic sales"), "indent": 1},
            sales_zero,
        ),
        {"description": frappe._("Exports"), "indent": 1},
        merge({"description": frappe._("Exempt sales"), "indent": 1}, sales_exempt),
        merge({"description": frappe._("Total sales"), "bold": True}, sales_total),
        {"description": frappe._("VAT on purchases"), "bold": True},
        merge(
            {"description": frappe._("Standard rated domestic purchases"), "indent": 1},
            purchase_standard,
        ),
        merge(
            {
                "description": frappe._(
                    "Imports subject to VAT either paid at customs or deferred"
                ),
                "indent": 1,
            },
            purchase_import,
        ),
        {
            "description": frappe._(
                "Imports subject to VAT accounted for through reverse charge mechanism"
            ),
            "indent": 1,
        },
        {
            "description": frappe._(
                "Purchases subject to domestic reverse charge mechanism"
            ),
            "indent": 1,
        },
        merge(
            {
                "description": frappe._(
                    "Purchases from non-registered taxpayers, zero-rated/ exempt purchases"
                ),
                "indent": 1,
            },
            _merge_sum([purchase_zero, purchase_exempt, purchase_na]),
        ),
        merge(
            {"description": frappe._("Total purchases"), "bold": True}, purchase_total,
        ),
        {
            "description": frappe._("Total VAT due for current period"),
            "bold": True,
            "vat_amount": vat_total,
        },
        {
            "description": frappe._(
                "Corrections from previous period (between BHD ±5,000)"
            )
        },
        {"description": frappe._("VAT credit carried forward from previous period(s)")},
        {
            "description": frappe._("Net VAT due (or reclaimed)"),
            "bold": True,
            "vat_amount": vat_total,
        },
    ]


def _get_vat_row(doctype, filters, vat_type):
    try:
        _, data = make_report(
            doctype,
            frappe._dict(
                merge(filters, {"vat_type": vat_type, "hide_error_message": True})
            ),
        )
        return _merge_sum(data)
    except VatCategoryNotFound:
        return {"taxable_amount": 0, "vat_amount": 0}


def _merge_sum(data):
    return {x: sum_by(x, data) for x in ["taxable_amount", "vat_amount"]}
