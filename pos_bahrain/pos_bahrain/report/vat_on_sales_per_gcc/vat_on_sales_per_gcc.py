# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import frappe,erpnext
# from erpnext.controllers.taxes_and_totals import get_itemised_tax_breakup_data
from functools import partial
from toolz import compose, concatv, pluck, merge, groupby, concat, excepts, first
from frappe.utils import cint, flt, round_based_on_smallest_currency_fraction
from pos_bahrain.utils import pick
from pos_bahrain.utils.report import make_column


class VatCategoryNotFound(frappe.exceptions.ValidationError):
    pass


def execute(filters=None):
    return make_report("Sales Invoice", filters)


def make_report(doctype, filters):
    if doctype not in ["Sales Invoice", "Purchase Invoice"]:
        frappe.throw(
            frappe._("Report not available for {}".format(frappe.bold(doctype)))
        )
    columns = _get_columns(doctype, filters)
    keys = compose(list, partial(pluck, "fieldname"))(columns)
    clauses, values = _get_filters(doctype, filters)

    data = _get_data(clauses, values, keys)

    jsonString_col = json.dumps(clauses, indent=4, sort_keys=True, default=str)
    #f3= open("txt/clauses.txt","w+")
    f3= open("clauses.txt","w+")
    f3.write(jsonString_col)

    jsonString_col = json.dumps(values, indent=4, sort_keys=True, default=str)
    #f3= open("txt/clauses.txt","w+")
    f3= open("values.txt","w+")
    f3.write(jsonString_col)

    return columns, data


def _get_columns(doctype, filters):
    return [
        make_column("vat_return_no", "VAT return field number", width=150),
        make_column("invoice", "Invoice number", width=150),
        make_column("date", "Invoice date", type="Date", width=90),
        make_column("vat_account_no", "VAT Account Number", width=150),
        make_column("cost_center", "Cost Center", width=150),
        make_column("branch", "Branch", width=150),
        make_column("party_name", "Client name", width=150),
        make_column("description", "Good/Service description", width=180),
        make_column("taxable_amount", "Total BHD (exclusive of VAT)", type="Float"),
        make_column("vat_amount", "VAT amount", type="Float"),
        make_column("total_amount", "Total BHD (inclusive of VAT)", type="Float"),
    ]


def _get_filters(doctype, filters):
    # is_include = filters.vat_type not in ["Standard Rated", "Zero Rated"]
    is_include = filters.vat_type not in ["ZeroRated"]
    vat_exempt_accounts = [
        x[0]
        for x in frappe.get_all(
            "POS Bahrain Settings Tax Category",
            # filters={"category": filters.vat_type} if is_include else {"category":('not in',(filters.vat_type))},
            # filters={"category": filters.vat_type} if is_include else {"category":('not in',(filters.vat_type))},or_filters= {"category":('not in' ,("Standard Rated", "Zero Rated" ))},
            filters={"category": filters.vat_type} if is_include else {"category":('not in',(filters.vat_type))},or_filters= {"category":('not in' ,("ZeroRated" ))},
            fields=["account"],
            as_list=1,
        )
    ]
    print('/////////',vat_exempt_accounts)
    if not vat_exempt_accounts:
        msg = "Please setup {}: <em>VAT Tax Categories</em>".format(
            frappe.get_desk_link("POS Bahrain Settings", "")
        )
        if filters.get("hide_error_message"):
            raise VatCategoryNotFound(msg)
        else:
            frappe.throw(msg, exc=VatCategoryNotFound)

    inv_clauses = list(
        concatv(
            ["d.docstatus = 1"],
            ["d.posting_date BETWEEN %(from_date)s AND %(to_date)s"],
            ["IFNULL(dt.account_head, '') != ''"],
            ["dt.account_head {} %(tax_accounts)s".format("IN" if is_include else "NOT IN")],
            ["d.company = %(company)s"] if filters.get('company') else [],
            ["d.cost_center = %(cost_center)s"] if filters.get('cost_center') else [],
            ["d.set_warehouse = %(warehouse)s"] if filters.get('warehouse') else [],
        )
    )
    glp_clauses = concatv(
        inv_clauses, ["d.payment_type IN %(payment_types)s", "a.account_type = 'Tax'"]
    )
    values = merge(
        pick(["vat_type"], filters),
        {
            "from_date": filters.from_date,
            "to_date": filters.to_date,
            "tax_accounts": vat_exempt_accounts,
            "payment_types": ["Incoming"]
            if doctype == "Sales Invoice"
            else ["Outgoing", "Internal Transfer"],
        },
        pick(["company", "cost_center", "warehouse"], filters),
    )
    return (
        {
            "doctype": doctype,
            "item_doctype": "{} Item".format(doctype),
            "tax_doctype": "{} Taxes and Charges".format(
                "Sales" if doctype == "Sales Invoice" else "Purchase"
            ),
            "party_name": "{}_name".format(
                "customer" if doctype == "Sales Invoice" else "supplier"
            ),
            "invoice_clauses": " AND ".join(inv_clauses),
            "glp_clauses": " AND ".join(glp_clauses),
        },
        values,
    )


