import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_field
from frappe.custom.doctype.property_setter.property_setter import make_property_setter


@frappe.whitelist()
def after_install():
    custom_field_quotation()
    property_setter()

def custom_field_quotation():
    create_custom_field(
        "Quotation",
        {
            "label": _("Packed Items"),
            "fieldname": "packed_items",
            "fieldtype": "Table",
            "insert_after": "items",
            "options": "Packed Item",

        },
    )
    create_custom_field(
        "Purchase Order",
        {
            "label": _("Purchase Invoice Date"),
            "fieldname": "purchase_invoice_date",
            "fieldtype": "Date",
            "insert_after": "schedule_date",
             

        },
    )
def property_setter():
    make_property_setter(
        "Purchase Order",
        "purchase_invoice_date",
        "allow_on_submit",
        1,
        "Check"
        
         
    )