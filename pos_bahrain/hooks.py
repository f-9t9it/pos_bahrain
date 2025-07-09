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
]

# include js, css files in header of web template
# web_include_css = "/assets/pos_bahrain/css/pos_bahrain.css"
# web_include_js = "/assets/pos_bahrain/js/pos_bahrain.js"

# include js in page
page_js = {
    "pos": ["public/js/pos_page_js.js", "public/js/includes/number_to_words.js"],
    "point-of-sale": "public/js/pos_page_js.js",
}

# include js in doctype views
doctype_js = {
    "Mode of Payment": "public/js/mode_of_payment.js",
    "Stock Entry": ["public/js/includes/scan_barcode.js", "public/js/stock_entry.js"],
    "Company": "public/js/company.js",
    "Sales Invoice": [
        "public/js/alternate_discount.js",
        "public/js/includes/scan_barcode.js",
        "public/js/sales_invoice.js",
        "public/js/branch.js",
        "public/js/includes/discount_percentage.js",
    ],
    "Sales Order": [
        "public/js/alternate_discount.js",
        "public/js/includes/discount_percentage.js",
    ],
    "Purchase Invoice": [
        "public/js/set_retail_price.js",
        "public/js/includes/scan_barcode.js",
        "public/js/batch_no_qty.js",
        "public/js/branch.js",
    ],
    "Purchase Order": "public/js/set_retail_price.js",
    "Purchase Receipt": "public/js/includes/scan_barcode.js",
    "Material Request": "public/js/material_request.js",
    "Quotation": [
        "public/js/quotation.js",
        "public/js/includes/discount_percentage.js",
    ],
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
                    "Payment Entry-pb_posting_time",
                    "Sales Invoice Item-salesman_name",
                    "Sales Invoice Item-salesman",
                    "Warehouse-pb_cost_center",
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
                    "Sales Invoice-pb_related_pi",
                    "Purchase Invoice Item-pb_branch",
                    "Purchase Invoice Item-pb_branch_qty",
                    "Sales Invoice Item-pb_branch",
                    "Sales Invoice Item-pb_branch_qty",
                    "Quotation-pb_discount_percentage",
                    "Sales Order-pb_discount_percentage",
                    "Sales Invoice-pb_discount_percentage",
                    "Item-authorized_representative_name",
                    "Item-authorized_representative_contact",
                    "Item-authorized_representative_email",
                ],
            ]
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
    "Sales Invoice": {
        "validate": "pos_bahrain.doc_events.sales_invoice.validate",
        "before_save": "pos_bahrain.doc_events.sales_invoice.before_save",
        "on_submit": "pos_bahrain.doc_events.sales_invoice.on_submit",
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
        "on_submit": [
            "pos_bahrain.doc_events.purchase_invoice.on_submit",
            "pos_bahrain.doc_events.purchase_receipt.set_batch_references",
        ],
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
    "Contact" : {"validate": "pos_bahrain.doc_events.contact.update_customer_phone"}, 
    "Item":{"before_insert":"pos_bahrain.doc_events.item.custom_autoname_before_insert"},
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

# Overriding Whitelisted Methods
# ------------------------------
#
override_whitelisted_methods = {
    "erpnext.stock.get_item_details.get_item_details": "pos_bahrain.api.get_item_details.get_item_details",  # noqa
    "erpnext.accounts.doctype.sales_invoice.pos.get_pos_data": "pos_bahrain.api.item.get_pos_data",  # noqa
    "erpnext.accounts.doctype.sales_invoice.pos.make_invoice": "pos_bahrain.api.pos.make_invoice",  # noqa
    "erpnext.selling.page.point_of_sale.point_of_sale.search_serial_or_batch_or_barcode_number": "pos_bahrain.api.item.search_serial_or_batch_or_barcode_number",  # noqa
}
