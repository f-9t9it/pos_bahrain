# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__

app_name = "pos_bahrain"
app_version = __version__
app_title = "Pos Bahrain"
app_publisher = "	9t9it"
app_description = "Pos Customization"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "hafeesk@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/css/pos_css.css"
# app_include_js = "/assets/pos_bahrain/js/pos_bahrain.js"
app_include_css = "/assets/css/jmi.min.css"
app_include_js = [
    "/assets/js/jmi.min.js",
    "/assets/js/pos_bahrain.min.js",
    "/assets/pos_bahrain/js/batch_quick_entry.js",
    "/assets/pos_bahrain/js/meta.js",
    "pos_bahain/public/js/taxes_and_totals.js",
]

# include js, css files in header of web template
# web_include_css = "/assets/pos_bahrain/css/pos_bahrain.css"
# web_include_js = "/assets/pos_bahrain/js/pos_bahrain.js"

# include js in page--------offline POS----
# page_js = {
#     "pos": "public/js/pos_page_js.js",
#     "point-of-sale": "public/js/pos_page_js.js",
# }

# include js in doctype views
doctype_js = {
    "Mode of Payment": "public/js/mode_of_payment.js",
    "Stock Entry": ["public/js/includes/scan_barcode.js", "public/js/stock_entry.js"],
    "Company": "public/js/company.js",
    "Quotation": [
        "public/js/price_list.js",
        "public/js/quotation.js",
        "public/js/includes/discount_percentage.js",
    ],
    "Sales Invoice": [
        "public/js/alternate_discount.js",
        "public/js/includes/scan_barcode.js",
        "public/js/price_list.js",
        "public/js/branch.js",
        "public/js/sales_invoice.js",
        "public/js/includes/discount_percentage.js",
        # "public/js/includes/salesinvoicecontroller.js",
    ],
    "Sales Order": [
        "public/js/alternate_discount.js",
        "public/js/price_list.js",
        "public/js/branch.js",
        "public/js/includes/discount_percentage.js",
        "public/js/sales_order.js",
    ],
    "Purchase Invoice": [
        "public/js/set_retail_price.js",
        "public/js/includes/scan_barcode.js",
        "public/js/branch.js",
        "public/js/purchase_invoice.js",
    ],
    "Purchase Order": [
        "public/js/set_retail_price.js",
        "public/js/purchase_order.js",
    ],
    "Purchase Receipt": [
        "public/js/includes/scan_barcode.js",
        "public/js/purchase_receipt.js",
    ],
    "Payment Entry": [
         "public/js/payment_entry.js"
    ],
    "Material Request": "public/js/material_request.js",
    "Delivery Note": "public/js/delivery_note.js",
    "Print Format": "public/js/print_format.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                [
                    "Sales Invoice-pos_total_qty",
                    "Mode of Payment-currency_section",
                    "Mode of Payment-in_alt_currency",
                    "Mode of Payment-alt_currency",
                    "Mode of Payment-pb_alt_col",
                    "Mode of Payment-pb_bank_method",
                    "POS Profile-pb_max_discount",
                    "Sales Invoice Payment-pos_section",
                    "Sales Invoice Payment-mop_currency",
                    "Sales Invoice Payment-cb11",
                    "Sales Invoice Payment-mop_conversion_rate",
                    "Sales Invoice Payment-mop_amount",
                    "Sales Invoice Payment-pb_ref_sec",
                    "Sales Invoice Payment-pb_reference_no",
                    "Sales Invoice Payment-pb_reference_date",
                    "Batch-naming_series",
                    "Company-default_warehouse",
                    "Sales Invoice-pb_set_cost_center",
                    "Sales Invoice-pb_sales_employee",
                    "Sales Invoice-pb_sales_employee_name",
                    "Sales Invoice-discount_on_retail_price",
                    "Sales Invoice Item-other_prices_section",
                    "Sales Invoice Item-retail_price",
                    "Sales Invoice Item-discount_percentage_on_retail",
                    "Sales Order-discount_on_retail_price",
                    "Sales Order Item-other_prices_section",
                    "Sales Order Item-retail_price",
                    "Sales Order Item-discount_percentage_on_retail",
                    "Purchase Receipt-pb_scan_barcode",
                    "Purchase Invoice-pb_set_cost_center",
                    "Purchase Invoice Item-retail_price",
                    "Purchase Invoice Item-pb_supplier_part_no",
                    "Purchase Receipt Item-pb_supplier_part_no",
                    "Purchase Order-pb_get_items_from_default_supplier",
                    "Purchase Order Item-pb_supplier_part_no",
                    "Purchase Order Item-retail_price",
                    "Purchase Order Item-pb_actual_qty",
                    "Batch-pb_price_sec",
                    "Batch-pb_price_based_on",
                    "Batch-pb_price_col",
                    "Batch-pb_rate",
                    "Batch-pb_discount",
                    "Sales Order Item-batch_no",
                    "Item Barcode-pb_uom",
                    "Purchase Receipt Item-pb_expiry_date",
                    "Purchase Invoice Item-pb_expiry_date",
                    "Stock Entry Detail-pb_expiry_date",
                    "Journal Entry-pb_is_cheque",
                    "Payment Entry Reference-pb_invoice_date",
                    "Item Price-pb_conversion_factor",
                    "Item Price-pb_customer_name",
                    "Payment Entry-pb_branch",
                    "Payment Entry-pb_pos_profile",
                    "Payment Entry-pb_posting_time",
                    "Sales Invoice Item-salesman_name",
                    "Sales Invoice Item-salesman",
                    "Warehouse-pb_cost_center",
                    "Item-pb_storage_location_sb",
                    "Item-pb_storage_location",
                    "Sales Order Item-pb_price_list",
                    "Sales Invoice Item-pb_price_list",
                    "Branch-branch_code",
                    "Branch-disabled",
                    "Branch-pb_main_col",
                    "Branch-pb_user",
                    "Branch-pb_sales_sec",
                    "Branch-pb_sales_order_naming_series",
                    "Branch-pb_sales_invoice_naming_series",
                    "Branch-pb_sales_col",
                    "Branch-pb_cost_center",
                    "Branch-pb_targets_sec",
                    "Branch-pb_half_monthly_target",
                    "Branch-pb_target",
                    "Branch-pb_targets_col",
                    "Branch-pb_quarterly_target",
                    "Branch-pb_half_yearly_target",
                    "Branch-pb_yearly_target",
                    "Branch-pb_details_sec",
                    "Branch-warehouse",
                    "Branch-location",
                    "Branch-branch_phone",
                    "Branch-pb_email",
                    "Branch-pb_details_col",
                    "Branch-pb_nhra_license",
                    "Branch-pb_nhra_expiry",
                    "Branch-pb_cr_no",
                    "Branch-pb_cr_expiry",
                    "Stock Entry-pb_reference_stock_transfer",
                    "Stock Entry-pb_repack_request",
                    "Material Request-pb_to_warehouse",
                    "Sales Order-pb_branch",
                    "Sales Invoice-pb_branch",
                    "Sales Order Item-pb_location",
                    "Sales Invoice Item-pb_location",
                    "Sales Order Item-pb_price_list_rate",
                    "Sales Invoice Item-pb_price_list_rate",
                    "Quotation Item-pb_price_list_cb",
                    "Quotation Item-pb_price_list",
                    "Quotation Item-pb_price_list_rate",
                    "Sales Order Item-pb_branch",
                    "Sales Order Item-pb_branch_qty",
                    "Sales Invoice Item-pb_branch",
                    "Sales Invoice Item-pb_branch_qty",
                    "Purchase Invoice Item-pb_branch",
                    "Purchase Invoice Item-pb_branch_qty",
                    "Sales Invoice Item-pb_quotation",
                    "Quotation-pb_discount_percentage",
                    "Sales Order-pb_discount_percentage",
                    "Sales Invoice-pb_discount_percentage",
                    "Sales Invoice-pb_available_balance",
                    "Sales Invoice-pb_after_balance",
                    "Sales Invoice-pb_returned_to_warehouse",
                    "Sales Invoice-delivery_later",
                    "Sales Invoice-ws_remarks",
                    "Sales Invoice-delivery_date",
                    "Sales Invoice-pb_credit_note_no",
                    "Sales Invoice-old_si_no",
                    "Sales Invoice-reference_no",
                    "Sales Invoice-credit_note",
                    "Sales Invoice-pb_use_credit_if_available",
                    "Sales Invoice-customer_price_list",
                    "Sales Invoice-apply_offer",
                    "Sales Invoice-return_si_no",
                    "Sales Invoice-main_invoice",
                    "Sales Order-delivery_later",
                    "Sales Order-ws_remarks",
                    "Sales Order-transaction_time",
                    "Sales Order-pb_sales_employee",
                    "Sales Order-pb_sales_employee_name",
                    "Sales Order-customer_price_list",
                    "Sales Order-apply_offer",
                    "Sales Order-workflow_state",
                    "Sales Invoice-orx_dispensor",
                    "Sales Invoice-pb_notes",
                    "Sales Invoice Item-pb_minimum_selling_2_rate",
                    "Sales Invoice Item-pb_minimum_selling_rate",
                    "Quotation-ws_remarks",
                    "Quotation-pb_sales_employee",
                    "Quotation-pb_sales_employee_name",
                    "Quotation-customer_price_list",
                    "Quotation-apply_offer",
                    "Customer-pb_contact_person",
                    "Customer-pb_mobile_number",
                    "Customer-pb_email_address",
                    "Customer-pb_address",
                    "Customer-pb_city",
                    "Customer-cr_no",
                    "Customer-pb_country",
                    "Customer-customer_price_list",
                    "Purchase Receipt-supplier_invoice_date",
                    "Sales Invoice-credit_note_balance",
                    "Sales Invoice-main_si",
                    "Sales Invoice-credit_note_invoice",
                    "Sales Invoice-ignore_payments_for_return",
                    "Purchase Receipt Item-pb_description",
                    "Purchase Invoice Item-pb_description",
                    "Sales Order Item-pb_description",
                    "Purchase Order Item-pb_description",
                    "Sales Invoice Item-pb_description",
                    "Quotation Item-pb_description",
                    "Item-pb_description",
                    "Item-authorized_representative_name",
                    "Item-authorized_representative_email_field",
                    "authorized_representative_contact_person_number",
                    "Quotation-sales_order",
                    "Sales Invoice-mobile_no",
                    "Sales Invoice-phone",
                    "Sales Invoice-email_id",
                ],
            ],
        ],
    },
    {
        "doctype": "Property Setter",
        "filters": [
            [
                "name",
                "in",
                [
                    "Batch-search_fields",
                    "Batch-batch_id-reqd",
                    "Batch-batch_id-bold",
                    "Batch-expiry_date-in_list_view",
                    "Batch-expiry_date-bold",
                    "Sales Invoice Item-discount_percentage-precision",
                    "Sales Invoice Item-discount_percentage-depends_on",
                    "Sales Order Item-discount_percentage-precision",
                    "Sales Order Item-discount_percentage-depends_on",
                    "Payment Entry Reference-total_amount-in_list_view",
                    "Sales Invoice-customer_name-default",
                ],
            ]
        ],
    },
]

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "pos_bahrain.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "pos_bahrain.install.before_install"
# after_install = "pos_bahrain.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "pos_bahrain.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "*": {
        "validate": "pos_bahrain.doc_events.sales_controller.validate",
    },
    "Sales Order": {
        "before_save": "pos_bahrain.doc_events.sales_order.before_save",
        "on_submit": "pos_bahrain.doc_events.sales_order.on_submit",
        "before_cancel": "pos_bahrain.doc_events.sales_order.before_cancel",
    },
    "Sales Invoice": {
        "validate": "pos_bahrain.doc_events.sales_invoice.validate",
        "before_save": "pos_bahrain.doc_events.sales_invoice.before_save",
        "on_submit": "pos_bahrain.doc_events.sales_invoice.on_submit",
        "before_cancel": "pos_bahrain.doc_events.sales_invoice.before_cancel",
        "on_cancel": "pos_bahrain.doc_events.sales_invoice.on_cancel",
    },
    "Journal Entry": {
        # "before_cancel": "pos_bahrain.doc_events.journal_entry.cancel_jv",
        "on_cancel": "pos_bahrain.doc_events.journal_entry.on_cancel",
    },
    "Purchase Receipt": {
        "before_save": "pos_bahrain.doc_events.purchase_receipt.before_validate",
        "on_submit": "pos_bahrain.doc_events.purchase_receipt.set_batch_references",
    },
    "Purchase Invoice": {
        "before_save": [
            "pos_bahrain.doc_events.purchase_invoice.before_validate",
            "pos_bahrain.doc_events.purchase_invoice.before_save",
        ],
        "on_submit": "pos_bahrain.doc_events.purchase_receipt.set_batch_references",
    },
    "Payment Entry": {
        "before_save": "pos_bahrain.doc_events.payment_entry.before_save"
    },
    "Stock Entry": {
        "before_save": "pos_bahrain.doc_events.stock_entry.before_validate",
        "on_submit": [
            "pos_bahrain.doc_events.purchase_receipt.set_batch_references",
            "pos_bahrain.doc_events.stock_entry.on_submit",
        ],
    },
    "Item Price": {"before_save": "pos_bahrain.doc_events.item_price.before_save"},
    "Bin": {"on_update": "pos_bahrain.doc_events.bin.on_update"},
    "Bank Reconciliation": {
        "get_payment_entries": "pos_bahrain.doc_events.bank_reconciliation.get_payment_entries",
        "update_clearance_date": "pos_bahrain.doc_events.bank_reconciliation.update_clearance_date",
    },
}

