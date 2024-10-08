# -*- coding: utf-8 -*-
# Copyright (c) 2021, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cstr, flt
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from erpnext.stock.get_item_details import (
    process_args,
    get_basic_details,
    get_default_income_account,
    get_default_expense_account,
    get_default_cost_center,
    get_default_supplier,
    calculate_service_end_date,
    get_conversion_factor,
    update_barcode_value,
)
from erpnext.stock.doctype.item.item import get_item_defaults
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from erpnext.setup.doctype.brand.brand import get_brand_defaults


class RepackRequest(Document):
    def validate(self):
        self.set_status()
        self.set_items_warehouse()

    def set_status(self, update=False, status=None):
        if self.is_new():
            if self.get("amended_from"):
                self.status = "Draft"
            return

        # Newly submitted is Pending
        if self.status == "Draft":
            self.status = "Pending"

        # Current status is not equal
        if self.status != status and update:
            self.add_comment("Label", _(status))
            self.db_set("status", status, update_modified=True)

    def set_items_warehouse(self):
        for item in self.items:
            item.warehouse = self.warehouse
        for item in self.to_items:
            item.warehouse = self.warehouse


# https://github.com/frappe/erpnext/blob/version-11/erpnext/stock/get_item_details.py
@frappe.whitelist()
def make_stock_entry(source_name, target_doc=None):
    def update_item(obj, target, source_parent):
        qty = (
            flt(flt(obj.stock_qty) - flt(obj.ordered_qty)) / target.conversion_factor
            if flt(obj.stock_qty) > flt(obj.ordered_qty)
            else 0
        )

        target.qty = qty
        target.transfer_qty = qty * obj.conversion_factor
        target.conversion_factor = obj.conversion_factor

        if obj.doctype == "Repack Request Item From":
            target.s_warehouse = obj.warehouse
        else:
            target.t_warehouse = obj.warehouse

    def set_missing_values(source, target):
        target.purpose = source.material_request_type
        target.pb_repack_request = source.name
        target.run_method("calculate_rate_and_amount")
        target.set_job_card_data()

    doclist = get_mapped_doc(
        "Repack Request",
        source_name,
        {
            "Repack Request": {
                "doctype": "Stock Entry",
                "field_map": {
                    "material_request_type": "stock_entry_type",
                },
                "validation": {
                    "docstatus": ["=", 1],
                    "material_request_type": [
                        "in",
                        ["Material Transfer", "Material Issue"],
                    ],
                },
            },
            "Repack Request Item From": {
                "doctype": "Stock Entry Detail",
                "field_map": {
                    "uom": "stock_uom",
                },
                "postprocess": update_item,
                "condition": lambda doc: doc.ordered_qty < doc.stock_qty,
            },
            "Repack Request Item To": {
                "doctype": "Stock Entry Detail",
                "field_map": {
                    "uom": "stock_uom",
                },
                "postprocess": update_item,
                "condition": lambda doc: doc.ordered_qty < doc.stock_qty,
            },
        },
        target_doc,
        set_missing_values,
    )

    return doclist


@frappe.whitelist()
def get_item_details(args):
    args = process_args(args)
    print(args)
    item = frappe.get_cached_doc("Item", args.item_code)
    _validate_item_details(args, item)
    return _get_basic_details(args, item)


def _validate_item_details(args, item):
    if not args.company:
        frappe.throw(frappe._("Please specify Company"))

    from erpnext.stock.doctype.item.item import validate_end_of_life

    validate_end_of_life(item.name, item.end_of_life, item.disabled)


