# -*- coding: utf-8 -*-
# Copyright (c) 2019, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from pos_bahrain.doc_events.purchase_receipt import set_or_create_batch
from pos_bahrain.doc_events.sales_invoice import set_cost_center
from erpnext.controllers.queries import get_match_cond


def before_validate(doc, method):
    set_or_create_batch(doc, method)


def before_save(doc, method):
    set_cost_center(doc)




@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_batch_no(doctype, txt, searchfield, start, page_len, filters):
	cond = ""
	is_return = filters.get("is_return_invoice")
	if not is_return and filters.get("posting_date"):
		cond = "and (batch.expiry_date is null or batch.expiry_date >= %(posting_date)s)"
	batch_nos = None
	args = {
		'item_code': filters.get("item_code"),
		'warehouse': filters.get("warehouse"),
		'posting_date': filters.get('posting_date'),
		'txt': "%{0}%".format(txt),
		"start": start,
		"page_len": page_len
	}

	having_clause = "having sum(sle.actual_qty) > 0"
	if filters.get("is_return"):
		having_clause = ""

	if args.get('warehouse'):
		batch_nos = frappe.db.sql("""select sle.batch_no, round(sum(sle.actual_qty),2), sle.stock_uom,
				concat('MFG-',batch.manufacturing_date), concat('EXP-',batch.expiry_date)
			from `tabStock Ledger Entry` sle
				INNER JOIN `tabBatch` batch on sle.batch_no = batch.name
			where
				batch.disabled = 0
				and sle.item_code = %(item_code)s
				and sle.warehouse = %(warehouse)s
				and (sle.batch_no like %(txt)s
				or batch.expiry_date like %(txt)s
				or batch.manufacturing_date like %(txt)s)
				and batch.docstatus < 2
				{cond}
				{match_conditions}
			group by batch_no {having_clause}
			order by batch.expiry_date, sle.batch_no desc
			limit %(start)s, %(page_len)s""".format(
				cond=cond,
				match_conditions=get_match_cond(doctype),
				having_clause = having_clause
			), args)

		return batch_nos
	else:
		return frappe.db.sql("""select name, concat('MFG-', manufacturing_date), concat('EXP-',expiry_date) from `tabBatch` batch
			where batch.disabled = 0
			and item = %(item_code)s
			and (name like %(txt)s
			or expiry_date like %(txt)s
			or manufacturing_date like %(txt)s)
			and docstatus < 2
			{0}
			{match_conditions}
			order by expiry_date, name desc
			limit %(start)s, %(page_len)s""".format(cond, match_conditions=get_match_cond(doctype)), args)