boot_session = "pos_bahrain.doc_events.boot.boot_session"
on_session_creation = "pos_bahrain.doc_events.set_user_defaults"

# Scheduled Tasks
# ---------------

scheduler_events = {
    "daily": ["pos_bahrain.scheduler_events.daily.send_email_to_manager"]
}
# scheduler_events = {
# 	"all": [
# 		"pos_bahrain.tasks.all"
# 	],
# 	"daily": [
# 		"pos_bahrain.tasks.daily"
# 	],
# 	"hourly": [
# 		"pos_bahrain.tasks.hourly"
# 	],
# 	"weekly": [
# 		"pos_bahrain.tasks.weekly"
# 	]
# 	"monthly": [
# 		"pos_bahrain.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "pos_bahrain.install.before_tests"
# Overrding Class
# override_doctype_class = {
#     "Sales Invoice": "pos_bahrain.api.sales_invoice.CustomAccountsController"
# }
# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
#     "erpnext.stock.get_item_details.get_item_details": "pos_bahrain.api.get_item_details.get_item_details",  # noqa
#     "erpnext.accounts.doctype.sales_invoice.pos.get_pos_data": "pos_bahrain.api.item.get_pos_data",  # noqa
#     "erpnext.accounts.doctype.sales_invoice.pos.make_invoice": "pos_bahrain.api.pos.make_invoice",  # noqa
#     "erpnext.selling.page.point_of_sale.point_of_sale.search_serial_or_batch_or_barcode_number": "pos_bahrain.api.item.search_serial_or_batch_or_barcode_number" # noqa
# }


