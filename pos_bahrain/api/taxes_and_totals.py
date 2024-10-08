import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt

def calculate_change_amount(self):
		self.doc.change_amount = 0.0
		self.doc.base_change_amount = 0.0

		if self.doc.doctype == 'POS Invoice' and self.doc.is_return and self.doc.ignore_payments_for_return:
			# self.calculate_outstanding_amount()
			return

		if self.doc.doctype == "Sales Invoice" \
			and self.doc.paid_amount > self.doc.grand_total and not self.doc.is_return \
			and any(d.type == "Cash" for d in self.doc.payments):
			grand_total = self.doc.rounded_total or self.doc.grand_total
			base_grand_total = self.doc.base_rounded_total or self.doc.base_grand_total

			self.doc.change_amount = flt(self.doc.paid_amount - grand_total +
				self.doc.write_off_amount, self.doc.precision("change_amount"))

			self.doc.base_change_amount = flt(self.doc.base_paid_amount - base_grand_total +
				self.doc.base_write_off_amount, self.doc.precision("base_change_amount"))

def calculate_write_off_amount(self):
		if self.doc.doctype == 'Sales Invoice' and self.doc.is_pos and self.doc.credit_note_invoice:
			self.doc.write_off_amount = self.total_advance
			self.doc.base_write_off_amount = self.total_advance
			# return

		if flt(self.doc.change_amount) > 0:
			self.doc.write_off_amount = flt(self.doc.grand_total - self.doc.paid_amount
				+ self.doc.change_amount, self.doc.precision("write_off_amount"))
			self.doc.base_write_off_amount = flt(self.doc.write_off_amount * self.doc.conversion_rate,
				self.doc.precision("base_write_off_amount"))

def set_total_amount_to_default_mop(self, total_amount_to_pay):
		default_mode_of_payment = frappe.db.get_value('POS Payment Method',
			{'parent': self.doc.pos_profile, 'default': 1}, ['mode_of_payment'], as_dict=1)
		if self.doc.is_return and self.doc.outstanding_amount < 0:
			total_amount_to_pay = 0
		if default_mode_of_payment:
			self.doc.payments = []
			self.doc.append('payments', {
				'mode_of_payment': default_mode_of_payment.mode_of_payment,
				'amount': total_amount_to_pay,
				'default': 1
			})
	
def calculate_outstanding_amount_ov(self):
		# NOTE:
		# write_off_amount is only for POS Invoice
		# total_advance is only for non POS Invoice
		if self.doc.doctype == "Sales Invoice":
			self.calculate_paid_amount()

		if self.doc.is_return and self.doc.return_against and not self.doc.get('is_pos'): return

		self.doc.round_floats_in(self.doc, ["grand_total", "total_advance", "write_off_amount"])
		self._set_in_company_currency(self.doc, ['write_off_amount'])

		if self.doc.doctype in ["Sales Invoice", "Purchase Invoice"]:
			change_amount = 0

			if self.doc.doctype == "Sales Invoice" and not self.doc.get('is_return'):
				self.calculate_write_off_amount()
				self.calculate_change_amount()
				change_amount = self.doc.change_amount \
					if self.doc.party_account_currency == self.doc.currency else self.doc.base_change_amount

			calculate_outstanding_amount_ov(self.doc, change_amount)

			if self.doc.doctype == 'Sales Invoice' and self.doc.get('is_pos') and self.doc.get('is_return') and self.doc.get('ignore_payments_for_return'):
				self.update_paid_amount_for_return(self.doc.total_amount_to_pay)
def update_paid_amount_for_return_ov(self, total_amount_to_pay):
		existing_amount = 0

		for payment in self.doc.payments:
			existing_amount += payment.amount

		# do not override user entered amount if equal to total_amount_to_pay
		if existing_amount != total_amount_to_pay:
			default_mode_of_payment = frappe.db.get_value('Sales Invoice Payment',
				{'parent': self.doc.pos_profile, 'default': 1},
				['mode_of_payment', 'type', 'account'], as_dict=1)

			self.doc.payments = []

			if default_mode_of_payment:
				self.doc.append('payments', {
					'mode_of_payment': default_mode_of_payment.mode_of_payment,
					'type': default_mode_of_payment.type,
					'account': default_mode_of_payment.account,
					'amount': total_amount_to_pay
				})
			else:
				self.doc.is_pos = 0
				self.doc.pos_profile = ''

		self.calculate_paid_amount()
def calculate_outstanding_amount_ov(doc, change_amount=None):
	grand_total = doc.rounded_total or doc.grand_total
	if doc.party_account_currency == doc.currency:
		doc.total_amount_to_pay = flt(grand_total - doc.total_advance
			- flt(doc.write_off_amount), doc.precision("grand_total"))
	else:
		doc.total_amount_to_pay = flt(flt(grand_total *
			doc.conversion_rate, doc.precision("grand_total")) - doc.total_advance
				- flt(doc.base_write_off_amount), doc.precision("grand_total"))

	doc.round_floats_in(doc, ["paid_amount"])
	paid_amount = doc.paid_amount \
		if doc.party_account_currency == doc.currency else doc.base_paid_amount

	doc.outstanding_amount = flt(doc.total_amount_to_pay - flt(paid_amount) + flt(change_amount),
		doc.precision("outstanding_amount"))		