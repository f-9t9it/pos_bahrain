# # Copyright (c) 2013, 	9t9it and contributors
# # For license information, please see license.txt

# from __future__ import unicode_literals
# # import frappe

# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data




# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import msgprint, _
from frappe.model.meta import get_field_precision
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_accounting_dimensions, get_dimension_with_children
from datetime import datetime
from functools import partial, reduce
from toolz import groupby, pluck, compose, merge, keyfilter
import pandas as pd
from collections import defaultdict

def execute(filters=None):
	return _execute(filters)

def _execute(filters, additional_table_columns=None, additional_query_columns=None):
	if not filters: filters = frappe._dict({})

	invoice_list = get_invoices(filters, additional_query_columns)
	columns, income_accounts, tax_accounts = get_columns(invoice_list, additional_table_columns,filters)

	if not invoice_list:
		msgprint(_("No record found"))
		return columns, invoice_list

	invoice_income_map = get_invoice_income_map(invoice_list)
	invoice_income_map, invoice_tax_map = get_invoice_tax_map(invoice_list,
		invoice_income_map, income_accounts)
	#Cost Center & Warehouse Map
	invoice_cc_wh_map = get_invoice_cc_wh_map(invoice_list)
	invoice_so_dn_map = get_invoice_so_dn_map(invoice_list)
	company_currency = frappe.get_cached_value('Company',  filters.get("company"),  "default_currency")
	mode_of_payments = get_mode_of_payments([inv.name for inv in invoice_list])
	incentive_slab_list = get_incentive_slab_list()
	data = []
	for inv in invoice_list:
				
		if inv.is_return == False:
			# invoice details

			sales_order = list(set(invoice_so_dn_map.get(inv.name, {}).get("sales_order", [])))
			delivery_note = list(set(invoice_so_dn_map.get(inv.name, {}).get("delivery_note", [])))
			cost_center = list(set(invoice_cc_wh_map.get(inv.name, {}).get("cost_center", [])))
			warehouse = list(set(invoice_cc_wh_map.get(inv.name, {}).get("warehouse", [])))

			row = {
				'invoice': inv.name,
				'posting_date': inv.posting_date,
				'customer': inv.customer,
				'customer_name': inv.customer_name,
				'pb_sales_employee_name' : inv.pb_sales_employee_name,
				'is_return': inv.is_return,
				'sales_team_name': inv.sales_person
			}

			if additional_query_columns:
				for col in additional_query_columns:
					row.update({
						col: inv.get(col)
					})

			# Accumulate all associated invoices for return
			returned_invoices = []
			for invobj in invoice_list:
				if invobj.return_against == inv.name:
					returned_invoices.append(invobj.name)

			row.update({
				'return_against': ", ".join(returned_invoices),  # Join all associated invoices
				'tax_id': inv.get("tax_id"),
				'mode_of_payment':  ", ".join(mode_of_payments.get(inv.name, [])),
				'owner': inv.owner,
				'sales_order': ", ".join(sales_order),
				'delivery_note': ", ".join(delivery_note),
				'cost_center': ", ".join(cost_center),
				'warehouse': ", ".join(warehouse),
				'currency': company_currency
			})

			# map income values
			base_net_total = 0
			for income_acc in income_accounts:
				income_amount = flt(invoice_income_map.get(inv.name, {}).get(income_acc))
				base_net_total += income_amount
				row.update({
					frappe.scrub(income_acc): income_amount
				})

			# net total
			row.update({'net_total': base_net_total or inv.base_net_total})

			# tax account
			total_tax = 0
			for tax_acc in tax_accounts:
				if tax_acc not in income_accounts:
					tax_amount_precision = get_field_precision(frappe.get_meta("Sales Taxes and Charges").get_field("tax_amount"), currency=company_currency) or 2
					tax_amount = flt(invoice_tax_map.get(inv.name, {}).get(tax_acc), tax_amount_precision)
					total_tax += tax_amount
					row.update({
						frappe.scrub(tax_acc): tax_amount
					})

			# total tax, grand total, outstanding amount & rounded total

			row.update({
				'tax_total': total_tax,
				'grand_total': inv.base_grand_total,
				'rounded_total': inv.base_rounded_total,
				'outstanding_amount': inv.outstanding_amount,
				'amount_before_discount': inv.amount_before_discount,
				'discount_value': inv.amount_before_discount - base_net_total or inv.base_net_total
			})

			returned_amount_value = 0
			remaining_amount = 0
			# Calculate returned amount and remaining amount based on all associated invoices
			for returned_inv_name in returned_invoices:
				returned_inv = next((invobj for invobj in invoice_list if invobj.name == returned_inv_name), None)
				if returned_inv:
					# returned_amount_value += returned_inv.base_grand_total
					returned_amount_value += base_net_total or inv.base_net_total
			remaining_amount = (base_net_total or inv.base_net_total) - (returned_amount_value)
			returned_amount_value = abs(returned_amount_value)
			row.update({
				'returned_amount': returned_amount_value,
				'remaining_amount': remaining_amount,
			})

			# Calculate the value for incentive
			discount_value = inv.amount_before_discount - base_net_total or inv.base_net_total
			incentive_value = get_incentive_value(remaining_amount,discount_value,incentive_slab_list)
			row.update({
				'incentive_value': incentive_value,
			})
			data.append(row)

 

	if filters.get('summary_view'):
		grouped_data = defaultdict(dict)
		for row in data:
			sales_team_name = row.get('sales_team_name')
			if sales_team_name not in grouped_data:
				# Initialize the fields as lists
				grouped_data[sales_team_name] = {
					'invoice': [row['invoice']],
					'posting_date': [str(row['posting_date'])],
					'customer': [row['customer']],
					'customer_name': [row['customer_name']],
					'pb_sales_employee_name': [row['pb_sales_employee_name']],
					'return_against': [row['return_against']],
					'cost_center': [row['cost_center']],
					'warehouse': [row['warehouse']],
					'sales___wcpw': row['sales___wcpw'],
					'net_total': row['net_total'],
					'vat___wcpw': row['vat___wcpw'],
					'tax_total': row['tax_total'],
					'grand_total': row['grand_total'],
					'rounded_total': row['rounded_total'],
					'outstanding_amount': row['outstanding_amount'],
					'amount_before_discount': row['amount_before_discount'],
					'discount_value': row['discount_value'],
					'returned_amount': row['returned_amount'],
					'remaining_amount': row['remaining_amount'],
					'incentive_value': row['incentive_value'],
					'sales_team_name' :  row['sales_team_name'],
				}
			else:
				# Append values to the existing fields
				grouped_data[sales_team_name]['invoice'].append(row['invoice'])
				grouped_data[sales_team_name]['posting_date'].append(str(row['posting_date']))
				grouped_data[sales_team_name]['customer'].append(row['customer'])
				grouped_data[sales_team_name]['customer_name'].append(row['customer_name'])
				grouped_data[sales_team_name]['pb_sales_employee_name'].append(row['pb_sales_employee_name'])
				grouped_data[sales_team_name]['return_against'].append(row['return_against'])
				grouped_data[sales_team_name]['cost_center'].append(row['cost_center'])
				grouped_data[sales_team_name]['warehouse'].append(row['warehouse'])

				# Sum the numeric fields
				grouped_data[sales_team_name]['sales___wcpw'] += row['sales___wcpw']
				grouped_data[sales_team_name]['net_total'] += row['net_total']
				grouped_data[sales_team_name]['vat___wcpw'] += row['vat___wcpw']
				grouped_data[sales_team_name]['tax_total'] += row['tax_total']
				grouped_data[sales_team_name]['grand_total'] += row['grand_total']
				grouped_data[sales_team_name]['rounded_total'] += row['rounded_total']
				grouped_data[sales_team_name]['outstanding_amount'] += row['outstanding_amount']
				grouped_data[sales_team_name]['amount_before_discount'] += row['amount_before_discount']
				grouped_data[sales_team_name]['discount_value'] += row['discount_value']
				grouped_data[sales_team_name]['returned_amount'] += row['returned_amount']
				grouped_data[sales_team_name]['remaining_amount'] += row['remaining_amount']
				grouped_data[sales_team_name]['incentive_value'] += row['incentive_value']
		data = list(grouped_data.values())
 
     
	
 
	return columns, data


