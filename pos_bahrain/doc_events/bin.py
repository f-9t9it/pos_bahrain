# -*- coding: utf-8 -*-
# Copyright (c) 2020, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals


from pos_bahrain.api.bin import set_item_price_from_bin


def on_update(doc, method):
    set_item_price_from_bin(doc)