def _get_data(clauses, values, keys):
    invoices = frappe.db.sql(
        """
            SELECT
                '{doctype}' AS doctype,
                d.name AS name,
                d.posting_date,
                d.tax_id AS tax_id,
                d.{party_name} AS {party_name}
            FROM `tab{tax_doctype}` AS dt
            LEFT JOIN `tab{doctype}` AS d ON d.name = dt.parent
            WHERE {invoice_clauses}
            GROUP BY d.name
        """.format(
            **clauses
        ),
        values=values,
        as_dict=1,
    )
    invoice_items = _get_child_table_rows(
        """
            SELECT * FROM `tab{child_doctype}` WHERE parent IN %(docnames)s
        """.format(
            child_doctype=clauses.get("item_doctype"),
        ),
        invoices,
    )
    invoice_taxes = _get_child_table_rows(
        """
            SELECT p.* FROM `tab{child_doctype}` AS p
            LEFT JOIN `tabAccount` AS a ON a.name = p.account_head
            WHERE p.parent IN %(docnames)s AND a.account_type = 'Tax'
        """.format(
            child_doctype=clauses.get("tax_doctype"),
        ),
        invoices,
    )

    gl_payments = frappe.db.sql(
        """
            SELECT
                d.name AS name,
                d.posting_date,
                d.tax_id AS tax_id,
                d.party_name AS {party_name},
                dt.net_amount AS net_amount,
                dt.tax_amount AS tax_amount,
                dt.rate AS tax_rate,
                dt.account AS account,
                dt.account_head AS account_head,
                dt.remarks AS remarks
            FROM `tabGL Payment Item` AS dt
            LEFT JOIN `tabGL Payment` AS d ON d.name = dt.parent
            LEFT JOIN `tabAccount` AS a ON a.name = dt.account_head
            WHERE {glp_clauses}
        """.format(
            **clauses
        ),
        values=values,
        as_dict=1,
    )

    def make_doc(x):
        if x.doctype:
            inv = frappe.get_doc(x)
            inv.items = invoice_items.get(x.get("name"), [])
            inv.taxes = invoice_taxes.get(x.get("name"), [])
            return inv
        inv = frappe.get_doc((merge({"doctype": clauses.get("doctype")}, x)))
        inv.items = [
            frappe._dict(
                {
                    "item_code": x.get("account"),
                    "item_name": x.get("remarks"),
                    "net_amount": x.get("net_amount"),
                }
            )
        ]
        inv.taxes = [
            frappe._dict(
                {
                    "item_wise_tax_detail": json.dumps(
                        {
                            x.get("account"): [
                                x.get("tax_rate") or 0,
                                x.get("tax_amount") or 0,
                            ]
                        }
                    )
                }
            )
        ]
        return inv

    def breakup_taxes(doc):
        tax, amount = get_itemised_tax_breakup_data(doc)
        # signatures
        # tax {item_code: {tax_description: {"tax_rate": tax_rate, "tax_amount": tax_amount}}}
        # amount {item_code: taxable_amount}
        def get_amounts(item_code):
            taxable_amount = amount.get(item_code, 0)
            vat_amount = sum(
                [x.get("tax_amount") for x in tax.get(item_code, {}).values()]
            )
            return {
                "taxable_amount": taxable_amount,
                "vat_amount": vat_amount,
                "total_amount": taxable_amount + vat_amount,
            }

        def get_item_name(item_code):
            return compose(
                excepts(StopIteration, first, lambda _: item_code),
                partial(map, lambda x: x.item_name),
                lambda: filter(lambda x: x.item_code == item_code, doc.items),
            )()

        def get_cost_center(item_code):
            return compose(
                excepts(StopIteration, first, lambda _: item_code),
                partial(map, lambda x: x.cost_center),
                lambda: filter(lambda x: x.item_code == item_code, doc.items),
            )()

        def get_branch(item_code):
            return compose(
                excepts(StopIteration, first, lambda _: item_code),
                partial(map, lambda x: x.pb_branch),
                lambda: filter(lambda x: x.item_code == item_code, doc.items),
            )()

        return [
            merge(
                {
                    "invoice": doc.name,
                    "date": doc.posting_date,
                    "vat_account_no": doc.tax_id,
                    "party_name": doc.get(clauses.get("party_name")),
                    "description": get_item_name(x),
                    "cost_center": get_cost_center(x),
                    "branch": get_branch(x),
                },
                get_amounts(x),
            )
            for x in amount
        ]

    def filter_type(row):
        if values.get("vat_type") == "Standard Rated":
            return row.get("vat_amount") != 0
        if values.get("vat_type") == "Zero Rated":
            return row.get("vat_amount") == 0
        return True

    make_row = compose(breakup_taxes, make_doc)
    make_list = compose(
        partial(sorted, key=lambda x: (x.get("date"), x.get("invoice"))),
        partial(filter, filter_type),
        concat,
    )
    return make_list([make_row(x) for x in invoices + gl_payments])


