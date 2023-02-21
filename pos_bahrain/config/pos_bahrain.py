from frappe import _
import frappe


def get_data():
    def make_item(type, name, label, is_query_report=None):
        return {
            "type": type,
            "name": name,
            "label": _(label),
            "is_query_report": is_query_report,
        }

    def make_section(label, items):
        return {"label": _(label), "items": items}

    return [
        make_section(
            "Reports",
            [
                make_item(
                    "report", "Item Consumption Report", "Item Consumption Report", True
                ),
                make_item(
                    "report",
                    "Batch-wise Expiry Report",
                    "Batch-wise Expiry Report",
                    True,
                ),
                make_item(
                    "report",
                    "Customer Item-wise Sales",
                    "Customer Item-wise Sales",
                    True,
                ),
                make_item(
                    "report", "Customer Sales Summary", "Customer Sales Summary", True
                ),
                make_item(
                    "report",
                    "Item-wise Periodic Sales for Customer",
                    "Item-wise Periodic Sales for Customer",
                    True,
                ),
                make_item(
                    "report", "Item-wise Sales Returns", "Item-wise Sales Returns", True
                ),
                make_item(
                    "report", "Simple Sales Register", "Simple Sales Register", True
                ),
                make_item(
                    "report",
                    "Simple Purchase Register",
                    "Simple Purchase Register",
                    True,
                ),
                make_item(
                    "report",
                    "Sales Person Item-wise Sales",
                    "Sales Person Item-wise Sales",
                    True,
                ),
                make_item("report", "Daily Sales Summary", "Daily Sales Summary", True),
                make_item(
                    "report",
                    "Item Balance (Simple) with Supplier",
                    "Item Balance (Simple) with Supplier",
                    True,
                ),
                make_item(
                    "report", "Stock Ledger (Simple)", "Stock Ledger (Simple)", True
                ),
                make_item("report", "Daily Cash", "Daily Cash", True),
                make_item(
                    "report",
                    "Item-wise Sales Register Simple",
                    "Item-wise Sales Register Simple",
                    True,
                ),
                make_item("report", "Cheque Summary", "Cheque Summary", True),
                make_item("report", "Cash Account", "Cash Account", True),
                make_item(
                    "report", "Daily Item-wise Sales", "Daily Item-wise Sales", True
                ),
                make_item(
                    "report", "Daily Cash with Payment", "Daily Cash with Payment", True
                ),
                make_item(
                    "report",
                    "Stock Balance with Prices",
                    "Stock Balance with Prices",
                    True,
                ),
                make_item(
                    "report",
                    "Sales and Purchase History",
                    "Sales and Purchase History",
                    True,
                ),
                make_item(
                    "report",
                    "Item-wise Purchase Register Simple",
                    "Item-wise Purchase Register Simple",
                    True,
                ),
                make_item("report", "Accounts Payable 2", "Accounts Payable 2", True),
                make_item(
                    "report", "Accounts Receivable 2", "Accounts Receivable 2", True
                ),
                make_item(
                    "report",
                    "Sales Register with Employee",
                    "Sales Register with Employee",
                    True,
                ),
                make_item(
                    "report",
                    "Bank Reconciliation Statement PB",
                    "Bank Reconciliation Statement PB",
                    True,
                ),
                make_item(
                    "report",
                    "Item-wise Sales with Stock Balance",
                    "Item-wise Sales with Stock Balance",
                    True,
                ),
                make_item(
                    "report",
                    "Item-wise Sales Register with Employee",
                    "Item-wise Sales Register with Employee",
                    True,
                ),
                make_item("report", "Hourly Sales", "Hourly Sales", True),
                make_item("report", "VAT Return", "VAT Return", True),
                make_item("report", "VAT on Sales per GCC", "VAT on Sales per GCC", True),
                make_item("report", "VAT on Purchase per GCC", "VAT on Purchase per GCC", True),
                make_item("report", "Stock Item Cost", "Stock Item Cost", True),
                make_item("report", "Stock Cost Summary", "Stock Cost Summary", True),
                make_item("report", "Purchase Analytics with Warehouse", "Purchase Analytics with Warehouse", True),
                make_item("report", "Sales Analytics with Warehouse", "Sales Analytics with Warehouse", True),
                make_item("report", "Branch Stock And Value", "Branch Stock And Value", True),
                make_item("report", "General Ledger with Party Names", "General Ledger with Party Names", True),
                make_item("report", "General Ledger Customized", "General Ledger Customized", True),
                make_item("report", "Sales Gross Profit", "Sales Gross Profit", True),
                make_item("report", "Sales summary by product", "Sales summary by product", True),
            ],
        ),
        make_section(
            "Documents",
            [
                make_item("doctype", "Opening Cash", "Opening Cash"),
                make_item("doctype", "Barcode Print", "Barcode Print"),
                make_item("doctype", "Branch Barcode Print", "Branch Barcode Print"),
                make_item(
                    "doctype",
                    "Backported Stock Reconciliation",
                    "Backported Stock Reconciliation",
                ),
                make_item("doctype", "Payment Entry PB", "Payment Entry PB"),
                make_item("doctype", "POS Closing Voucher", "POS Closing Voucher"),
                make_item("doctype", "Day Closing Voucher", "Day Closing Voucher"),
                make_item("doctype", "Batch Recall", "Batch Recall"),
                make_item("doctype", "Stock Transfer", "Stock Transfer"),
                make_item("doctype", "Repack Request", "Repack Request"),
                make_item("doctype", "Price Check", "Price Check"),
                make_item("doctype", "Stock Adjustment And PREC API", "Stock Adjustment And PREC API"),
            ],
        ),
        make_section(
            "Setup",
            [make_item("doctype", "POS Bahrain Settings", "POS Bahrain Settings"),
            make_item("doctype", "Price Checker API Settings", "Price Checker API Settings")],
        ),
    ]
