# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.accounts.report.item_wise_sales_register.item_wise_sales_register import (
    execute as item_wise_sales_register,
)

from pos_bahrain.pos_bahrain.report.sales_register_with_employee.sales_register_with_employee import (
    extend_report,
)


def execute(filters=None):
    filters.net_amount_col = "amount"
    filters["date_range"] = [filters.get("from_date"), filters.get("to_date")]
    return extend_report(item_wise_sales_register, filters)

