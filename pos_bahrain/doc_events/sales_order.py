from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, today
from erpnext.setup.utils import get_exchange_rate
from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_delivery_note
from pos_bahrain.api.sales_invoice import get_customer_account_balance
from functools import partial
from toolz import first, compose, pluck, unique
from .sales_invoice import set_location

def validate(doc, method):

    custom_update_current_stock(doc)
    custom_after_save(doc, method)

def custom_update_current_stock(doc):

    for d in doc.get('packed_items'):
        bin = frappe.db.sql("SELECT actual_qty, projected_qty FROM `tabBin` WHERE item_code = %s AND warehouse = %s", 
                             (d.item_code, d.warehouse), as_dict=1)
        d.actual_qty = bin and flt(bin[0]['actual_qty']) or 0
        d.projected_qty = bin and flt(bin[0]['projected_qty']) or 0

        if not d.parent_item:
            if doc.items:

                d.parent_item = doc.items[0].item_code 

def custom_after_save(doc, method):
    if doc.is_new():
        from erpnext.stock.doctype.packed_item.packed_item import make_packing_list
        make_packing_list(doc)

def before_save(doc, method):
    set_location(doc)
def on_submit(doc, method):
    update_against_quotation(doc)

def before_cancel(doc, method):
    update_quotation_sales_order(doc)

@frappe.whitelist()
def update_against_quotation(doc):
    get_qns = compose(
        list,
        unique,
        partial(pluck, "prevdoc_docname"),
        frappe.db.sql,
    )
    
    qns = get_qns(
        """
            Select prevdoc_docname From `tabSales Order Item` where docstatus = 1 AND parent=%(so)s
        """,
        values={"so": doc.name},
        as_dict=1,
    )
   
    if qns :
        for row in qns:
            
            frappe.db.sql("""
			update `tabQuotation` 
				set sales_order = "{sales_order}"
				where docstatus=1 AND name="{quotation}";""".format( sales_order= doc.name,quotation=row))
            frappe.db.commit()
@frappe.whitelist()
def update_quotation_sales_order(doc):
    get_qns = compose(
        list,
        unique,
        partial(pluck, "prevdoc_docname"),
        frappe.db.sql,
    )
    
    qns = get_qns(
        """
            Select prevdoc_docname From `tabSales Order Item` where docstatus = 1 AND parent=%(so)s
        """,
        values={"so": doc.name},
        as_dict=1,
    )
   
    if qns :
        for row in qns:
            
            frappe.db.sql("""
			update `tabQuotation` 
				set sales_order = ""
				where docstatus=1 AND name="{quotation}";""".format( quotation=row))
            frappe.db.commit()