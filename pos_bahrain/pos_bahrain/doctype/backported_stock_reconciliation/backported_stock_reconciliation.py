# -*- coding: utf-8 -*-
# Copyright (c) 2020,     9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import erpnext
from erpnext.stock.doctype.stock_reconciliation.stock_reconciliation import (
    StockReconciliation,
    EmptyStockReconciliationItemsError,
    OpeningEntryAccountError,
)
from erpnext.stock.stock_ledger import update_entries_after
from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos
from erpnext.stock.utils import (
    get_stock_balance,
    get_incoming_rate,
)
from erpnext.stock.doctype.batch.batch import get_batch_qty


class BackportedStockReconciliation(StockReconciliation):
    def validate(self):
        super().validate()
        if self._action == "submit":
            self.make_batches("warehouse")

    def on_submit(self):
        super().on_submit()
        _update_serial_nos_after_submit(self, "items")

    def remove_items_with_no_change(self):
        """Remove items if qty or rate is not changed"""
        self.difference_amount = 0.0

        def _changed(item):
            item_dict = get_stock_balance_for(
                item.item_code,
                item.warehouse,
                self.posting_date,
                self.posting_time,
                batch_no=item.batch_no,
            )

            if (
                (item.qty is None or item.qty == item_dict.get("qty"))
                and (
                    item.valuation_rate is None
                    or item.valuation_rate == item_dict.get("rate")
                )
                and (
                    not item.serial_no
                    or (item.serial_no == item_dict.get("serial_nos"))
                )
            ):
                return False
            else:
                # set default as current rates
                if item.qty is None:
                    item.qty = item_dict.get("qty")

                if item.valuation_rate is None:
                    item.valuation_rate = item_dict.get("rate")

                if item_dict.get("serial_nos"):
                    item.current_serial_no = item_dict.get("serial_nos")

                item.current_qty = item_dict.get("qty")
                item.current_valuation_rate = item_dict.get("rate")
                self.difference_amount += frappe.utils.flt(
                    item.qty, item.precision("qty")
                ) * frappe.utils.flt(
                    item.valuation_rate or item_dict.get("rate"),
                    item.precision("valuation_rate"),
                ) - frappe.utils.flt(
                    item_dict.get("qty"), item.precision("qty")
                ) * frappe.utils.flt(
                    item_dict.get("rate"), item.precision("valuation_rate")
                )
                return True

        items = list(filter(lambda d: _changed(d), self.items))

        if not items:
            frappe.throw(
                frappe._("None of the items have any change in quantity or value."),
                EmptyStockReconciliationItemsError,
            )

        elif len(items) != len(self.items):
            self.items = items
            for i, item in enumerate(self.items):
                item.idx = i + 1
            frappe.msgprint(
                frappe._("Removed items with no change in quantity or value.")
            )

    def validate_data(self):
        def _get_msg(row_num, msg):
            return frappe._("Row # {0}: ").format(row_num + 1) + msg

        self.validation_messages = []
        item_warehouse_combinations = []

        default_currency = frappe.db.get_default("currency")

        for row_num, row in enumerate(self.items):
            # find duplicates
            key = [row.item_code, row.warehouse]
            for field in ["serial_no", "batch_no"]:
                if row.get(field):
                    key.append(row.get(field))

            if key in item_warehouse_combinations:
                self.validation_messages.append(
                    _get_msg(row_num, frappe._("Duplicate entry"))
                )
            else:
                item_warehouse_combinations.append(key)

            self.validate_item(row.item_code, row)

            # validate warehouse
            if not frappe.db.get_value("Warehouse", row.warehouse):
                self.validation_messages.append(
                    _get_msg(row_num, frappe._("Warehouse not found in the system"))
                )

            # if both not specified
            if row.qty in ["", None] and row.valuation_rate in ["", None]:
                self.validation_messages.append(
                    _get_msg(
                        row_num,
                        frappe._(
                            "Please specify either Quantity or Valuation Rate or both"
                        ),
                    )
                )

            # do not allow negative quantity
            if frappe.utils.flt(row.qty) < 0:
                self.validation_messages.append(
                    _get_msg(row_num, frappe._("Negative Quantity is not allowed"))
                )

            # do not allow negative valuation
            if frappe.utils.flt(row.valuation_rate) < 0:
                self.validation_messages.append(
                    _get_msg(
                        row_num, frappe._("Negative Valuation Rate is not allowed")
                    )
                )

            if row.qty and row.valuation_rate in ["", None]:
                row.valuation_rate = get_stock_balance(
                    row.item_code,
                    row.warehouse,
                    self.posting_date,
                    self.posting_time,
                    with_valuation_rate=True,
                )[1]
                if not row.valuation_rate:
                    # try if there is a buying price list in default currency
                    buying_rate = frappe.db.get_value(
                        "Item Price",
                        {
                            "item_code": row.item_code,
                            "buying": 1,
                            "currency": default_currency,
                        },
                        "price_list_rate",
                    )
                    if buying_rate:
                        row.valuation_rate = buying_rate

                    else:
                        # get valuation rate from Item
                        row.valuation_rate = frappe.get_value(
                            "Item", row.item_code, "valuation_rate"
                        )

        # throw all validation messages
        if self.validation_messages:
            for msg in self.validation_messages:
                frappe.msgprint(msg)

            raise frappe.ValidationError(self.validation_messages)

    def validate_item(self, item_code, row):
        from erpnext.stock.doctype.item.item import (
            validate_end_of_life,
            validate_is_stock_item,
            validate_cancelled_item,
        )

        # using try except to catch all validation msgs and display together

        try:
            item = frappe.get_doc("Item", item_code)

            # end of life and stock item
            validate_end_of_life(item_code, item.end_of_life, item.disabled)
            validate_is_stock_item(item_code, item.is_stock_item)

            # item should not be serialized
            if item.has_serial_no and not row.serial_no and not item.serial_no_series:
                raise frappe.ValidationError(
                    frappe._("Serial no(s) required for serialized item {0}").format(
                        item_code
                    )
                )

            # item managed batch-wise not allowed
            if item.has_batch_no and not row.batch_no and not item.create_new_batch:
                raise frappe.ValidationError(
                    frappe._("Batch no is required for batched item {0}").format(
                        item_code
                    )
                )

            # docstatus should be < 2
            validate_cancelled_item(item_code, item.docstatus)

        except Exception as e:
            self.validation_messages.append(
                frappe._("Row # ") + ("%d: " % (row.idx)) + frappe.utils.cstr(e)
            )

    def update_stock_ledger(self):
        """    find difference between current and expected entries
            and create stock ledger entries based on the difference"""
        from erpnext.stock.stock_ledger import get_previous_sle

        sl_entries = []
        has_serial_no = False
        for row in self.items:
            item = frappe.get_doc("Item", row.item_code)
            if item.has_serial_no or item.has_batch_no:
                has_serial_no = True
                self.get_sle_for_serialized_items(row, sl_entries)
            else:
                if row.serial_no or row.batch_no:
                    frappe.throw(
                        frappe._(
                            "Row #{0}: Item {1} is not a Serialized/Batched Item. It cannot have a Serial No/Batch No against it."
                        ).format(row.idx, frappe.bold(row.item_code))
                    )
                previous_sle = get_previous_sle(
                    {
                        "item_code": row.item_code,
                        "warehouse": row.warehouse,
                        "posting_date": self.posting_date,
                        "posting_time": self.posting_time,
                    }
                )

                if previous_sle:
                    if row.qty in ("", None):
                        row.qty = previous_sle.get("qty_after_transaction", 0)

                    if row.valuation_rate in ("", None):
                        row.valuation_rate = previous_sle.get("valuation_rate", 0)

                if row.qty and not row.valuation_rate:
                    frappe.throw(
                        frappe._(
                            "Valuation Rate required for Item {0} at row {1}"
                        ).format(row.item_code, row.idx)
                    )

                if (
                    previous_sle
                    and row.qty == previous_sle.get("qty_after_transaction")
                    and (
                        row.valuation_rate == previous_sle.get("valuation_rate")
                        or row.qty == 0
                    )
                ) or (not previous_sle and not row.qty):
                    continue

                sl_entries.append(self.get_sle_for_items(row))

        if sl_entries:
            if has_serial_no:
                sl_entries = self.merge_similar_item_serial_nos(sl_entries)

            self.make_sl_entries(sl_entries)

        if has_serial_no and sl_entries:
            self.update_valuation_rate_for_serial_no()

    def get_sle_for_serialized_items(self, row, sl_entries):
        from erpnext.stock.stock_ledger import get_previous_sle

        serial_nos = get_serial_nos(row.serial_no)

        # To issue existing serial nos
        if row.current_qty and (row.current_serial_no or row.batch_no):
            args = self.get_sle_for_items(row)
            args.update(
                {
                    "actual_qty": -1 * row.current_qty,
                    "serial_no": row.current_serial_no,
                    "batch_no": row.batch_no,
                    "valuation_rate": row.current_valuation_rate,
                }
            )

            if row.current_serial_no:
                args.update(
                    {"qty_after_transaction": 0,}
                )

            sl_entries.append(args)

        for serial_no in serial_nos:
            args = self.get_sle_for_items(row, [serial_no])

            previous_sle = get_previous_sle(
                {
                    "item_code": row.item_code,
                    "posting_date": self.posting_date,
                    "posting_time": self.posting_time,
                    "serial_no": serial_no,
                }
            )

            if previous_sle and row.warehouse != previous_sle.get("warehouse"):
                # If serial no exists in different warehouse

                new_args = args.copy()
                new_args.update(
                    {
                        "actual_qty": -1,
                        "qty_after_transaction": frappe.utils.cint(
                            previous_sle.get("qty_after_transaction")
                        )
                        - 1,
                        "warehouse": previous_sle.get("warehouse", "") or row.warehouse,
                        "valuation_rate": previous_sle.get("valuation_rate"),
                    }
                )

                sl_entries.append(new_args)

        if row.qty:
            args = self.get_sle_for_items(row)

            args.update(
                {
                    "actual_qty": row.qty,
                    "incoming_rate": row.valuation_rate,
                    "valuation_rate": row.valuation_rate,
                }
            )

            sl_entries.append(args)

        if serial_nos == get_serial_nos(row.current_serial_no):
            # update valuation rate
            self.update_valuation_rate_for_serial_nos(row, serial_nos)

    def update_valuation_rate_for_serial_no(self):
        for d in self.items:
            if not d.serial_no:
                continue

            serial_nos = get_serial_nos(d.serial_no)
            self.update_valuation_rate_for_serial_nos(d, serial_nos)

    def update_valuation_rate_for_serial_nos(self, row, serial_nos):
        valuation_rate = (
            row.valuation_rate if self.docstatus == 1 else row.current_valuation_rate
        )
        if valuation_rate is None:
            return

        for d in serial_nos:
            frappe.db.set_value("Serial No", d, "purchase_rate", valuation_rate)

    def get_sle_for_items(self, row, serial_nos=None):
        """Insert Stock Ledger Entries"""

        if not serial_nos and row.serial_no:
            serial_nos = get_serial_nos(row.serial_no)

        data = frappe._dict(
            {
                "doctype": "Stock Ledger Entry",
                "item_code": row.item_code,
                "warehouse": row.warehouse,
                "posting_date": self.posting_date,
                "posting_time": self.posting_time,
                "voucher_type": self.doctype,
                "voucher_no": self.name,
                "voucher_detail_no": row.name,
                "company": self.company,
                "stock_uom": frappe.db.get_value("Item", row.item_code, "stock_uom"),
                "is_cancelled": "No" if self.docstatus != 2 else "Yes",
                "serial_no": "\n".join(serial_nos) if serial_nos else "",
                "batch_no": row.batch_no,
                "valuation_rate": frappe.utils.flt(
                    row.valuation_rate, row.precision("valuation_rate")
                ),
            }
        )

        if not row.batch_no:
            data.qty_after_transaction = frappe.utils.flt(row.qty, row.precision("qty"))

        return data

    def delete_and_repost_sle(self):
        """    Delete Stock Ledger Entries related to this voucher
            and repost future Stock Ledger Entries"""

        existing_entries = frappe.db.sql(
            """select distinct item_code, warehouse
            from `tabStock Ledger Entry` where voucher_type=%s and voucher_no=%s""",
            (self.doctype, self.name),
            as_dict=1,
        )

        # delete entries
        frappe.db.sql(
            """delete from `tabStock Ledger Entry`
            where voucher_type=%s and voucher_no=%s""",
            (self.doctype, self.name),
        )

        sl_entries = []

        has_serial_no = False
        for row in self.items:
            if row.serial_no or row.batch_no or row.current_serial_no:
                has_serial_no = True
                self.get_sle_for_serialized_items(row, sl_entries)

        if sl_entries:
            if has_serial_no:
                sl_entries = self.merge_similar_item_serial_nos(sl_entries)

            sl_entries.reverse()
            allow_negative_stock = frappe.db.get_value(
                "Stock Settings", None, "allow_negative_stock"
            )
            self.make_sl_entries(sl_entries, allow_negative_stock=allow_negative_stock)

        # repost future entries for selected item_code, warehouse
        for entries in existing_entries:
            update_entries_after(
                {
                    "item_code": entries.item_code,
                    "warehouse": entries.warehouse,
                    "posting_date": self.posting_date,
                    "posting_time": self.posting_time,
                }
            )

    def merge_similar_item_serial_nos(self, sl_entries):
        # If user has put the same item in multiple row with different serial no
        new_sl_entries = []
        merge_similar_entries = {}

        for d in sl_entries:
            if not d.serial_no or d.actual_qty < 0:
                new_sl_entries.append(d)
                continue

            key = (d.item_code, d.warehouse)
            if key not in merge_similar_entries:
                merge_similar_entries[key] = d
            elif d.serial_no:
                data = merge_similar_entries[key]
                data.actual_qty += d.actual_qty
                data.qty_after_transaction += d.qty_after_transaction

                data.valuation_rate = (
                    data.valuation_rate + d.valuation_rate
                ) / data.actual_qty
                data.serial_no += "\n" + d.serial_no

                if data.incoming_rate:
                    data.incoming_rate = (
                        data.incoming_rate + d.incoming_rate
                    ) / data.actual_qty

        for key, value in merge_similar_entries.items():
            new_sl_entries.append(value)

        return new_sl_entries

    def validate_expense_account(self):
        if not frappe.utils.cint(erpnext.is_perpetual_inventory_enabled(self.company)):
            return

        if not self.expense_account:
            frappe.throw(frappe._("Please enter Expense Account"))
        elif self.purpose == "Opening Stock" or not frappe.db.sql(
            """select name from `tabStock Ledger Entry` limit 1"""
        ):
            if (
                frappe.db.get_value("Account", self.expense_account, "report_type")
                == "Profit and Loss"
            ):
                frappe.throw(
                    frappe._(
                        "Difference Account must be a Asset/Liability type account, since this Stock Reconciliation is an Opening Entry"
                    ),
                    OpeningEntryAccountError,
                )


