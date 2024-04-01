from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns = [
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 120},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 120},
        {"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 120}, 
        {"label": _("Description"), "fieldname": "description", "fieldtype": "Data", "width": 120}, 
        {"label": _("Invoice Name"), "fieldname": "invoice_name", "fieldtype": "Link", "options": "Purchase Invoice", "width": 130},
        {"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 120}, 
        {"label": _("Supplier"), "fieldname": "default_supplier", "fieldtype": "Link", "options": "Supplier", "width": 120}, 
        {"label": _("Stock UOM"), "fieldname": "stock_uom", "fieldtype": "Data", "width": 120}, 
        {"label": _("Bonus Quantity"), "fieldname": "bonus_qty", "fieldtype": "Float", "width": 120},
        {"label": _("Paid Quantity"), "fieldname": "paid_qty", "fieldtype": "Float", "width": 120},
        {"label": _("Total"), "fieldname": "total_qty", "fieldtype": "Float", "width": 120}, 
        {"label": _("Rate"), "fieldname": "rate", "fieldtype": "Currency", "width": 120},
        {"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 120},
        {"label": _("VAT Rate"), "fieldname": "vat_rate", "fieldtype": "Float", "width": 120},  
        {"label": _("VAT Amount"), "fieldname": "vat_amount", "fieldtype": "Currency", "width": 120},  
        # {"label": _("Item Tax Template"), "fieldname": "item_tax_template", "fieldtype": "Link", "options": "Item Tax", "width": 120},         
        {"label": _("Total Tax"), "fieldname": "total_tax", "fieldtype": "Currency", "width": 120}, 
        {"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 120},
        {"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 120},
    ]

    data = get_data(filters)

    return columns, data

def get_data(filters):
    conditions = ""
    if filters.get("from_date"):
        conditions += " AND pi.posting_date >= '{}'".format(filters["from_date"])
    if filters.get("to_date"):
        conditions += " AND pi.posting_date <= '{}'".format(filters["to_date"])
    if filters.get("item_code"):
        conditions += " AND pii.item_code = '{}'".format(filters["item_code"])
    if filters.get("invoice"):
        conditions += " AND pi.name = '{}'".format(filters["invoice"])
    if filters.get("supplier"):
        conditions += " AND default_supplier = '{}'".format(filters["supplier"])
    if filters.get("company"):
        conditions += " AND pi.company = '{}'".format(filters["company"])

    where_clause = " WHERE pi.docstatus = 1" + conditions if conditions else ""

    sql_query = f"""
        SELECT
            pii.item_code AS item_code,
            pii.item_name AS item_name,            
            item.item_group AS item_group, 
            pii.description AS description, 
            pi.name AS invoice_name,
            pi.posting_date AS posting_date, 
            item_default.default_supplier AS default_supplier,
            pii.uom AS stock_uom, 
            item_tax_detail.tax_rate AS vat_rate, 
            SUM(CASE WHEN pii.rate = 0 THEN pii.qty ELSE 00 END) AS bonus_qty,
            SUM(CASE WHEN pii.rate > 0 THEN pii.qty ELSE 00 END) AS paid_qty,
            SUM(pii.qty) AS total_qty, 
            max_rate.rate AS rate,
            max_rate.amount AS amount,
            pi.taxes_and_charges_added AS total_tax, 
            pi.grand_total AS grand_total,
            pi.company AS company,
            (max_rate.amount * item_tax_detail.tax_rate / 100) AS vat_amount  
        FROM
            `tabPurchase Invoice Item` pii
        JOIN
            `tabPurchase Invoice` pi ON pii.parent = pi.name
        LEFT JOIN
            `tabItem` item ON pii.item_code = item.name
        LEFT JOIN
            `tabItem Tax Template` item_tax ON pii.item_tax_template = item_tax.name
        LEFT JOIN
            `tabItem Tax Template Detail` item_tax_detail ON item_tax_detail.parent = item_tax.name  
        LEFT JOIN (
            SELECT
                item_code,
                MAX(rate) AS rate,
                MAX(amount) AS amount
            FROM
                `tabPurchase Invoice Item`
            WHERE
                rate > 0
            GROUP BY
                item_code
        ) max_rate ON pii.item_code = max_rate.item_code
        LEFT JOIN
            `tabItem Default` item_default ON item_default.parent = pii.item_code
        {where_clause}
        GROUP BY
            pii.item_code, pi.name;
    """

    data = frappe.db.sql(sql_query, as_dict=True)

    return data