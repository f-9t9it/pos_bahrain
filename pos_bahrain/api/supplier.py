from __future__ import unicode_literals
import frappe
import json

@frappe.whitelist()
def get_supplier_list():
    supplier_list = frappe.db.sql("""SELECT name as supplier_code,supplier_name From `tabSupplier` where disabled=0 """, as_dict = 1)
    return supplier_list
  