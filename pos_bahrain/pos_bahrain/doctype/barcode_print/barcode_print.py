# -*- coding: utf-8 -*-
# Copyright (c) 2019, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from toolz import merge

from pos_bahrain.api.item import get_actual_qty
from pos_bahrain.utils import pick


class BarcodePrint(Document):
    def validate(self):
        mismatched_batches = []
        for item in self.items:
            if item.batch and item.item_code != frappe.db.get_value(
                "Batch", item.batch, "item"
            ):
                mismatched_batches.append(item)
        if mismatched_batches:
            frappe.throw(
                "Batches mismatched in rows: {}".format(
                    ", ".join(
                        [
                            "<strong>{}</strong>".format(x.idx)
                            for x in mismatched_batches
                        ]
                    )
                )
            )
    @frappe.whitelist()
    def set_items_from_reference(self):
        ref_doc = frappe.get_doc(self.print_dt, self.print_dn)

        if self.print_dt == "Stock Entry":
            self.set_warehouse = (
                ref_doc.from_warehouse
                if self.use_warehouse == "Source"
                else ref_doc.to_warehouse
            )
        else:
            self.set_warehouse = ref_doc.set_warehouse
            self.use_warehouse = None  # Target, Source

        self.items = []
        for ref_item in ref_doc.items:
            items = merge(
                pick(
                    ["item_code", "item_name", "qty", "uom", "rate", "warehouse"],
                    ref_item.as_dict(),
                ),
                {
                    "batch": ref_item.batch_no,
                    "expiry_date": _get_expiry_date(ref_item),
                    "actual_qty": _get_actual_qty(ref_item, self.set_warehouse),
                },
            )
            self.append("items", items)


def _get_expiry_date(item):
    if (
        item.batch_no
        and not item.pb_expiry_date
        and frappe.get_cached_value("Item", item.item_code, "has_expiry_date")
    ):
        return frappe.db.get_value("Batch", item.batch_no, "expiry_date")
    return item.pb_expiry_date


def _get_actual_qty(item, warehouse):
    if warehouse:
        return get_actual_qty(item.item_code, warehouse, item.batch_no)
    return 0