def _get_child_table_rows(query, docs):
    if not docs:
        return {}
    return groupby(
        "parent",
        frappe.db.sql(
            query, values={"docnames": [x.get("name") for x in docs]}, as_dict=1,
        ),
    )

# for company currency amout and tax
@erpnext.allow_regional
def get_itemised_tax_breakup_data(doc):
    itemised_tax = get_itemised_tax(doc.taxes)

    itemised_taxable_amount = get_itemised_taxable_amount(doc.items)

    return itemised_tax, itemised_taxable_amount


def get_itemised_tax(taxes, with_tax_account=False):
    itemised_tax = {}
    for tax in taxes:
        if getattr(tax, "category", None) and tax.category == "Valuation":
            continue

        item_tax_map = json.loads(tax.item_wise_tax_detail) if tax.item_wise_tax_detail else {}
        if item_tax_map:
            for item_code, tax_data in item_tax_map.items():
                itemised_tax.setdefault(item_code, frappe._dict())

                tax_rate = 0.0
                tax_amount = 0.0

                if isinstance(tax_data, list):
                    tax_rate = flt(tax_data[0])
                    tax_amount = flt(tax_data[1])
                else:
                    tax_rate = flt(tax_data)

                itemised_tax[item_code][tax.description] = frappe._dict(
                    dict(tax_rate=tax_rate, tax_amount=tax_amount)
                )

                if with_tax_account:
                    itemised_tax[item_code][tax.description].tax_account = tax.account_head

    return itemised_tax


def get_itemised_taxable_amount(items):
    itemised_taxable_amount = frappe._dict()
    for item in items:
        item_code = item.item_code or item.item_name
        itemised_taxable_amount.setdefault(item_code, 0)
        # itemised_taxable_amount[item_code] += item.base_net_amount
        if item.net_amount is not None:
            itemised_taxable_amount[item_code] += item.net_amount

    return itemised_taxable_amount
