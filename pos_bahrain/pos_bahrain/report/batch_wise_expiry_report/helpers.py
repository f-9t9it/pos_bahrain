import frappe
from frappe.utils import flt
from functools import reduce
from toolz import groupby, merge, concat, compose

from pos_bahrain.utils.report import make_column


def get_uom_columns(num_of_columns):
    def uom_columns(x):
        return [
            make_column("uom{}".format(x), "UOM {}".format(x), width=90),
            make_column(
                "cf{}".format(x),
                "Coversion Factor {}".format(x),
                type="Float",
                width=90,
            ),
            make_column("qty{}".format(x), "Qty {}".format(x), type="Float", width=90),
        ]

    join_columns = compose(list, concat)

    return join_columns([uom_columns(x + 1) for x in range(0, num_of_columns)])


def make_uom_col_setter(item_codes):
    uoms_by_item_code = groupby(
        "item_code",
        frappe.db.sql(
            """
            SELECT
                i.name AS item_code,
                ucd.uom AS uom,
                ucd.conversion_factor AS conversion_factor
            FROM `tabUOM Conversion Detail` AS ucd
            LEFT JOIN `tabItem` AS i ON i.name = ucd.parent
            WHERE ucd.parent IN %(parent)s AND ucd.uom != i.stock_uom
        """,
            values={"parent": item_codes},
            as_dict=1,
        ),
    )

    precision = frappe.defaults.get_global_default("float_precision")

    def fn(row):
        def get_detail(i, detail):
            qty = flt(row.get("qty") or 0, precision)
            cf = flt(detail.get("conversion_factor"), precision)
            return {
                "uom{}".format(i + 1): detail.get("uom"),
                "cf{}".format(i + 1): cf,
                "qty{}".format(i + 1): flt(qty / cf, precision) if cf else None,
            }

        details = uoms_by_item_code.get(row.get("item_code"), [])
        fields = reduce(lambda a, x: merge(a, get_detail(*x)), enumerate(details), {})
        return merge(row, fields)

    return fn