@frappe.whitelist()
def get_items(warehouse, posting_date, posting_time, company):
    lft, rgt = frappe.db.get_value("Warehouse", warehouse, ["lft", "rgt"])
    items = frappe.db.sql(
        """
            select i.name, i.item_name, bin.warehouse
            from tabBin bin, tabItem i
            where i.name=bin.item_code and i.disabled=0 and i.is_stock_item = 1
            and i.has_variants = 0 and i.has_serial_no = 0 and i.has_batch_no = 0
            and exists(select name from `tabWarehouse` where lft >= %s and rgt <= %s and name=bin.warehouse)
        """,
        (lft, rgt),
    )

    items += frappe.db.sql(
        """
            select i.name, i.item_name, id.default_warehouse
            from tabItem i, `tabItem Default` id
            where i.name = id.parent
                and exists(select name from `tabWarehouse` where lft >= %s and rgt <= %s and name=id.default_warehouse)
                and i.is_stock_item = 1 and i.has_serial_no = 0 and i.has_batch_no = 0
                and i.has_variants = 0 and i.disabled = 0 and id.company=%s
            group by i.name
        """,
        (lft, rgt, company),
    )

    res = []
    for d in set(items):
        stock_bal = get_stock_balance(
            d[0], d[2], posting_date, posting_time, with_valuation_rate=True
        )

        if frappe.db.get_value("Item", d[0], "disabled") == 0:
            res.append(
                {
                    "item_code": d[0],
                    "warehouse": d[2],
                    "qty": stock_bal[0],
                    "item_name": d[1],
                    "valuation_rate": stock_bal[1],
                    "current_qty": stock_bal[0],
                    "current_valuation_rate": stock_bal[1],
                }
            )

    return res


