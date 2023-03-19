# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from datetime import datetime
from functools import partial, reduce
from toolz import groupby, pluck, compose, merge, keyfilter

def execute(filters=None):
	mop = _get_mop()

	columns = _get_columns(mop, filters)
	data = _get_data(_get_clauses(filters), filters, mop)

	return columns, data


def _get_columns(mop, filters):
	summary_view = filters.get('summary_view')
	show_customer_info = filters.get('show_customer_info')
	show_ref_info = filters.get('show_reference_info')
	columns = []
	show_creator = filters.get('show_creator')

	def make_column(key, label=None, type="Data", options=None, width=120):
		return {
			"label": _(label or key.replace("_", " ").title()),
			"fieldname": key,
			"fieldtype": type,
			"options": options,
			"width": width
		}

	if not summary_view:
		columns.append(
			make_column("invoice", type="Link", options="Sales Invoice")
		)
	if not summary_view:
		columns.append(
			make_column("pe", type="Link", options="Payment Entry",width='50')
		)

	columns.append(make_column("posting_date", "Date", type="Date"))

	if not summary_view:
		columns.append(
			make_column("posting_time", "Time", type="Time")
		)

	if show_customer_info:
		columns.extend([
			make_column("customer", "Customer", "Link", "Customer"),
			make_column("customer_name", "Customer Name"),
			make_column("mobile_no", "Mobile No")
		])

	if show_ref_info:
		columns.extend([
			make_column("ref_no", "Ref No"),
			# make_column("ref_date", "Ref Date"),
		])
	if show_creator:
		columns.extend([
			make_column("show_creator", "Show Creator"),
		])

	print(columns)

	def make_mop_column(row):
		return make_column(
			row.replace(" ", "_").lower(),
			type="Float"
		)

	columns.extend(
		list(map(make_mop_column, mop))
		+ [make_column("total", type="Float")]
	)

	return columns


def _get_data(clauses, filters, mop):
	result = frappe.db.sql(
		"""
			SELECT
				si.name AS invoice,
				"" as pe,
				pp.warehouse AS warehouse,
				si.posting_date AS posting_date,
				si.posting_time AS posting_time,
				si.change_amount AS change_amount,
				sip.mode_of_payment AS mode_of_payment,
				sip.amount as amt,
				case when (si.is_pos=1) then sip.amount else 0 end as amount,
				sip.pb_reference_no AS ref_no,
				usert.full_name as show_creator,
				sip.pb_reference_date AS ref_date,
				si.customer AS customer,
				si.customer_name AS customer_name,
				c.mobile_no AS mobile_no
			FROM `tabSales Invoice` AS si
			JOIN `tabCustomer` AS c ON
				c.name = si.customer
			LEFT JOIN `tabSales Invoice Payment` AS sip ON
				sip.parent = si.name 
			LEFT JOIN `tabPOS Profile` AS pp ON
				pp.name = si.pos_profile
			LEFT JOIN
				`tabUser` as usert ON usert.email = si.owner
			WHERE {clauses}
		""".format(
			clauses=clauses
		),
		values=filters,
		as_dict=1
	)

	clause = {"query_doc":filters.query_doc, "start":filters.from_date, "end":filters.to_date}
	if(filters.query_doctype == 'POS Profile'):
		pe_clauses = ("pe.pb_pos_profile = '%(query_doc)s' AND pe.posting_date BETWEEN '%(start)s' AND '%(end)s'"%clause)
	elif(filters.query_doctype == 'Warehouse'):
		pe_clauses = ("pp.warehouse = '%(query_doc)s' AND pe.posting_date BETWEEN '%(start)s' AND '%(end)s'"%clause)

	payment_entry = frappe.db.sql(
		"""SELECT
				pe.name AS invoice,
				pe.name as pe,
				pp.warehouse AS warehouse,
				pe.posting_date AS posting_date,
				pe.pb_posting_time AS posting_time,
				0 AS change_amount,
				pe.mode_of_payment AS mode_of_payment,
				pe.paid_amount AS amount,
				pe.reference_no AS ref_no,
				pe.reference_date AS ref_date,
				pe.party_name AS customer,
				pe.party_name AS customer_name,
				c.mobile_no AS mobile_no
			FROM `tabPayment Entry` AS pe
			LEFT JOIN `tabCustomer` AS c ON
				c.name = pe.party_name
			LEFT JOIN `tabPOS Profile` AS pp ON
				pp.name = pe.pb_pos_profile
			WHERE {pe_clauses} AND pe.docstatus = 1
		""".format(
			pe_clauses = pe_clauses
		),
		values=filters,
		as_dict=1
	)

	result = result + payment_entry

	result = _sum_invoice_payments(
		groupby('invoice', result),
		mop
	)

	if filters.get('summary_view'):
		result = _summarize_payments(
			groupby('posting_date', result),
			mop
		)

	def get_sort_key(item):
		if filters.get("summary_view"):
			return item["posting_date"]
		return datetime.combine(item["posting_date"], datetime.min.time()) + item["posting_time"]

	return sorted(result, key=get_sort_key)


