

from __future__ import unicode_literals
import frappe
import json
from frappe.utils import (
    add_days,
    ceil,
    cint,
    comma_and,
    flt,
    get_link_to_form,
    getdate,
    now_datetime,
    nowdate,today,formatdate, get_first_day, get_last_day 
)
from datetime import date,timedelta

@frappe.whitelist()
def search_batch(batch):
    item_data = search_serial_or_batch_or_barcode_number(batch)
    if item_data != 0:
        stock = frappe.db.sql("""SELECT batch_no,item_code,warehouse, sum(actual_qty) as qty,stock_uom from `tabStock Ledger Entry` WHERE is_cancelled = 0 and item_code = '%(item_code)s' group by warehouse,batch_no """%{"item_code": item_data['item_code']}, as_dict = 1)
        return stock
    
    return "Item/Price not found"
def search_serial_or_batch_or_barcode_number(search_value):
    # search barcode no
    barcode_data = frappe.db.get_value('Item Barcode', {'barcode': search_value}, ['barcode', 'parent as item_code', 'pb_uom'], as_dict=True)
    if barcode_data:
        barcode_data["type"] = "item_barcode"
        return barcode_data

    #confirm item code
    item_code_data = frappe.db.get_value('Item', search_value, ['name as item_code'], as_dict=True)
    if item_code_data:
        item_code_data["type"] = "item_code"
        item_code_data["pb_uom"] = ""
        return item_code_data
    
    # search batch no
    batch_no_data = frappe.db.get_value('Batch', search_value, ['name as batch_no', 'item as item_code'], as_dict=True)
    # batch_no_data=frappe.db.sql("""SELECT name as batch_no,item as item_code from `tabBatch` WHERE name = '%(search_value)s' """%{"search_value": search_value}, as_dict = 1)
    if batch_no_data:
        batch_no_data["type"] = "batch"
        return batch_no_data

    # search serial no
    serial_no_data = frappe.db.get_value('Serial No', search_value, ['name as serial_no', 'item_code'], as_dict=True)
    if serial_no_data:
        serial_no_data["type"] = "item_serial"
        return serial_no_data

    return 0  

#####Stock Reconciliation Create###
@frappe.whitelist(allow_guest=True)
def create_stock_adjustment(data=None):
    status = frappe.db.get_single_value("Price Checker API Settings", "stock_reconciliation_status")
    data=json.loads(frappe.request.data)
    if status == "Draft" :
        try:
            sa_doc = frappe.new_doc("Stock Reconciliation")
            sa_doc.purpose = "Stock Reconciliation"

            items=[]
            for item in data["items"]:
            #     sa_doc.append("items", {'item_code': item.item_code,'warehouse': item.warehouse,'qty': item.qty,'stock_uom': item.stock_uom,'batch_no': item.batch_no})
                sa_doc.append("items", {
                "item_code":item["item_code"],
                "warehouse":item["warehouse"],
                "qty": item["qty"],
                "batch_no" : item["batch_no"],
                "allow_zero_valuation_rate" : 1,
                })
   
            sa_doc.insert(ignore_permissions=True)
            if sa_doc :
                return {"Stock Reconciliation Successfully Created ":sa_doc.name}
        except Exception as e:
            return {"error":e}
    else :
        try:
            sa_doc = frappe.new_doc("Stock Reconciliation")
            sa_doc.purpose = "Stock Reconciliation"

            items=[]
            for item in data["items"]:
            #     sa_doc.append("items", {'item_code': item.item_code,'warehouse': item.warehouse,'qty': item.qty,'stock_uom': item.stock_uom,'batch_no': item.batch_no})
                sa_doc.append("items", {
                "item_code":item["item_code"],
                "warehouse":item["warehouse"],
                "qty": item["qty"],
                "batch_no" : item["batch_no"],
                "allow_zero_valuation_rate" : 1,
                })
   
            sa_doc.insert(ignore_permissions=True)
            sa_doc.submit()
            frappe.db.commit()
            if sa_doc :
                return {"Stock Reconciliation Successfully Created ":sa_doc.name}
        except Exception as e:
            return {"error":e}