@frappe.whitelist()
def get_stock_balance_for(
    item_code,
    warehouse,
    posting_date,
    posting_time,
    batch_no=None,
    with_valuation_rate=True,
):
    frappe.has_permission("Backported Stock Reconciliation", "write", throw=True)

    item_dict = frappe.db.get_value(
        "Item", item_code, ["has_serial_no", "has_batch_no"], as_dict=1
    )

    serial_nos = ""
    if item_dict.get("has_serial_no"):
        qty, rate, serial_nos = _get_qty_rate_for_serial_nos(
            item_code, warehouse, posting_date, posting_time, item_dict
        )
    else:
        qty, rate = get_stock_balance(
            item_code,
            warehouse,
            posting_date,
            posting_time,
            with_valuation_rate=with_valuation_rate,
        )

    if item_dict.get("has_batch_no"):
        qty = get_batch_qty(batch_no, warehouse) or 0
        print(get_batch_qty(batch_no, warehouse))

    return {"qty": qty, "rate": rate, "serial_nos": serial_nos}


def _get_qty_rate_for_serial_nos(
    item_code, warehouse, posting_date, posting_time, item_dict
):
    args = {
        "item_code": item_code,
        "warehouse": warehouse,
        "posting_date": posting_date,
        "posting_time": posting_time,
    }

    serial_nos_list = [
        serial_no.get("name")
        for serial_no in frappe.db.sql(
            """
                SELECT name FFROM `tabSerial No` WHERE
                    item_code = %(item_code)s AND
                    warehouse = %(warehouse)s AND
                    timestamp(purchase_date, purchase_time) <= timestamp(%(posting_date)s, %(posting_time)s)
            """,
            args,
            as_dict=1,
        )
    ]

    qty = len(serial_nos_list)
    serial_nos = "\n".join(serial_nos_list)
    args.update({"qty": qty, "serial_nos": serial_nos})

    rate = get_incoming_rate(args, raise_error_if_no_rate=False) or 0

    return qty, rate, serial_nos


