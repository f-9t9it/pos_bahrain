# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def execute(filters=None):
    from pos_bahrain.pos_bahrain.report.item_wise_sales_register_simple.item_wise_sales_register_simple import (
        execute,
    )

    return execute(filters, transaction_type="Purchase")
