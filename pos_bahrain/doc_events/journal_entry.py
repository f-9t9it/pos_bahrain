
# -*- coding: utf-8 -*-
# Copyright (c) 2018, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, today
from erpnext.setup.utils import get_exchange_rate
from functools import partial
from toolz import first, compose, pluck, unique

###########Credit Note Journal Entry Cancel & update value in GL###
def on_cancel(doc, method=None):
    journa_entry_cancel_with_payment_reco = frappe.db.get_single_value("POS Bahrain Settings", "journa_entry_cancel_with_payment_reco")
    if journa_entry_cancel_with_payment_reco :
        update_gl_on_jv_cancel(doc)
        # cancel_jv(doc)

def update_gl_on_jv_cancel(doc):
    sales_invoice = frappe.db.sql(
        """
        SELECT reference_name 
        FROM `tabJournal Entry Account`
        WHERE reference_type = "Sales Invoice"
        AND parent =%(jv)s """, values={"jv": doc.name}, as_dict=1,)
    # print("//////////",sales_invoice)
    
    if sales_invoice:
        ref_name = frappe.get_all('Journal Entry Account', filters={'parent':doc.name},or_filters= {"reference_type":"Sales Invoice"}, fields=['reference_name','credit_in_account_currency'],limit =1)
        gl_no = frappe.db.sql(
        """
        SELECT name 
        FROM `tabGL Entry`
        WHERE voucher_type = "Sales Invoice"
        AND voucher_no =%(sales_invoice)s and credit=0 """, values={"sales_invoice": ref_name[0].reference_name}, as_dict=1,)
        # print("//////////",gl_no)

        for name in gl_no:
            
            frappe.db.set_value("GL Entry", name, "credit",ref_name[0].credit_in_account_currency)
            frappe.db.set_value("GL Entry", name, "credit_in_account_currency",ref_name[0].credit_in_account_currency)
            frappe.db.set_value("Sales Invoice", ref_name[0].reference_name, "status", "Paid")
            frappe.db.set_value("Sales Invoice", ref_name[0].reference_name, "outstanding_amount", 0)
            # doc.set_status(update=True)
    cn_no=frappe.db.get_value("Sales Invoice",{"pb_credit_note_no":doc.name}, "name")
    if cn_no :
        gl_no2 = frappe.db.sql(
        """
        SELECT name 
        FROM `tabGL Entry`
        WHERE voucher_type = "Sales Invoice"
        AND voucher_no =%(sales_invoice)s and debit=0 """, values={"sales_invoice": cn_no}, as_dict=1,)
        for name in gl_no2:
            
            frappe.db.set_value("GL Entry", name, "debit",doc.total_debit)
            frappe.db.set_value("GL Entry", name, "debit_in_account_currency",doc.total_debit)
        doc.flags.ignore_links = True
# def cancel_jv(doc):
#     jv_doc = frappe.get_doc("Journal Entry", doc.name)
#     cn_no=frappe.db.get_value("Sales Invoice",{"pb_credit_note_no":doc.name}, "name")
#     if cn_no :
#         gl_no2 = frappe.db.sql(
#         """
#         SELECT name 
#         FROM `tabGL Entry`
#         WHERE voucher_type = "Sales Invoice"
#         AND voucher_no =%(sales_invoice)s and debit=0 """, values={"sales_invoice": cn_no}, as_dict=1,)
#         for name in gl_no2:
            
#             frappe.db.set_value("GL Entry", name, "debit",doc.total_debit)
#         doc.flags.ignore_links = True
        # print("////////////////",cn_no)
        # jv_doc.cancel(doc)
    