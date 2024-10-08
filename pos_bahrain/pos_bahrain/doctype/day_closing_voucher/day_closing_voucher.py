# -*- coding: utf-8 -*-
# Copyright (c) 2021, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from itertools import groupby
import json

class DayClosingVoucher(Document):
	def validate(self):
		args = ""
		# if self.docstatus:
		# args = "c"%{"cur_docname":self.name}
		existing = frappe.db.sql("""SELECT name FROM `tabDay Closing Voucher`
									WHERE date = '%(date)s' AND branch = '%(branch)s'
									AND docstatus != 2 AND name != '%(cur_docname)s'"""%{
									"date":self.date, "branch": self.branch, "args":args, "cur_docname":self.name})
		if existing:
			frappe.throw("Closing voucher exists for this branch for this date ")

		get_data(self)


def get_data(self):
	def get_pcv(self):
		pcv_tup = ()
		pcv = frappe.db.sql("""SELECT
							name, docstatus 
						FROM 
							`tabPOS Closing Voucher`
						WHERE
							Date(period_from) = '%(dc_date)s'
							AND Date(period_to) = '%(dc_date)s'
							AND pos_profile = '%(pos_profile)s'
							AND docstatus < 2 """%{
								"dc_date":self.date, 
								"pos_profile":self.branch}, as_dict = 1)
		if pcv:
			if len(pcv) == 1:
				if pcv[0]['name'] == 0:
					frappe.throw("Draft POS Closing Voucher Exists for this branch for the selected date")
					return 0, 0
				pcv_tup = """('%(pcv)s')""" %{"pcv":pcv[0]['name']}
				return pcv_tup, pcv

			for i in pcv:
				if i['docstatus'] == 0:
					frappe.throw("Draft POS Closing Voucher Exists for this branch for the selected date")
				pcv_tup = pcv_tup + (i['name'],)
			return pcv_tup, pcv
		return 0, 0

	def get_employees(pcv_tup):
		pcv_emp_list = []
		pcv_employees = frappe.db.sql("""SELECT sales_employee, sales_employee_name, invoices_count, sales_total, parent
						FROM `tabPOS Voucher Employee` WHERE parent in %(parent)s """%{"parent":pcv_tup}, as_dict = 1)

		# pcv_employees_sorted = sorted(pcv_employees, key = lambda i: i['sales_employee'])

		# group_emp_list = [(a, list(b)) for a, b in groupby(pcv_employees_sorted, key=lambda x:x['sales_employee'])]

		# for key,value in group_emp_list:
		# 	pcv_emp_list.append( {
		# 		'sales_employee':key,
		# 		'sales_employee_name':list(value)[0]['sales_employee_name'],
		# 		'invoices_count': sum(int(d['invoices_count']) for d in value) ,
		# 		'sales_total':sum(float(d['sales_total']) for d in value)
		# 		})

		pcv_employees_sorted = sorted(pcv_employees, key = lambda i: i['parent'])

		jsonString_col = json.dumps(pcv_employees_sorted, indent=4, sort_keys=True, default=str)
		f3= open("/home/demo9t9it/frappe-bench/apps/pos_bahrain/pos_bahrain/pos_bahrain/doctype/day_closing_voucher/txt/col_data.txt","w+")
		f3.write(jsonString_col)

		# group_emp_list = [(a, list(b)) for a, b in groupby(pcv_employees_sorted, key=lambda x:x['sales_employee'])]
		# for entry in pcv_employees_sorted:
		# # for key,value in pcv_employees_sorted:
		# 	pcv_emp_list.append( {
		# 		'sales_employee': entry['sales_employee'],
		# 		'sales_employee_name':entry['sales_employee_name'],
		# 		'invoices_count': entry['invoices_count'] ,
		# 		'sales_total': entry['sales_total'],
		# 		'pcv' : entry['parent']
		# 		})
		return pcv_employees_sorted
	
	def get_mop(pcv_tup):
		mop_list = []
		pcv_mop = frappe.db.sql("""SELECT
									is_default, mode_of_payment,
									type, collected_amount, expected_amount,
									difference_amount, mop_currency, mop_conversion_rate,
									base_collected_amount, parent
								FROM `tabPOS Voucher Payment`
								WHERE parent in %(parent)s """%{"parent":pcv_tup}, as_dict = 1)

		pcv_mop_sorted = sorted(pcv_mop, key = lambda i: i['parent'])

		# group_mop_list = [(a, list(b)) for a, b in groupby(pcv_mop_sorted, key=lambda x:x['mode_of_payment'])]

		# for key,value in group_mop_list:
		# for entry in pcv_mop_sorted:
		# 	mop_list.append({
		# 		'mode_of_payment':entry['mode_of_payment'],
		# 		'is_default':entry['is_default'],
		# 		'type':entry['type'],
		# 		'collected_amount': entry['collected_amount'],
		# 		'expected_amount': entry['expected_amount'],
		# 		'difference_amount': entry['difference_amount'],
		# 		'mop_currency':entry['mop_currency'],
		# 		'mop_conversion_rate':entry['mop_conversion_rate'],
		# 		'base_collected_amount': entry['base_collected_amount'],
		# 		'pcv' : entry['parent']
		# 		})

		return pcv_mop_sorted

	def get_invoices(pcv_tup):
		pcv_invoices = frappe.db.sql("""SELECT invoice, sales_employee, total_quantity, grand_total, paid_amount, change_amount, parent
						FROM `tabPOS Voucher Invoice` WHERE parentfield = 'invoices' AND parent in %(parent)s """%{"parent":pcv_tup}, as_dict = 1)
		pcv_invoices_sorted = sorted(pcv_invoices, key = lambda i: i['invoice'])
		return pcv_invoices_sorted
	
	def get_pe(pcv_tup):
		pcv_pe = frappe.db.sql("""SELECT pe_number, party_name, mop, amount, parent
						FROM `tabPCV Payment Entry Table` WHERE parent in %(parent)s """%{"parent":pcv_tup}, as_dict = 1)
		pcv_pe_sorted = sorted(pcv_pe, key = lambda i: i['pe_number'])
		return pcv_pe_sorted

	def get_returns(pcv_tup):
		pcv_return = frappe.db.sql("""SELECT pe_number, party_name, mop, amount, parent
						FROM `tabPCV Payment Entry Table` WHERE parentfield = 'returns' AND parent in %(parent)s """%{"parent":pcv_tup}, as_dict = 1)
		pcv_return_sorted = sorted(pcv_return, key = lambda i: i['pe_number'])
		return pcv_return_sorted
	
	def get_taxes(pcv_tup):
		taxes_list = []
		pcv_taxes = frappe.db.sql("""SELECT rate, tax_amount, parent
								FROM `tabPOS Voucher Tax`
								WHERE parent in %(parent)s """%{"parent":pcv_tup}, as_dict = 1)
								
		pcv_taxes_sorted = sorted(pcv_taxes, key = lambda i: i['rate'])

		# group_taxes_list = [(a, list(b)) for a, b in groupby(pcv_taxes_sorted, key=lambda x:x['rate'])]

		# for key,value in group_taxes_list:
		# for tax in pcv_taxes:
		# 	taxes_list.append({
		# 		'rate':tax['rate'],
		# 		'tax_amount': sum(float(d['tax_amount']) for d in value),
		# 		})

		return pcv_taxes_sorted

	def get_item_groups(pcv_tup):
		item_group_list = []
		pcv_item_groups = frappe.db.sql("""SELECT item_group, qty, net_amount, 
											tax_amount, grand_total, parent
								FROM `tabPOS Voucher Item Group`
								WHERE parent in %(parent)s """%{"parent":pcv_tup}, as_dict = 1)
		
		pcv_item_sorted = sorted(pcv_item_groups, key = lambda i: i['item_group'])

		# group_item_group_list = [(a, list(b)) for a, b in groupby(pcv_item_sorted, key=lambda x:x['item_group'])]

		# for key,value in group_item_group_list:
		# 	item_group_list.append({
		# 		'item_group':key,
		# 		'qty': sum(float(d['qty']) for d in value),
		# 		'net_amount': sum(float(d['net_amount']) for d in value),
		# 		'tax_amount': sum(float(d['tax_amount']) for d in value),
		# 		'grand_total': sum(float(d['grand_total']) for d in value),
		# 		})

		

		return pcv_item_sorted

	def get_pcv_columns_data(pcv_tup):
		pcv_columns_data = frappe.db.sql("""SELECT
												name AS name,
												net_total AS net_total,
												tax_total AS tax_total,
												discount_total AS discount_total,
												grand_total AS grand_total,
												outstanding_total AS outstanding_total,
												total_collected AS total_collected, 
												change_total AS change_total,
												total_quantity AS total_quantity,
												total_invoices AS total_invoices, 
												average_sales AS average_sales,
												returns_net_total AS returns_net_total,
												returns_total AS returns_total,
												returns_quantity AS returns_quantity
								FROM `tabPOS Closing Voucher`
								WHERE name in %(parent)s """%{"parent":pcv_tup}, as_dict = 1)
		
		# pcv_columns_data = pcv_columns_data[0]

		# pcv_columns_data['average_sales'] = pcv_columns_data['average_sales'] / len(pcv_tup)

		return pcv_columns_data

	pcv_tup, pcv = get_pcv(self)
	if pcv_tup != 0 :
		employees = get_employees(pcv_tup)
		mop = get_mop(pcv_tup)
		invoices = get_invoices(pcv_tup)
		pe = get_pe(pcv_tup)
		returns = get_returns(pcv_tup)
		taxes = get_taxes(pcv_tup)
		item_groups = get_item_groups(pcv_tup)
		pcv_columns_data = get_pcv_columns_data(pcv_tup)

		net_total = sum(item['net_total'] for item in pcv_columns_data)
		total_invoices = sum(item['total_invoices'] for item in pcv_columns_data)

		avg_per_invoice = (net_total / total_invoices)

		self.net_total = net_total
		self.tax_total = sum(item['tax_total'] for item in pcv_columns_data)
		self.discount_total =sum(item['discount_total'] for item in pcv_columns_data)
		self.grand_total = sum(item['grand_total'] for item in pcv_columns_data)
		self.outstanding_total = sum(item['outstanding_total'] for item in pcv_columns_data)
		self.total_collected = sum(item['total_collected'] for item in pcv_columns_data)
		self.total_change = sum(item['change_total'] for item in pcv_columns_data)
		self.total_quantity = sum(item['total_quantity'] for item in pcv_columns_data)
		self.total_invoices = total_invoices
		self.average_sales_per_invoice = avg_per_invoice
		self.returns_net_total = sum(item['returns_net_total'] for item in pcv_columns_data)
		self.returns_total = sum(item['returns_total'] for item in pcv_columns_data)
		self.returns_quantity = sum(item['returns_quantity'] for item in pcv_columns_data)


		self.pcv = []
		for pcv in pcv_columns_data:
			self.append("pcv",{
				"pcv" : pcv['name'],
				"net" : pcv['net_total'],
				"tax" : pcv['tax_total'],
				"discount" : pcv['discount_total'],
				"grand_total" : pcv['grand_total'],
				"outstanding" : pcv['outstanding_total'],
				"total_collected" : pcv['total_collected'],
				"total_change" : pcv['change_total'],
				"total_qty" : pcv['total_quantity'],
				"total_invoices" : pcv['total_invoices'],
				"avg_sales_per_invoice" : pcv['average_sales'],
				"returns_net_total" : pcv['returns_net_total'],
				"return_total" : pcv['returns_total'],
				"return_qty" : pcv['returns_quantity'],
			})

		self.employees = []
		for employee in employees:
			self.append("employees",{
				"sales_employee" : employee['sales_employee'],
				"sales_employee_name" : employee['sales_employee_name'],
				"invoices_count": employee['invoices_count'],
				"sales_total" : employee['sales_total'],
				"pcv" : employee['parent']
			})

		self.payments = []
		for entry in mop:
			self.append("payments", {
				"is_default" : entry["is_default"],
				"mode_of_payment" : entry["mode_of_payment"],
				"type" : entry["type"],
				"collected_amount" : entry["collected_amount"],
				"expected_amount" : entry["expected_amount"],
				"difference_amount" : entry["difference_amount"],
				"mop_currency" : entry["mop_currency"],
				"mop_conversion_rate" : entry["mop_conversion_rate"],
				"base_collected_amount" : entry["base_collected_amount"],
					
			})
		
		self.invoices = []
		for invoice in invoices:
			self.append("invoices", {
				"invoice" : invoice.invoice,
				"sales_employee" : invoice.sales_employee, 
				"total_quantity" : invoice.total_quantity,
				"grand_total" : invoice.grand_total,
				"paid_amount" : invoice.paid_amount,
				"change_amount" : invoice.change_amount,
				"pcv" : invoice.parent

			})

		self.payment_entry = []
		for pe_entry in pe:
			self.append("payment_entry", {
				"pe_number" : pe_entry['pe_number'],
				"party_name" : pe_entry['party_name'],
				"mop": pe_entry['mop'],
				"amount" : pe_entry['amount'],
				"pcv" : pe_entry['parent']
			})

		self.returns = []
		for invoice in returns:
			self.append("returns",{
				"invoice" : invoice['invoice'],
				"sales_employee" : invoice['sales_employee'],
				"total_quantity" : invoice['total_quantity'],
				"grand_total" : invoice['grand_total'],
				"paid_amount" : invoice['paid_amount'],
				"change_amount" : invoice['change_amount'],
				"pcv" : invoice['parent']
			})

		self.taxes = []
		for tax in taxes:
			self.append("taxes",{
				"rate" : tax['rate'],
				"tax_amount" : tax['tax_amount'],
				"pcv" : tax['parent']
			})

		self.item_groups = []
		for item_group in item_groups:
			self.append("item_groups", {
				"item_group" : item_group['item_group'],
				"qty" : item_group['qty'],
				"net_amount" : item_group['net_amount'],
				"tax_amount" : item_group['tax_amount'],
				"grand_total" : item_group['grand_total'],
				"pcv" : item_group['parent']
			})

	elif pcv_tup == 0:
		frappe.throw("No POS Closing Vouchers found to create day closing")