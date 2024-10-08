# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe import _
from toolz import merge


def execute(filters=None):
	columns = _get_columns()
	data = _get_data(
		_get_clauses(filters),
		filters
	)

	return columns, data


def _get_columns():
	def make_column(key, label, type="Currency", options=None, width=120):
		return {
			'label': _(label),
			'fieldname': key,
			'fieldtype': type,
			'options': options,
			'width': width
		}

	return [
		make_column('item_code', 'Item Code', type='Link', options='Item'),
		make_column('item_name', 'Item Name', type='Data', width=180),
		make_column('rate', 'Rate'),
		make_column('valuation_rate', 'Valuation'),
		make_column('profit', 'Profit')
	]


def _get_clauses(filters):
	clauses = [
		"si.docstatus = 1",
		"si.is_return = 0",
		"si.posting_date = %(posting_date)s"
	]
	return " AND ".join(clauses)


def _get_data(clauses, args):
	items = frappe.db.sql(
		"""
			SELECT
				sii.item_code,
				sii.item_name,
				sii.rate,
				i.valuation_rate
			FROM `tabSales Invoice Item` AS sii
			LEFT JOIN `tabSales Invoice` AS si ON sii.parent = si.name
			LEFT JOIN `tabItem` AS i ON sii.item_code = i.name
			WHERE {clauses}
			GROUP BY sii.item_code
		""".format(
			clauses=clauses
		),
		values=args,
		as_dict=1
	)

	def calculate_profit(row):
		return merge(row, {'profit': row.rate - row.valuation_rate})

	return [calculate_profit(x) for x in items]