jenv = {
    "methods": [
        "get_workflow_user_received:pos_bahrain.api.stock_transfer.get_workflow_user_received",
    ]
}

'''
override default delete_auto_created_batches_override in erpnext.controllers.stock_controller.StockController class
to enable the user to cancel purchase receipt

'''
from erpnext.controllers.stock_controller import StockController
# import frappe

def delete_auto_created_batches_override(self):
	import frappe
	dont_delete_batch = frappe.db.get_single_value('POS Bahrain Settings', "do_not_delete_batch_with_purchase_receipt")
	if dont_delete_batch and (self.doctype == 'Purchase Receipt' or self.doctype == 'Purchase Invoice'):
		return
		
	for d in self.items:
		if not d.batch_no: continue

		serial_nos = [sr.name for sr in frappe.get_all("Serial No",
			{'batch_no': d.batch_no, 'status': 'Inactive'})]

		if serial_nos:
			frappe.db.set_value("Serial No", { 'name': ['in', serial_nos] }, "batch_no", None)

		d.batch_no = None
		d.db_set("batch_no", None)

	for data in frappe.get_all("Batch",
		{'reference_name': self.name, 'reference_doctype': self.doctype}):
		frappe.delete_doc("Batch", data.name)

StockController.delete_auto_created_batches = delete_auto_created_batches_override

from erpnext.controllers.accounts_controller import AccountsController as _AccountsController
# from erpnext.accounts import utils
from erpnext.controllers import sales_and_purchase_return as _sales_and_purchase_return
from erpnext.controllers import taxes_and_totals as _taxes_and_totals
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
from pos_bahrain.api.sales_invoice import set_advances_ov,get_advance_entries,reconcile_against_document_ov,update_against_document_in_jv_ov,validate_pos_paid_amount_ov
from pos_bahrain.api.sales_and_purchase_return import set_missing_values
from pos_bahrain.api.taxes_and_totals import calculate_change_amount,calculate_write_off_amount,update_paid_amount_for_return_ov
_AccountsController.set_advances = set_advances_ov
_AccountsController.get_advance_entries = get_advance_entries
_AccountsController.update_against_document_in_jv = update_against_document_in_jv_ov
_taxes_and_totals.calculate_write_off_amount = calculate_write_off_amount
# _taxes_and_totals.update_paid_amount_for_return = update_paid_amount_for_return_ov
SalesInvoice.validate_pos_paid_amount = validate_pos_paid_amount_ov