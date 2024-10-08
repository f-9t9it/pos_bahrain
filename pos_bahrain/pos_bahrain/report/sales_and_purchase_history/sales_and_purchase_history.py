# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from functools import partial
from toolz import compose, pluck, merge, concatv

from pos_bahrain.utils import pick, sum_by
from pos_bahrain.utils.report import make_column


def execute(filters=None):
    columns = _get_columns(filters)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(filters)

    partners = _get_partners()
    opening_data = _get_opening_data(filters, keys, partners)

    data = _get_data(clauses, values, keys)
    partners_data = _get_partners_data(data, partners)

    total_data = _get_total_receipts_and_issues(partners_data, "Total", True)
    closing_data = _get_total_receipts_and_issues(
        [opening_data, *partners_data], "Closing (Opening + Total)", True
    )

    return columns, [opening_data, *partners_data, total_data, closing_data]


def _get_columns(filters):
    join_columns = compose(list, concatv)
    return join_columns(
        [
            make_column("posting_date", "Date", type="Date", width=90),
            make_column("voucher_type", hidden=1),
            make_column(
                "voucher_no",
                "Bill No",
                type="Dynamic Link",
                options="voucher_type",
                width=150,
            ),
            make_column("particulars", width=180),
            make_column("expiry_date", type="Date", width=90),
            make_column("receipt", type="Float", width=90),
            make_column("issue", type="Float", width=90),
            make_column("balance", type="Float", width=90),
            make_column("partner", type="Float", width=120, label="Partner Sales"),
        ],
    )


def _get_filters(filters, opening=False):
    clauses = concatv(
        ["sle.posting_date BETWEEN %(from_date)s AND %(to_date)s"]
        if not opening
        else ["sle.posting_date < %(from_date)s"],
        ["sle.item_code = %(item_code)s"],
        ["sle.warehouse = %(warehouse)s"] if filters.warehouse else [],
    )
    values = merge(
        pick(["item_code", "price_list", "warehouse"], filters),
        {"from_date": filters.from_date, "to_date": filters.to_date},
    )
    return (
        {"clauses": " AND ".join(clauses)},
        values,
    )


def _get_data(clauses, values, keys):
    result = frappe.db.sql(
        """
            SELECT
                sle.posting_date AS posting_date,
                sle.voucher_type AS voucher_type,
                sle.voucher_no AS voucher_no,
                sle.actual_qty AS qty,
                b.expiry_date AS expiry_date,
                si.customer AS partner
            FROM `tabStock Ledger Entry` AS sle
            LEFT JOIN `tabItem` AS i ON i.name = sle.item_code
            LEFT JOIN `tabBatch` AS b ON b.name = sle.batch_no
            LEFt JOIN `tabSales Invoice` AS si ON si.name = sle.voucher_no
            WHERE {clauses}
            ORDER BY sle.posting_date
        """.format(
            **clauses
        ),
        values=values,
        as_dict=1,
    )

    def set_particalurs_and_qtys(row):
        voucher_type = row.get("voucher_type")
        qty = row.get("qty")
        if voucher_type in ["Sales Invoice", "Delivery Note"]:
            return merge(row, {"particulars": "Sales", "receipt": None, "issue": -qty})
        if voucher_type in ["Purchase Invoice", "Purchase Receipt"]:
            return merge(
                row,
                {
                    "particulars": "Purchase",
                    "receipt": qty if qty > 0 else None,
                    "issue": -qty if qty < 0 else None,
                },
            )
        if voucher_type in ["Stock Entry", "Stock Reconciliation"]:
            return merge(
                row, {"particulars": "Adjustment", "receipt": qty, "issue": None}
            )
        return row

    make_row = compose(partial(pick, keys), set_particalurs_and_qtys)
    return [make_row(x) for x in result]


def _get_opening_data(filters, keys, partners=None):
    clauses, values = _get_filters(filters, True)
    data = _get_data(clauses, values, keys)
    partners_data = list(_get_partners_data(data, partners))
    return _get_total_receipts_and_issues(partners_data, "Opening", True)


def _get_total_receipts_and_issues(data, title, partner=False):
    receipt = sum_by("receipt", data)
    issue = sum_by("issue", data)
    partner = sum_by("partner", data) if partner else 0.00
    return {
        "particulars": title,
        "receipt": receipt,
        "issue": issue,
        "balance": receipt - issue,
        "partner": partner,
    }


def _get_partners():
    return [
        x.get("customer")
        for x in frappe.get_all(
            "POS Bahrain Settings Partner",
            fields=["customer"],
        )
    ]


def _get_partners_data(data, partners):
    return list(
        map(
            lambda x: merge(
                x,
                {
                    "partner": x.get("issue")
                    if x.get("particulars") == "Sales"
                    and x.get("partner", "") in partners
                    else 0.00
                },
            ),
            data,
        )
    )
