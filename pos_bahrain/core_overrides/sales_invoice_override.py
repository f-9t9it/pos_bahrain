import frappe
from frappe import _
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
from frappe.utils import add_days, cint, cstr, flt, formatdate, get_link_to_form, getdate, nowdate


def custom_validate_pos(self):
    pass
		# if self.is_return:
		# 	invoice_total = self.rounded_total or self.grand_total
		# 	if flt(self.paid_amount) + flt(self.write_off_amount) - flt(invoice_total) > 1.0 / (
		# 		10.0 ** (self.precision("grand_total") + 1.0)
		# 	):
		# 		frappe.throw(_("Paid amount + Write Off Amount can not be greater than Grand Total"))

SalesInvoice.validate_pos = custom_validate_pos