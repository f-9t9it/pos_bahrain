import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt

def set_missing_values(source, target):
		doc = frappe.get_doc(target)
		doc.is_return = 1
		doc.return_against = source.name
		doc.ignore_pricing_rule = 1
		doc.set_warehouse = ""
		if doctype == "Sales Invoice" or doctype == "POS Invoice":
			doc.is_pos = source.is_pos

			# look for Print Heading "Credit Note"
			if not doc.select_print_heading:
				doc.select_print_heading = frappe.db.get_value("Print Heading", _("Credit Note"))

		elif doctype == "Purchase Invoice":
			# look for Print Heading "Debit Note"
			doc.select_print_heading = frappe.db.get_value("Print Heading", _("Debit Note"))

		for tax in doc.get("taxes"):
			if tax.charge_type == "Actual":
				tax.tax_amount = -1 * tax.tax_amount

		if doc.get("is_return"):
			if doc.doctype == 'Sales Invoice' or doc.doctype == 'POS Invoice':
				doc.consolidated_invoice = ""
				doc.set('payments', [])
				for data in source.payments:
					paid_amount = 0.00
					base_paid_amount = 0.00
					data.base_amount = flt(data.amount*source.conversion_rate, source.precision("base_paid_amount"))
					paid_amount += data.amount
					base_paid_amount += data.base_amount
					payment = {
						'mode_of_payment': data.mode_of_payment,
						'type': data.type,
						'amount': -1 * paid_amount,
						'base_amount': -1 * base_paid_amount,
						'account': data.account,
						'default': data.default
					}
					if data.credit_note:
						payment.update({'credit_note': data.credit_note})
					doc.append('payments', payment)

				if doc.is_pos:
					doc.paid_amount = -1 * source.paid_amount

			elif doc.doctype == 'Purchase Invoice':
				doc.paid_amount = -1 * source.paid_amount
				doc.base_paid_amount = -1 * source.base_paid_amount
				doc.payment_terms_template = ''
				doc.payment_schedule = []

		if doc.get("is_return") and hasattr(doc, "packed_items"):
			for d in doc.get("packed_items"):
				d.qty = d.qty * -1

		doc.discount_amount = -1 * source.discount_amount
		doc.run_method("calculate_taxes_and_totals")
	