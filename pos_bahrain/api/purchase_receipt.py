
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
def search_prec_item(item,warehouse=None):
    item_data = search_serial_or_batch_or_barcode_number(item)
    if item_data != 0:
        if warehouse:
        #stock = frappe.db.sql("""SELECT item_code,item_name,description,stock_uom,stock_uom as uom,1 as conversion_factor,last_purchase_rate From `tabItem` Where item_code = '%(item_code)s' """%{"item_code": item_data['item_code']}, as_dict = 1)
#         stock = frappe.db.sql("""SELECT item.item_code,item.item_name,item.description,bin.warehouse,bin.actual_qty as available_qty,item.stock_uom,item.stock_uom_conversion_factor,item.uom,item.uom_conversion_factor,item.last_purchase_rate as stock_uom_last_purchase_rate
# From
# (SELECT item.item_code,item.item_name,item.description,item.stock_uom,1 as stock_uom_conversion_factor,
# IFNULL(uom.uom,item.stock_uom) as uom,IFNULL(uom.conversion_factor,1) as uom_conversion_factor,item.last_purchase_rate 
# From `tabItem` item left join `tabUOM Conversion Detail` uom
# ON item.name=uom.parent and uom.conversion_factor>1) item
# LEFT JOIN (Select warehouse,item_code,actual_qty from `tabBin` where actual_qty>0) bin ON (item.item_code=bin.item_code) 
# Where bin.warehouse = '%(warehouse)s' and item.item_code = '%(item_code)s' """%{"warehouse":warehouse,"item_code": item_data['item_code']}, as_dict = 1)
            stock = frappe.db.sql("""SELECT item.name as item_code,item.item_name,item.description,item.last_purchase_rate,standard_price.price_list_rate as standard_price,item.warehouse,item.actual_qty as available_qty,uom_price.uom1,uom_price.conversion_factor1,IFNULL(uom_price.uom1_price,standard_price.price_list_rate) as uom1_price,uom_price.uom2,uom_price.conversion_factor2,uom_price.uom2_price,uom_price.uom3,uom_price.conversion_factor3,uom_price.uom3_price
FROM
(SELECT item.name,item.item_name,item.description,item.last_purchase_rate,bin.warehouse,bin.actual_qty from `tabItem` item LEFT JOIN `tabBin` bin 
ON (item.name=bin.item_code and bin.actual_qty>0)) item
LEFT JOIN 
(SELECT u1.parent,u1.uom1,u1.conversion_factor1,u1.uom1_price,u2.uom2,u2.conversion_factor2,u2.uom2_price,u3.uom3,u3.conversion_factor3,u3.uom3_price FROM
(Select a.parent,a.uom as uom1,a.conversion_factor as conversion_factor1,b.price_list_rate as uom1_price FROM `tabUOM Conversion Detail` a
LEFT JOIN `tabItem Price` b ON (a.parent=b.item_code and b.buying=1 and a.uom=b.uom) where a.idx=1)u1
LEFT JOIN(Select a.parent as parent2,a.uom as uom2,a.conversion_factor as conversion_factor2,b.price_list_rate as uom2_price FROM `tabUOM Conversion Detail` a
LEFT JOIN `tabItem Price` b ON (a.parent=b.item_code and b.buying=1 and a.uom=b.uom) where a.idx=2)u2
ON(u1.parent=u2.parent2)
LEFT JOIN(Select a.parent as parent3,a.uom as uom3,a.conversion_factor as conversion_factor3,b.price_list_rate as uom3_price FROM `tabUOM Conversion Detail` a
LEFT JOIN `tabItem Price` b ON (a.parent=b.item_code and b.buying=1 and a.uom=b.uom) where a.idx=3)u3
ON(u1.parent=u3.parent3))uom_price
ON(item.name=uom_price.parent)
LEFT JOIN `tabItem Price` standard_price 
ON(item.name=standard_price.item_code and standard_price.buying=1 and standard_price.pb_conversion_factor IN(0,1))
Where item.name = '%(item_code)s' and item.warehouse = '%(warehouse)s' """%{"item_code": item_data['item_code'],"warehouse":warehouse}, as_dict = 1)
            return stock
        else :
            stock = frappe.db.sql("""SELECT item.name as item_code,item.item_name,item.description,item.last_purchase_rate,standard_price.price_list_rate as standard_price,item.warehouse,item.actual_qty as available_qty,uom_price.uom1,uom_price.conversion_factor1,IFNULL(uom_price.uom1_price,standard_price.price_list_rate) as uom1_price,uom_price.uom2,uom_price.conversion_factor2,uom_price.uom2_price,uom_price.uom3,uom_price.conversion_factor3,uom_price.uom3_price
FROM
(SELECT item.name,item.item_name,item.description,item.last_purchase_rate,bin.warehouse,bin.actual_qty from `tabItem` item LEFT JOIN `tabBin` bin 
ON (item.name=bin.item_code and bin.actual_qty>0)) item
LEFT JOIN 
(SELECT u1.parent,u1.uom1,u1.conversion_factor1,u1.uom1_price,u2.uom2,u2.conversion_factor2,u2.uom2_price,u3.uom3,u3.conversion_factor3,u3.uom3_price FROM
(Select a.parent,a.uom as uom1,a.conversion_factor as conversion_factor1,b.price_list_rate as uom1_price FROM `tabUOM Conversion Detail` a
LEFT JOIN `tabItem Price` b ON (a.parent=b.item_code and b.buying=1 and a.uom=b.uom) where a.idx=1)u1
LEFT JOIN(Select a.parent as parent2,a.uom as uom2,a.conversion_factor as conversion_factor2,b.price_list_rate as uom2_price FROM `tabUOM Conversion Detail` a
LEFT JOIN `tabItem Price` b ON (a.parent=b.item_code and b.buying=1 and a.uom=b.uom) where a.idx=2)u2
ON(u1.parent=u2.parent2)
LEFT JOIN(Select a.parent as parent3,a.uom as uom3,a.conversion_factor as conversion_factor3,b.price_list_rate as uom3_price FROM `tabUOM Conversion Detail` a
LEFT JOIN `tabItem Price` b ON (a.parent=b.item_code and b.buying=1 and a.uom=b.uom) where a.idx=3)u3
ON(u1.parent=u3.parent3))uom_price
ON(item.name=uom_price.parent)
LEFT JOIN `tabItem Price` standard_price 
ON(item.name=standard_price.item_code and standard_price.buying=1 and standard_price.pb_conversion_factor IN(0,1))
Where item.name = '%(item_code)s' """%{"item_code": item_data['item_code']}, as_dict = 1)
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
    if batch_no_data:
        batch_no_data["type"] = "batch"
        return batch_no_data

    # search serial no
    serial_no_data = frappe.db.get_value('Serial No', search_value, ['name as serial_no', 'item_code'], as_dict=True)
    if serial_no_data:
        serial_no_data["type"] = "item_serial"
        return serial_no_data

    return 0  