def _summarize_payments(result, mop):
	summary = []

	mop_cols = [
		mop_col.replace(" ", "_").lower()
		for mop_col in mop
	]

	def make_summary_row(_, row):
		for col in mop_cols:
			_[col] = _[col] + row[col]

		_['posting_time'] = None
		_['invoice'] = None

		return _

	for key, payments in result.items():
		summary.append(
			reduce(make_summary_row, payments)
		)

	get_row_total = compose(
		sum, lambda x: x.values(), partial(keyfilter, lambda x: x in mop_cols)
	)

	return [merge(row, {'total': get_row_total(row)}) for row in summary]


def _sum_invoice_payments(invoice_payments, mop):
	data = []

	mop_cols = list(
		map(lambda x: x.replace(" ", "_").lower(), mop)
	)

	def make_change_total(row):
		row['cash'] = row.get('cash') - row.get('change')
		row['total'] = sum([
			row[mop_col] for mop_col in mop_cols
		])

		for mop_col in (mop_cols + ['total']):
			row[mop_col] = round(row.get(mop_col), 3)

		return row

	make_payment_row = partial(_make_payment_row, mop)

	for key, payments in invoice_payments.items():
		invoice_payment_row = reduce(
			make_payment_row,
			payments,
			_new_invoice_payment(mop_cols)
		)

		data.append(
			make_change_total(invoice_payment_row)
		)

	return data


def _get_clauses(filters):
	if filters.query_doctype == 'POS Profile':
		clauses = [
			"si.docstatus = 1",
			"si.pos_profile = %(query_doc)s",
			"si.posting_date BETWEEN %(from_date)s AND %(to_date)s"
		]
		return " AND ".join(clauses)
	if filters.query_doctype == 'Warehouse':
		clauses = [
			"si.docstatus = 1",
			"pp.warehouse = %(query_doc)s",
			"si.posting_date BETWEEN %(from_date)s AND %(to_date)s"
		]
		return " AND ".join(clauses)
	frappe.throw(_("Invalid 'Query By' filter"))


def _make_payment_row(mop_cols, _, row):
	mop = row.get('mode_of_payment')
	amount = row.get('amount')

	for mop_col in mop_cols:
		mop_key = mop_col.replace(" ", "_").lower()
		if mop == mop_col:
			_[mop_key] = _[mop_key] + amount
			break

	if not _.get('invoice'):
		_['invoice'] = row.get('invoice')
	if not _.get('pe'):
		_['pe'] = row.get('pe')
	if not _.get('change'):
		_['change'] = row.get('change_amount')
	if not _.get('posting_date'):
		_['posting_date'] = row.get('posting_date')
	if not _.get('posting_time'):
		_['posting_time'] = row.get('posting_time')
	if not _.get('customer'):
		_['customer'] = row.get('customer')
	if not _.get('customer_name'):
		_['customer_name'] = row.get('customer_name')
	if not _.get('mobile_no'):
		_['mobile_no'] = row.get('mobile_no')
	if not _.get('ref_no'):
		_['ref_no'] = row.get('ref_no')
	if not _.get('show_creator'):
		_['show_creator'] = row.get('show_creator')
	# if not _.get('ref_date'):
	# 	_['ref_date'] = row.get('ref_date')


	return _


def _get_mop():
	mop = frappe.get_all('POS Bahrain Settings MOP', fields=['mode_of_payment'])

	if not mop:
		frappe.throw(_('Please set Report MOP under POS Bahrain Settings'))

	return list(pluck('mode_of_payment', mop))


def _new_invoice_payment(mop_cols):
	invoice_payment = {
		'invoice': None,
		'payment_entry':None,
		'posting_date': None,
		'posting_time': None,
		'change': None,
		'total': 0.00,
		'customer': None,
		'customer_name': None,
		'mobile_no': None,
		'ref_no' : None,
		'show_creator':None
		# 'ref_date' :None
	}

	for mop_col in mop_cols:
		invoice_payment[mop_col] = 0.00

	return invoice_payment
