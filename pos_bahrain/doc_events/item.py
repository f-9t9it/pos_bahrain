import frappe
from erpnext.controllers.item_variant import (ItemVariantExistsError,
		copy_attributes_to_variant, get_variant, make_variant_item_code, validate_item_variant_attributes)
from frappe.utils import (cint, cstr, flt, formatdate, get_timestamp, getdate,
						  now_datetime, random_string, strip)

def custom_autoname_before_insert(doc, method=None):
	try:
		if frappe.db.get_default("item_naming_by") == "Naming Series":
			if doc.variant_of:
				if not doc.item_code:
					template_item_name = frappe.db.get_value("Item", doc.variant_of, "item_name")
					doc.item_code = make_variant_item_code(doc.variant_of, template_item_name, doc)
			else:
				from frappe.model.naming import set_name_by_naming_series
				set_name_by_naming_series(doc)
				doc.item_code = doc.name

		doc.item_code = strip(doc.item_code)
		doc.name = doc.item_code
	except Exception as e:
		  frappe.throw(f"{e}")