@frappe.whitelist()
def create_purchase_receipt(data=None):
    status = frappe.db.get_single_value("Price Checker API Settings", "purchase_receipt_status")
    tax_template = frappe.db.get_single_value("Price Checker API Settings", "default_purchase_tax_template")
    data=json.loads(frappe.request.data)
    if status == "Draft" :
        try:
            prec_doc = frappe.new_doc("Purchase Receipt")
            prec_doc.supplier = data.get("supplier")
            prec_doc.posting_date = today()
            prec_doc.supplier_delivery_note = data.get("supplier_invoice_no")
            prec_doc.supplier_invoice_date = data.get("supplier_invoice_date")
            items=[]
            for item in data["items"]:
                prec_doc.append("items",
                {
                    "item_code": item["item_code"],
                    "item_name": frappe.db.get_value("Item", item["item_code"],"item_name"),
                    "description" : frappe.db.get_value("Item", item["item_code"],"description"),
                    "qty":item["qty"],
                    "rate": item["rate"],
                    "uom": item["uom"],
                    "conversion_factor": item["conversion_factor"],
                    "warehouse": item["warehouse"],
                    "pb_expiry_date" : item["expiry_date"],
                })
            taxes = frappe.db.sql("""SELECT account_head,rate FROM `tabPurchase Taxes API` """, as_dict = 1)
            for row in taxes:
                prec_doc.append("taxes",
                {
                    "category": "Total",
                    "add_deduct_tax": "Add",
                    "charge_type": "On Net Total",
                    "account_head":row["account_head"],
                    "description": "VAT",
                    "rate": row["rate"],
                })
            prec_doc.set_missing_values()
            prec_doc.insert(ignore_permissions=True)
            # prec_doc.submit()
            if prec_doc :
                return prec_doc.name
        except Exception as e:
            return {"error":e}
    else :
        try:
            prec_doc = frappe.new_doc("Purchase Receipt")
            prec_doc.supplier = data.get("supplier")
            prec_doc.posting_date = today()
            prec_doc.supplier_delivery_note = data.get("supplier_invoice_no")
            prec_doc.supplier_invoice_date = data.get("supplier_invoice_date")
            items=[]
            for item in data["items"]:
                prec_doc.append("items",
                {
                    "item_code": item["item_code"],
                    "item_name": frappe.db.get_value("Item", item["item_code"],"item_name"),
                    "description" : frappe.db.get_value("Item", item["item_code"],"description"),
                    "qty":item["qty"],
                    "rate": item["rate"],
                    "uom": item["uom"],
                    "conversion_factor": item["conversion_factor"],
                    "warehouse": item["warehouse"],
                    "pb_expiry_date" : item["expiry_date"],
                })
            taxes = frappe.db.sql("""SELECT account_head,rate FROM `tabPurchase Taxes API` """, as_dict = 1)
            for row in taxes:
                prec_doc.append("taxes",
                {
                    "category": "Total",
                    "add_deduct_tax": "Add",
                    "charge_type": "On Net Total",
                    "account_head":row["account_head"],
                    "description": "VAT",
                    "rate": row["rate"],
                })
            prec_doc.set_missing_values()
            prec_doc.insert(ignore_permissions=True)
            prec_doc.submit()
            frappe.db.commit()
            if prec_doc :
                return prec_doc.name
        except Exception as e:
            return {"error":e}
        
