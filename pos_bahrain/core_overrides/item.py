import frappe
from erpnext.stock.doctype.item.item import Item
from frappe import _, msgprint
from frappe.utils import (cint, cstr, flt, formatdate, get_timestamp, getdate,
						  now_datetime, random_string, strip, get_link_to_form)

def custom_onload(self):
		# super(Item, self).onload()
    self.set_onload('stock_exists', custom_stock_ledger_created(self))
    self.set_asset_naming_series()
                
def custom_stock_ledger_created(self):
    bin_qty = frappe.db.sql("""
        select sum(tb.actual_qty) from tabBin tb where item_code = %s
    """, (self.name,))

    qty = bin_qty[0][0] if bin_qty and bin_qty[0] and bin_qty[0][0] is not None else 0  # Extract numeric value

    return 1 if qty > 0 else 0 


def custom_cant_change(self):
    frappe.log_error(title="Custom custom_cant_change",message= "Custom custom_cant_change")
    if not self.get("__islocal"):
        fields = ("has_serial_no", "is_stock_item", "valuation_method", "has_batch_no")

        values = frappe.db.get_value("Item", self.name, fields, as_dict=True)
        if not values.get('valuation_method') and self.get('valuation_method'):
            values['valuation_method'] = frappe.db.get_single_value("Stock Settings", "valuation_method") or "FIFO"

        if values:
            for field in fields:
                if cstr(self.get(field)) != cstr(values.get(field)):
                    if not self.check_if_linked_document_exists(field):
                        break # no linked document, allowed
                    # else:
                    # 	frappe.throw(_("As there are existing transactions against item {0}, you can not change the value of {1}").format(self.name, frappe.bold(self.meta.get_label(field))))

Item.onload = custom_onload
Item.cant_change = custom_cant_change
Item.stock_ledger_created = custom_stock_ledger_created