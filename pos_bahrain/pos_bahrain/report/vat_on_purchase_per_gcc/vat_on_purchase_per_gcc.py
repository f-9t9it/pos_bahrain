# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

from pos_bahrain.pos_bahrain.report.vat_on_sales_per_gcc.vat_on_sales_per_gcc import (
    make_report,
)


def execute(filters=None):
    return make_report("Purchase Invoice", filters)