@frappe.whitelist()
def create_prec(supplier,item_code,warehouse,qty,stock_uom,conversion_factor,rate,supplier_invoice_no,supplier_invoice_date):
    status = frappe.db.get_single_value("Price Checker API Settings", "purchase_receipt_status")
    if status == "Draft" :
        try:
            prec_doc = frappe.new_doc("Purchase Receipt")
            prec_doc.supplier = supplier
            prec_doc.posting_date = today()
            prec_doc.supplier_delivery_note = supplier_invoice_no
            prec_doc.supplier_invoice_date = supplier_invoice_date
            prec_doc.append("items",
                {
                    "item_code": item_code,
                    "item_name": frappe.db.get_value("Item",item_code,"item_name"),
                    "description" : frappe.db.get_value("Item",item_code,"description"),
                    "qty":qty,
                    "rate": rate,
                    "stock_uom": stock_uom,
                    # "uom": uom,
                    "conversion_factor": conversion_factor,
                    "warehouse": warehouse
            })
            taxes = frappe.db.sql("""SELECT account_head,rate FROM `tabPurchase Taxes API` """, as_dict = 1)
            for row in taxes:
                prec_doc.append("taxes",
                {
                    "category": "Total",
                    "add_deduct_tax": "Add",
                    "charge_type": "On Net Total",
                    "account_head":row["account_head"],
                    "description": "VAT",
                    "rate": row["rate"],
                })
            prec_doc.set_missing_values()
            prec_doc.insert(ignore_permissions=True)
            # prec_doc.submit()
            # frappe.db.commit()
            if prec_doc :
                return prec_doc.name
        except Exception as e:
            return {"error":e}
    else :
        try:
            prec_doc = frappe.new_doc("Purchase Receipt")
            prec_doc.supplier = supplier
            prec_doc.posting_date = today()
            prec_doc.supplier_delivery_note = supplier_invoice_no
            prec_doc.supplier_invoice_date = supplier_invoice_date
            prec_doc.append("items",
                {
                    "item_code": item_code,
                    "item_name": frappe.db.get_value("Item",item_code,"item_name"),
                    "description" : frappe.db.get_value("Item",item_code,"description"),
                    "qty":qty,
                    "rate": rate,
                    "stock_uom": stock_uom,
                    # "uom": uom,
                    "conversion_factor": conversion_factor,
                    "warehouse": warehouse
                })
            taxes = frappe.db.sql("""SELECT account_head,rate FROM `tabPurchase Taxes API` """, as_dict = 1)
            for row in taxes:
                prec_doc.append("taxes",
                {
                    "category": "Total",
                    "add_deduct_tax": "Add",
                    "charge_type": "On Net Total",
                    "account_head":row["account_head"],
                    "description": "VAT",
                    "rate": row["rate"],
                })
            prec_doc.insert(ignore_permissions=True)
            prec_doc.submit()
            frappe.db.commit()
            if prec_doc :
                return prec_doc.name
        except Exception as e:
            return {"error":e}



