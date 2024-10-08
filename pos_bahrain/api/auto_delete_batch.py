from __future__ import unicode_literals
import frappe
import json
from six import string_types
from erpnext.controllers.stock_controller import StockController
# import frappe

def delete_auto_created_batches_override(self):
	# import frappe
	dont_delete_batch = frappe.db.get_single_value('POS Bahrain Settings', "do_not_delete_batch_with_purchase_receipt")
	if dont_delete_batch and self.doctype == 'Purchase Receipt':
		return
		
	for d in self.items:
		if not d.batch_no: continue

		serial_nos = [sr.name for sr in frappe.get_all("Serial No",
			{'batch_no': d.batch_no, 'status': 'Inactive'})]

		if serial_nos:
			frappe.db.set_value("Serial No", { 'name': ['in', serial_nos] }, "batch_no", None)

		d.batch_no = None
		d.db_set("batch_no", None)

	for data in frappe.get_all("Batch",
		{'reference_name': self.name, 'reference_doctype': self.doctype}):
		frappe.delete_doc("Batch", data.name)
