import frappe
from frappe import _
from frappe.utils import getdate
from erpnext.stock.doctype.stock_ledger_entry.stock_ledger_entry import StockLedgerEntry


# =====
# Modified existing source code from
# https://github.com/frappe/erpnext/blob/develop/erpnext/stock/doctype/stock_ledger_entry/stock_ledger_entry.py#L123
# =====
def _validate_batch(self):
    if self.batch_no and self.voucher_type != 'Stock Entry':
        purchase_return = _get_purchase_return(self.voucher_type, self.voucher_no)
        is_return = _get_purchase_return(self.voucher_type, self.voucher_no)
        if self.voucher_type in ['Purchase Invoice', 'Purchase Receipt'] and is_return:
            pass 
        else:
            if not purchase_return:
                expiry_date = frappe.db.get_value('Batch', self.batch_no, 'expiry_date')
                if expiry_date:
                    if getdate(self.posting_date) > getdate(expiry_date):
                        frappe.throw(_('Batch {0} of Item {1} has expired.').format(self.batch_no, self.item_code))


def _get_purchase_return(voucher_type, voucher_no):
    if voucher_type in ['Purchase Invoice', 'Purchase Receipt']:
        return frappe.db.get_value(voucher_type, voucher_no, 'is_return')
    return False


StockLedgerEntry.validate_batch = _validate_batch