@frappe.whitelist()
def create_stock_adjust(batch_no,item_code,warehouse,qty,stock_uom):
    # data=json.loads(frappe.request.data)
    # try:
    status = frappe.db.get_single_value("Price Checker API Settings", "stock_reconciliation_status")
    if status == "Draft" :
        sa_doc = frappe.new_doc("Stock Reconciliation")
        sa_doc.purpose = "Stock Reconciliation"
        #     sa_doc.append("items", {'item_code': item.item_code,'warehouse': item.warehouse,'qty': item.qty,'stock_uom': item.stock_uom,'batch_no': item.batch_no})
        sa_doc.append("items", {
            "item_code":item_code,
            "warehouse":warehouse,
            "qty": qty,
            "stock_uom": stock_uom,
            "batch_no" : batch_no,
        })
        sa_doc.insert(ignore_permissions=True)
        # sa_doc.submit()
        # frappe.db.commit()
        # if sa_doc :
        return {"Stock Reconciliation Successfully Created ":sa_doc.name}
    # except Exception as e:
    #     return {"error":e}
    else :
        sa_doc = frappe.new_doc("Stock Reconciliation")
        sa_doc.purpose = "Stock Reconciliation"
        #     sa_doc.append("items", {'item_code': item.item_code,'warehouse': item.warehouse,'qty': item.qty,'stock_uom': item.stock_uom,'batch_no': item.batch_no})
        sa_doc.append("items", {
            "item_code":item_code,
            "warehouse":warehouse,
            "qty": qty,
            "stock_uom": stock_uom,
            "batch_no" : batch_no,
        })
        sa_doc.insert(ignore_permissions=True)
        sa_doc.submit()
        frappe.db.commit()
        return {"Stock Reconciliation Successfully Created ":sa_doc.name}
        
@frappe.whitelist()
def search_batch_details(batch):
    item_data = search_serial_or_batch_or_barcode_number(batch)
    batch_no_data = frappe.db.get_value('Batch', batch, ['name as batch_no', 'item as item_code'], as_dict=True)
    batch_exists = frappe.db.sql("""SELECT * from `tabItem` WHERE name = '%(item_code)s' and has_batch_no=1 """%{"item_code": batch}, as_dict = 1)
    # print('/////////',batch_exists)
    if item_data != 0 and batch_exists:
        if batch_no_data:
#             stock = frappe.db.sql("""SELECT batch_no,item_code,warehouse, sum(actual_qty) as qty,stock_uom 
# from `tabStock Ledger Entry` sl LEFT JOIN `tabBatch` batch ON(sl.item_code=batch.item and sl.batch_no=batch.name)
# WHERE sl.is_cancelled = 0 and batch.expiry_date>=CURDATE() and sl.batch_no = '%(item_code)s' group by sl.warehouse,sl.batch_no """%{"item_code": item_data['batch_no']}, as_dict = 1)
#             return stock
            stock = frappe.db.sql("""SELECT batch_no,item_code,warehouse, sum(actual_qty) as qty,stock_uom 
from `tabStock Ledger Entry` sl LEFT JOIN `tabBatch` batch ON(sl.item_code=batch.item and sl.batch_no=batch.name)
WHERE sl.is_cancelled = 0 and batch.expiry_date>=CURDATE() and sl.batch_no = '%(item_code)s' group by sl.warehouse,sl.batch_no """%{"item_code": item_data['batch_no']}, as_dict = 1)
            return stock
        else :
            stock = frappe.db.sql("""SELECT batch_no,item_code,warehouse, sum(actual_qty) as qty,stock_uom 
from `tabStock Ledger Entry` sl LEFT JOIN `tabBatch` batch ON(sl.item_code=batch.item and sl.batch_no=batch.name)
WHERE sl.is_cancelled = 0 and batch.expiry_date>=CURDATE() and item_code = '%(item_code)s' group by warehouse,batch_no """%{"item_code": item_data['item_code']}, as_dict = 1)
            return stock
    if item_data != 0 and not batch_exists:
        if batch_no_data:
            stock = frappe.db.sql("""SELECT batch_no,item_code,warehouse, sum(actual_qty) as qty,stock_uom from `tabStock Ledger Entry` WHERE is_cancelled = 0 and batch_no = '%(item_code)s' group by warehouse,batch_no """%{"item_code": item_data['batch_no']}, as_dict = 1)
            return stock
    
        else :
            stock = frappe.db.sql("""SELECT batch_no,item_code,warehouse, sum(actual_qty) as qty,stock_uom from `tabStock Ledger Entry` WHERE is_cancelled = 0 and item_code = '%(item_code)s' group by warehouse,batch_no """%{"item_code": item_data['item_code']}, as_dict = 1)
            return stock
    return "Item/Price not found"