def get_columns(invoice_list, additional_table_columns,filters):
	"""return columns based on filters"""
	columns = []
	if not filters.get('summary_view'):
		columns+=[
			{
				'label': _("Invoice"),
				'fieldname': 'invoice',
				'fieldtype': 'Link',
				'options': 'Sales Invoice',
				'width': 120
			},
			{
				'label': _("Posting Date"),
				'fieldname': 'posting_date',
				'fieldtype': 'Date',
				'width': 80
			},
			{
				'label': _("Customer"),
				'fieldname': 'customer',
				'fieldtype': 'Link',
				'options': 'Customer',
				'width': 120
			},
			{
				'label': _("Customer Name"),
				'fieldname': 'customer_name',
				'fieldtype': 'Data',
				'width': 120
			},
			{
				'label': _("Sales Employee Name"),
				'fieldname': 'pb_sales_employee_name',
				'fieldtype': 'Data',
				'width': 120
			}
		]
	
	if additional_table_columns:
		columns += additional_table_columns

 
	columns +=[
		{
			"label": _("Sales Team"),
			"fieldname": "sales_team_name",
			"fieldtype": "Data",
			"width": 120
		},
  		{
			"label": _("Incentive Value"),
			"fieldname": "incentive_value",
			"fieldtype": "Currency",
			"options": 'currency',
			"width": 120
		},
	]
	if not filters.get('summary_view'):
		columns +=[
  		{
			'label': _("Return Against Sales Invoice"),
			'fieldname': 'return_against',
			'fieldtype': 'Data',
			# 'options': 'Sales Invoice',
			'width': 120
		},
		]
		
	columns +=[
  		{
			"label": _("Value without Discount"),
			"fieldname": "amount_before_discount",
			"fieldtype": "Currency",
			"options": 'currency',
			"width": 120
		},
		{
			"label": _("Discount Value"),
			"fieldname": "discount_value",
			"fieldtype": "Currency",
			"options": 'currency',
			"width": 120
		},
		{
			"label": _("Net Total"),
			"fieldname": "net_total",
			"fieldtype": "Currency",
			"options": 'currency',
			"width": 120
		},
		{
			"label": _("Returned Amount"),
			"fieldname": "returned_amount",
			"fieldtype": "Currency",
			"options": 'currency',
			"width": 120
		},
		{
			"label": _("Value After Return"),
			"fieldname": "remaining_amount",
			"fieldtype": "Currency",
			"options": 'currency',
			"width": 120
		},
	]
	if not filters.get('summary_view'):
		columns +=[
		{
			'label': _("Tax Id"),
			'fieldname': 'tax_id',
			'fieldtype': 'Data',
			'width': 120
		},
		{
			'label': _("Mode Of Payment"),
			'fieldname': 'mode_of_payment',
			'fieldtype': 'Data',
			'width': 120
		},
		{
			'label': _("Owner"),
			'fieldname': 'owner',
			'fieldtype': 'Data',
			'width': 150
		},
		{
			'label': _("Sales Order"),
			'fieldname': 'sales_order',
			'fieldtype': 'Link',
			'options': 'Sales Order',
			'width': 100
		},
		{
			'label': _("Delivery Note"),
			'fieldname': 'delivery_note',
			'fieldtype': 'Link',
			'options': 'Delivery Note',
			'width': 100
		},
		{
			'label': _("Cost Center"),
			'fieldname': 'cost_center',
			'fieldtype': 'Link',
			'options': 'Cost Center',
			'width': 100
		},
		{
			'label': _("Warehouse"),
			'fieldname': 'warehouse',
			'fieldtype': 'Link',
			'options': 'Warehouse',
			'width': 100
		},
		{
			"fieldname": "currency",
			"label": _("Currency"),
			"fieldtype": "Data",
			"width": 80
		}
	]

	income_accounts = []
	tax_accounts = []
	income_columns = []
	tax_columns = []

	if invoice_list:
		income_accounts = frappe.db.sql_list("""select distinct income_account
			from `tabSales Invoice Item` where docstatus = 1 and parent in (%s)
			order by income_account""" %
			', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list]))

		tax_accounts = 	frappe.db.sql_list("""select distinct account_head
			from `tabSales Taxes and Charges` where parenttype = 'Sales Invoice'
			and docstatus = 1 and base_tax_amount_after_discount_amount != 0
			and parent in (%s) order by account_head""" %
			', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list]))

	for account in income_accounts:
		income_columns.append({
			"label": account,
			"fieldname": frappe.scrub(account),
			"fieldtype": "Currency",
			"options": 'currency',
			"width": 120
		})

	for account in tax_accounts:
		if account not in income_accounts:
			tax_columns.append({
				"label": account,
				"fieldname": frappe.scrub(account),
				"fieldtype": "Currency",
				"options": 'currency',
				"width": 120
			})

	# net_total_column = [{
	# 	"label": _("Net Total"),
	# 	"fieldname": "net_total",
	# 	"fieldtype": "Currency",
	# 	"options": 'currency',
	# 	"width": 120
	# }]

	total_columns = [
		{
			"label": _("Tax Total"),
			"fieldname": "tax_total",
			"fieldtype": "Currency",
			"options": 'currency',
			"width": 120
		},
		{
			"label": _("Grand Total"),
			"fieldname": "grand_total",
			"fieldtype": "Currency",
			"options": 'currency',
			"width": 120
		},
		{
			"label": _("Rounded Total"),
			"fieldname": "rounded_total",
			"fieldtype": "Currency",
			"options": 'currency',
			"width": 120
		},
		{
			"label": _("Outstanding Amount"),
			"fieldname": "outstanding_amount",
			"fieldtype": "Currency",
			"options": 'currency',
			"width": 120
		},
		{
			"label": _("Return Value"),
			"fieldname": "grand_total",
			"fieldtype": "Currency",
			"options": 'currency',
			"width": 120
		}
	]

	columns = columns + income_columns  + tax_columns + total_columns

	return columns, income_accounts, tax_accounts

def get_conditions(filters):
	conditions = ""

	if filters.get("company"): conditions += " and company=%(company)s"
	if filters.get("customer"): conditions += " and customer = %(customer)s"

	if filters.get("from_date"): conditions += " and posting_date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and posting_date <= %(to_date)s"

	if filters.get("owner"): conditions += " and owner = %(owner)s"

	if filters.get("mode_of_payment"):
		conditions += """ and exists(select name from `tabSales Invoice Payment`
			 where parent=i.name
			 	and ifnull(`tabSales Invoice Payment`.mode_of_payment, '') = %(mode_of_payment)s)"""

	if filters.get("cost_center"):
		conditions +=  """ and exists(select name from `tabSales Invoice Item`
			 where parent=i.name
			 	and ifnull(`tabSales Invoice Item`.cost_center, '') = %(cost_center)s)"""

	if filters.get("warehouse"):
		conditions +=  """ and exists(select name from `tabSales Invoice Item`
			 where parent=i.name
			 	and ifnull(`tabSales Invoice Item`.warehouse, '') = %(warehouse)s)"""

	if filters.get("brand"):
		conditions +=  """ and exists(select name from `tabSales Invoice Item`
			 where parent=i.name
			 	and ifnull(`tabSales Invoice Item`.brand, '') = %(brand)s)"""

	if filters.get("item_group"):
		conditions +=  """ and exists(select name from `tabSales Invoice Item`
			 where parent=i.name
			 	and ifnull(`tabSales Invoice Item`.item_group, '') = %(item_group)s)"""

	accounting_dimensions = get_accounting_dimensions(as_list=False)

	if accounting_dimensions:
		common_condition = """
			and exists(select name from `tabSales Invoice Item`
				where parent=i.name
			"""
		for dimension in accounting_dimensions:
			if filters.get(dimension.fieldname):
				if frappe.get_cached_value('DocType', dimension.document_type, 'is_tree'):
					filters[dimension.fieldname] = get_dimension_with_children(dimension.document_type,
						filters.get(dimension.fieldname))

					conditions += common_condition + "and ifnull(`tabSales Invoice Item`.{0}, '') in %({0})s)".format(dimension.fieldname)
				else:
					conditions += common_condition + "and ifnull(`tabSales Invoice Item`.{0}, '') in (%({0})s))".format(dimension.fieldname)

	return conditions


def get_invoices(filters, additional_query_columns):
	if additional_query_columns:
		additional_query_columns = ', ' + ', '.join(additional_query_columns)

	conditions = get_conditions(filters)
	result =  frappe.db.sql("""
		select st.sales_person,i.name, i.posting_date, i.customer,i.pb_sales_employee_name,i.is_return,i.return_against,
		i.customer_name, i.owner,i.tax_id,

		(SELECT sum(inv_item.price_list_rate * inv_item.qty) AS amount_before_discount
             FROM `tabSales Invoice Item` inv_item WHERE parent = i.name) AS amount_before_discount,
            (SELECT sum(inv_item.discount_amount * inv_item.qty)
             FROM `tabSales Invoice Item` inv_item WHERE parent = i.name) + i.discount_amount AS discount,
            (SELECT sum(inv_item.amount) FROM `tabSales Invoice Item` inv_item WHERE parent = i.name) AS amount_after_discount,
  
		i.base_net_total, i.base_grand_total, i.base_rounded_total, i.outstanding_amount {0}
		from `tabSales Invoice` i
		left join `tabSales Team` st on st.parent = i.name
		where i.docstatus = 1 %s order by i.posting_date desc, i.name desc""".format(additional_query_columns or '') %
		conditions, filters, as_dict=1)
	# mop = _get_mop() 
	# if filters.get('summary_view'):
	# 	result = _summarize_payments(
	# 		groupby('sales_person', result),
	# 		mop
	# 	)
	return result

def _get_mop():
	mop = frappe.get_all('POS Bahrain Settings MOP', fields=['mode_of_payment'])

	if not mop:
		frappe.throw(_('Please set Report MOP under POS Bahrain Settings'))

	return list(pluck('mode_of_payment', mop))

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





def get_invoice_income_map(invoice_list):
	income_details = frappe.db.sql("""select parent, income_account, sum(base_net_amount) as amount
		from `tabSales Invoice Item` where parent in (%s) group by parent, income_account""" %
		', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list]), as_dict=1)

	invoice_income_map = {}
	for d in income_details:
		invoice_income_map.setdefault(d.parent, frappe._dict()).setdefault(d.income_account, [])
		invoice_income_map[d.parent][d.income_account] = flt(d.amount)

	return invoice_income_map

def get_invoice_tax_map(invoice_list, invoice_income_map, income_accounts):
	tax_details = frappe.db.sql("""select parent, account_head,
		sum(base_tax_amount_after_discount_amount) as tax_amount
		from `tabSales Taxes and Charges` where parent in (%s) group by parent, account_head""" %
		', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list]), as_dict=1)

	invoice_tax_map = {}
	for d in tax_details:
		if d.account_head in income_accounts:
			if d.account_head in invoice_income_map[d.parent]:
				invoice_income_map[d.parent][d.account_head] += flt(d.tax_amount)
			else:
				invoice_income_map[d.parent][d.account_head] = flt(d.tax_amount)
		else:
			invoice_tax_map.setdefault(d.parent, frappe._dict()).setdefault(d.account_head, [])
			invoice_tax_map[d.parent][d.account_head] = flt(d.tax_amount)

	return invoice_income_map, invoice_tax_map

def get_invoice_so_dn_map(invoice_list):
	si_items = frappe.db.sql("""select parent, sales_order, delivery_note, so_detail
		from `tabSales Invoice Item` where parent in (%s)
		and (ifnull(sales_order, '') != '' or ifnull(delivery_note, '') != '')""" %
		', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list]), as_dict=1)

	invoice_so_dn_map = {}
	for d in si_items:
		if d.sales_order:
			invoice_so_dn_map.setdefault(d.parent, frappe._dict()).setdefault(
				"sales_order", []).append(d.sales_order)

		delivery_note_list = None
		if d.delivery_note:
			delivery_note_list = [d.delivery_note]
		elif d.sales_order:
			delivery_note_list = frappe.db.sql_list("""select distinct parent from `tabDelivery Note Item`
				where docstatus=1 and so_detail=%s""", d.so_detail)

		if delivery_note_list:
			invoice_so_dn_map.setdefault(d.parent, frappe._dict()).setdefault("delivery_note", delivery_note_list)

	return invoice_so_dn_map

def get_invoice_cc_wh_map(invoice_list):
	si_items = frappe.db.sql("""select parent, cost_center, warehouse
		from `tabSales Invoice Item` where parent in (%s)
		and (ifnull(cost_center, '') != '' or ifnull(warehouse, '') != '')""" %
		', '.join(['%s']*len(invoice_list)), tuple([inv.name for inv in invoice_list]), as_dict=1)

	invoice_cc_wh_map = {}
	for d in si_items:
		if d.cost_center:
			invoice_cc_wh_map.setdefault(d.parent, frappe._dict()).setdefault(
				"cost_center", []).append(d.cost_center)

		if d.warehouse:
			invoice_cc_wh_map.setdefault(d.parent, frappe._dict()).setdefault(
				"warehouse", []).append(d.warehouse)

	return invoice_cc_wh_map

def get_mode_of_payments(invoice_list):
	mode_of_payments = {}
	if invoice_list:
		inv_mop = frappe.db.sql("""select parent, mode_of_payment
			from `tabSales Invoice Payment` where parent in (%s) group by parent, mode_of_payment""" %
			', '.join(['%s']*len(invoice_list)), tuple(invoice_list), as_dict=1)

		for d in inv_mop:
			mode_of_payments.setdefault(d.parent, []).append(d.mode_of_payment)

	return mode_of_payments


def get_incentive_slab_list():
         
    incentive_slab_list = frappe.db.sql(""" select * from `tabPos Bahrain Incentive Slab`  """, {}, as_dict=1)
    return incentive_slab_list


def get_incentive_value(remaining_amount,discount_value, incentive_slab_list):
    incentive_value = 0.0
    for slab in incentive_slab_list:
        if remaining_amount >= slab.minimum_vaue and remaining_amount <= slab.maximum_value:
            if discount_value > 0:
                incentive_value = (remaining_amount * slab.incentive_with_discount) /100
            else:
                incentive_value = (remaining_amount * slab.incentive_without_discount) /100
    

    return incentive_value
