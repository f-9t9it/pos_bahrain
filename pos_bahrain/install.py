import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_field
from frappe.custom.doctype.property_setter.property_setter import make_property_setter


@frappe.whitelist()
def after_install():
    custom_field_quotation()

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