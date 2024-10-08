# Copyright (c) 2013, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from erpnext.accounts.report.accounts_payable.accounts_payable import (
    execute as accounts_payable,
)

from pos_bahrain.pos_bahrain.report.accounts_receivable_2.accounts_receivable_2 import (
    extend_report,
)


def execute(filters=None):
    return extend_report(accounts_payable, filters)