def _update_serial_nos_after_submit(controller, parentfield):
    stock_ledger_entries = frappe.db.sql(
        """select voucher_detail_no, serial_no, actual_qty, warehouse
        from `tabStock Ledger Entry` where voucher_type=%s and voucher_no=%s""",
        (controller.doctype, controller.name),
        as_dict=True,
    )

    if not stock_ledger_entries:
        return

    for d in controller.get(parentfield):
        if d.serial_no:
            continue

        update_rejected_serial_nos = False
        accepted_serial_nos_updated = False
        warehouse = d.warehouse
        qty = d.qty

        for sle in stock_ledger_entries:
            if sle.voucher_detail_no == d.name:
                if (
                    not accepted_serial_nos_updated
                    and qty
                    and abs(sle.actual_qty) == qty
                    and sle.warehouse == warehouse
                    and sle.serial_no != d.serial_no
                ):
                    d.serial_no = sle.serial_no
                    frappe.db.set_value(d.doctype, d.name, "serial_no", sle.serial_no)
                    accepted_serial_nos_updated = True
                    if not update_rejected_serial_nos:
                        break
                elif (
                    update_rejected_serial_nos
                    and abs(sle.actual_qty) == d.rejected_qty
                    and sle.warehouse == d.rejected_warehouse
                    and sle.serial_no != d.rejected_serial_no
                ):
                    d.rejected_serial_no = sle.serial_no
                    frappe.db.set_value(
                        d.doctype, d.name, "rejected_serial_no", sle.serial_no
                    )
                    update_rejected_serial_nos = False
                    if accepted_serial_nos_updated:
                        break
