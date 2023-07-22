# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import frappe
from six import string_types
from toolz import merge, concat


@frappe.whitelist()
def make_invoice(pos_profile, doc_list={}, email_queue_list={}, customers_list={}):
    from erpnext.accounts.doctype.sales_invoice.pos import make_invoice

    result = make_invoice(
        pos_profile,
        doc_list=[],
        email_queue_list=email_queue_list,
        customers_list=customers_list,
    )

    # update customers list (for v12)
    _update_contact_phones(customers_list)

    docs = json.loads(doc_list) if isinstance(doc_list, string_types) else doc_list

    prev_synced_invoices = [
        x[0]
        for x in frappe.get_all(
            "Sales Invoice",
            fields="offline_pos_name",
            filters={
                "offline_pos_name": ("in", list(concat([x.keys() for x in docs])))
            },
            as_list=1,
        )
    ]

    for doc_list_item in docs:
        for name, doc in doc_list_item.items():
            frappe.utils.background_jobs.enqueue(
                make_invoice,
                job_name=name,
                doc_list=[{name: doc}],
                pos_profile=pos_profile,
            )

    return merge(result, {"invoice": prev_synced_invoices})


def _update_contact_phones(customers_list):
    from erpnext.accounts.doctype.sales_invoice.pos import get_customer_id

    if isinstance(customers_list, string_types):
        customers_list = json.loads(customers_list)

    for customer, data in customers_list.items():
        data = json.loads(data)
        customer_id = get_customer_id(data, customer)

        # Contact DocType
        contact_name = frappe.db.get_value(
            "Dynamic Link",
            {
                "link_doctype": "Customer",
                "link_name": customer_id,
                "parenttype": "Contact",
            },
            "parent",
        )

        if contact_name:
            contact_doc = frappe.get_doc("Contact", contact_name)

            phone = data.get("phone")
            phone_nos = [x.phone for x in contact_doc.phone_nos]
            if phone not in phone_nos:
                contact_doc.add_phone(phone)

            contact_doc.save(ignore_permissions=True)