def _get_basic_details(args, item):
    """
    :param args: {
                    "item_code": "",
                    "warehouse": None,
                    "customer": "",
                    "conversion_rate": 1.0,
                    "selling_price_list": None,
                    "price_list_currency": None,
                    "price_list_uom_dependant": None,
                    "plc_conversion_rate": 1.0,
                    "doctype": "",
                    "name": "",
                    "supplier": None,
                    "transaction_date": None,
                    "conversion_rate": 1.0,
                    "buying_price_list": None,
                    "is_subcontracted": "Yes" / "No",
                    "ignore_pricing_rule": 0/1
                    "project": "",
                    barcode: "",
                    serial_no: "",
                    currency: "",
                    update_stock: "",
                    price_list: "",
                    company: "",
                    order_type: "",
                    is_pos: "",
                    project: "",
                    qty: "",
                    stock_qty: "",
                    conversion_factor: ""
            }
    :param item: `item_code` of Item object
    :return: frappe._dict
    """

    if not item:
        item = frappe.get_doc("Item", args.get("item_code"))

    if item.variant_of:
        item.update_template_tables()

    from frappe.defaults import get_user_default_as_list

    user_default_warehouse_list = get_user_default_as_list("Warehouse")
    user_default_warehouse = (
        user_default_warehouse_list[0] if len(user_default_warehouse_list) == 1 else ""
    )

    item_defaults = get_item_defaults(item.name, args.company)
    item_group_defaults = get_item_group_defaults(item.name, args.company)
    brand_defaults = get_brand_defaults(item.name, args.company)

    warehouse = (
        args.get("set_warehouse")
        or user_default_warehouse
        or item_defaults.get("default_warehouse")
        or item_group_defaults.get("default_warehouse")
        or args.warehouse
    )

    if not args.get("material_request_type"):
        args["material_request_type"] = frappe.db.get_value(
            "Material Request", args.get("name"), "material_request_type", cache=True
        )

    # Set the UOM to the Default Sales UOM or Default Purchase UOM if configured in the Item Master
    if not args.uom:
        args.uom = item.purchase_uom if item.purchase_uom else item.stock_uom

    out = frappe._dict(
        {
            "item_code": item.name,
            "item_name": item.item_name,
            "description": cstr(item.description).strip(),
            "image": cstr(item.image).strip(),
            "warehouse": warehouse,
            "income_account": get_default_income_account(
                args, item_defaults, item_group_defaults, brand_defaults
            ),
            "expense_account": get_default_expense_account(
                args, item_defaults, item_group_defaults, brand_defaults
            ),
            "cost_center": get_default_cost_center(
                args, item_defaults, item_group_defaults, brand_defaults
            ),
            "has_serial_no": item.has_serial_no,
            "has_batch_no": item.has_batch_no,
            "batch_no": None,
            "uom": args.uom,
            "min_order_qty": flt(item.min_order_qty),
            "qty": args.qty or 1.0,
            "stock_qty": args.qty or 1.0,
            "price_list_rate": 0.0,
            "base_price_list_rate": 0.0,
            "rate": 0.0,
            "base_rate": 0.0,
            "amount": 0.0,
            "base_amount": 0.0,
            "net_rate": 0.0,
            "net_amount": 0.0,
            "discount_percentage": 0.0,
            "supplier": get_default_supplier(
                args, item_defaults, item_group_defaults, brand_defaults
            ),
            "update_stock": args.get("update_stock")
            if args.get("doctype") in ["Sales Invoice", "Purchase Invoice"]
            else 0,
            "delivered_by_supplier": item.delivered_by_supplier
            if args.get("doctype") in ["Sales Order", "Sales Invoice"]
            else 0,
            "is_fixed_asset": item.is_fixed_asset,
            "weight_per_unit": item.weight_per_unit,
            "weight_uom": item.weight_uom,
            "last_purchase_rate": item.last_purchase_rate
            if args.get("doctype") in ["Purchase Order"]
            else 0,
            "transaction_date": args.get("transaction_date"),
        }
    )

    if item.get("enable_deferred_revenue") or item.get("enable_deferred_expense"):
        out.update(calculate_service_end_date(args, item))

    # calculate conversion factor
    if item.stock_uom == args.uom:
        out.conversion_factor = 1.0
    else:
        out.conversion_factor = args.conversion_factor or get_conversion_factor(
            item.name, args.uom
        ).get("conversion_factor")

    args.conversion_factor = out.conversion_factor
    out.stock_qty = out.qty * out.conversion_factor

    # calculate last purchase rate
    from erpnext.buying.doctype.purchase_order.purchase_order import (
        item_last_purchase_rate,
    )

    out.last_purchase_rate = item_last_purchase_rate(
        args.name, args.conversion_rate, item.name, out.conversion_factor
    )

    # if default specified in item is for another company, fetch from company
    for d in [
        ["Account", "income_account", "default_income_account"],
        ["Account", "expense_account", "default_expense_account"],
        ["Cost Center", "cost_center", "cost_center"],
        ["Warehouse", "warehouse", ""],
    ]:
        if not out[d[1]]:
            out[d[1]] = (
                frappe.get_cached_value("Company", args.company, d[2]) if d[2] else None
            )

    for fieldname in ("item_name", "item_group", "barcodes", "brand", "stock_uom"):
        out[fieldname] = item.get(fieldname)

    meta = frappe.get_meta(args.child_doctype)
    if meta.get_field("barcode"):
        update_barcode_value(out)

    return out
