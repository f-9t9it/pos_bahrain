import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_field
from frappe.custom.doctype.property_setter.property_setter import make_property_setter


@frappe.whitelist()
def after_install():
    custom_field_pos_profile()


def custom_field_pos_profile():
    create_custom_field(
        "POS Profile",
        {
            "label": _("Series"),
            "fieldname": "naming_series",
            "fieldtype": "Select",
            "options":"[Select]",
            "reqd":1,
            "in_list_view":1,
            "insert_after": "company",
        },
    )