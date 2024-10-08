from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def search_barcode(barcode):
    item_data = search_serial_or_batch_or_barcode_number(barcode)
    # print("/////////",stock)
    if item_data != 0:
        price_and_name = get_price(item_data)
        if price_and_name != 0:
            item_name = frappe.db.sql("""SELECT item_name FROM `tabItem`
                WHERE item_code = '%(item_code)s'"""%{"item_code": item_data['item_code']})[0][0]
            tax_rate = item_tax(item_data['item_code'])

            price_and_name[0]['tax_rate'] =  tax_rate
            if tax_rate != 0:
                rate = price_and_name[0]['price_list_rate']
                tax = price_and_name[0]['tax_rate']
                tax_prcnt =  1 + ( tax / 100) 
                tax_incl = rate * tax_prcnt
                price_and_name[0]['price_list_rate_with_vat'] = tax_incl

            if tax_rate == 0:
                price_and_name[0]['price_list_rate_with_vat'] = price_and_name[0]['price_list_rate']
            price_and_name[0]['item_name'] = item_name

            price_and_name[0]['price_list_rate_with_vat'] = '{:.3f}'.format( price_and_name[0]['price_list_rate_with_vat'] )
            price_and_name[0]['price_list_rate'] = '{:.3f}'.format( price_and_name[0]['price_list_rate'] )
            stock = frappe.db.sql("""SELECT warehouse,actual_qty from `tabBin` WHERE item_code = '%(item_code)s' """%{"item_code": item_data['item_code']}, as_dict = 1)
            return price_and_name+stock

    return "Item/Price not found"
def item_tax(item_code):
    tax_rate = frappe.db.sql("""SELECT ttd.tax_rate as tax_rate
                                FROM `tabItem Tax Template Detail` ttd
                                WHERE ttd.parent = (SELECT it.item_tax_template
                                FROM `tabItem Tax` it WHERE it.parent = '%(item_code)s') LIMIT 1
                                """%{"item_code":item_code}, as_dict = 1)
    
    return int(tax_rate[0]['tax_rate']) if tax_rate else 0

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

def get_price(item_data):
    price_list = frappe.db.get_single_value("Price Checker API Settings", "price_list")
    def get_price_from_price_list(item_data, price_list):
        price_data = frappe.db.sql("""SELECT
                            price_list_rate
                        FROM
                            `tabItem Price`
                        WHERE
                            item_code = '%(item_code)s'
                            AND uom = '%(uom)s'
                            AND price_list = '%(price_list)s'
                            AND selling = 1
                        ORDER BY creation ASC LIMIT 1
                            """%{"item_code" : item_data["item_code"], 
                                "uom" : item_data["pb_uom"],
                                "price_list" : price_list}, as_dict = 1)
        if price_data:
            return price_data

        price_data_2 = frappe.db.sql("""SELECT
                        price_list_rate
                    FROM
                        `tabItem Price`
                    WHERE
                        item_code = '%(item_code)s'
                        AND price_list = '%(price_list)s'
                        AND selling = 1
                    ORDER BY creation ASC LIMIT 1
                        """%{"item_code" : item_data["item_code"],
                            "price_list" : price_list}, as_dict = 1)
        if price_data_2:    
            return price_data_2
        
        price_data_3 = frappe.db.sql("""SELECT
                        price_list_rate
                    FROM
                        `tabItem Price`
                    WHERE
                        item_code = '%(item_code)s'
                        AND price_list = 'Standard Selling'
                        AND selling = 1
                    ORDER BY creation ASC LIMIT 1
                        """%{"item_code" : item_data["item_code"]}, as_dict = 1)
        if price_data_3:
            return price_data_3
        return 0

    if item_data["type"] == "item_barcode":
        price_data = get_price_from_price_list(item_data, price_list)
        return price_data

    if item_data["type"] == "item_code":
        price_data = get_price_from_price_list(item_data, price_list)
        return price_data
    
    if item_data["type"] == "batch":
        price_data = {}
        batch_data = frappe.db.sql("""SELECT pb_price_based_on, pb_rate, pb_discount
                                    FROM `tabBatch`
                                    WHERE name = '%(name)s'""" %{"name":item_data['batch_no']}, as_dict = 1)
        if batch_data:
            batch_data = batch_data[0]
        if batch_data['pb_price_based_on'] == "Based on Rate":
            price_data["price_list_rate"] = batch_data['pb_rate']
        if batch_data['pb_price_based_on'] == "Based on Discount" or batch_data['pb_price_based_on'] == "":
            item_data['pb_uom'] = ""
            price_data = get_price_from_price_list(item_data, price_list)
            if batch_data['pb_price_based_on'] == "Based on Discount":
                price_data["price_list_rate"] = price_data['price_list_rate'] * batch_data['pb_price_based_on']
        return [price_data]
    
    if item_data["type"] == "item_serial":
        return item_data

    return 0

@frappe.whitelist()        
def warehouse_stock(barcode):
    item_data = search_serial_or_batch_or_barcode_number(barcode)
    if item_data != 0:
        stock = frappe.db.sql("""SELECT warehouse,actual_qty from `tabBin` WHERE item_code = '%(item_code)s' """%{"item_code": item_data['item_code']}, as_dict = 1)
        return stock    