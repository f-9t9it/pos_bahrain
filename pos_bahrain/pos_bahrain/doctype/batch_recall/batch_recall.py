# -*- coding: utf-8 -*-
# pylint: disable=no-member
# Copyright (c) 2020, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from toolz.curried import groupby, merge, first, excepts


class BatchRecall(Document):
    def fetch_data(self):
        self._fetch_invoices()
        item_details = frappe.db.sql(
            """
            SELECT 
                b.item AS item_code,
                i.item_name AS item_name 
            FROM `tabBatch` AS b
            JOIN `tabItem` AS i ON i.name = b.item
            WHERE b.name = %s
            """,
            self.batch,
            as_dict=1,
        )
        item_details = item_details[0]
        self.item_name = item_details.get("item_name")
        self.item_code = item_details.get("item_code")

    def send_emails(self):
        if not self.email_template:
            frappe.throw(frappe._("Email Template required to send emails"))

        subject, response = frappe.get_cached_value(
            "Email Template", self.email_template, ["subject", "response"]
        )
        get_first_details = excepts(StopIteration, first, lambda _: {})

        for contact_email, invoices in groupby(
            "contact_email", [x.as_dict() for x in self.invoices if x.contact_email]
        ).items():
            context = merge(
                get_first_details(invoices), {"batch": self.batch, "invoices": invoices}
            )

            _subject = frappe.render_template(subject, context)
            _message = frappe.render_template(response, context)
            frappe.sendmail(
                recipients=[contact_email],
                subject=_subject,
                message=_message,
                reference_doctype="Sales Invoice",
                reference_name=context.get("sales_invoice"),
            )

    def _fetch_invoices(self):
        invoices = frappe.db.sql(
            """
                SELECT
                    si.name AS sales_invoice,
                    si.posting_date,
                    si.grand_total,
                    si.customer,
                    si.customer_name,
                    si.contact_email,
                    SUM(sii.qty) AS qty
                FROM `tabSales Invoice Item` AS sii
                LEFT JOIN  `tabSales Invoice` AS si ON
                    si.name = sii.parent
                WHERE si.docstatus = 1 AND sii.batch_no = %(batch_no)s
                GROUP BY si.name
            """,
            values={"batch_no": self.batch},
            as_dict=1,
        )
        self.invoices = []
        for invoice in invoices:
            self.append("invoices", invoice)

        self.no_of_invoices = len(invoices)
        self.no_of_customers = len(set([x.get("customer") for x in invoices]))
        self.total_qty_sold = sum([x.get("qty") for x in invoices])
