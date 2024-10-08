import frappe
from datetime import date

@frappe.whitelist()
def jv_cancel():
    customer = frappe.db.get_single_value("POS Bahrain Settings", "customer")
    if customer :
        for data in frappe.db.sql("""SELECT parent,party FROM `tabJournal Entry Account` WHERE Account = "Credit Note - WS" and party ='%(customer)s' """%{"customer":customer}, as_dict = 1):
            doc = frappe.get_doc('Journal Entry', data.parent)
            # print("////////",doc,customer)
            if doc.docstatus == 1:
                doc.cancel()
        for data in frappe.db.sql("""SELECT pb_credit_note_no FROM `tabSales Invoice` WHERE is_return = 1 and customer ='%(customer)s' """%{"customer":customer}, as_dict = 1):
            doc = frappe.get_doc('Journal Entry', data.pb_credit_note_no)
            if doc.docstatus == 1:
                doc.cancel()