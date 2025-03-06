import frappe
from erpnext.stock.doctype.item.item import Item

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

Item.onload = custom_onload