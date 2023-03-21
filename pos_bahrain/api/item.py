# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import today
from frappe.desk.reportview import get_filters_cond
from erpnext.stock.get_item_details import (
    get_item_price,
    get_batch_qty,
    get_default_cost_center,
)
from erpnext.stock.doctype.item.item import get_item_defaults
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from functools import partial
from toolz import groupby, merge, valmap, compose, get, excepts, first, pluck

from pos_bahrain.utils import key_by


@frappe.whitelist()
def get_pos_data():
    from erpnext.accounts.doctype.sales_invoice.pos import get_pos_data

    get_price = compose(
        partial(get, "price_list_rate", default=0),
        excepts(StopIteration, first, lambda __: {}),
    )

    get_price_list_data = compose(partial(valmap, get_price), _get_default_item_prices)

    def add_discounts(items):
        item_codes = compose(list, partial(pluck, "name"))(items)
        max_discounts_by_item = compose(partial(key_by, "name"), frappe.db.sql)(
            """
                SELECT name, max_discount FROM `tabItem`
                WHERE item_code IN %(item_codes)s
            """,
            values={"item_codes": item_codes},
            as_dict=1,
        )
        return [merge(x, max_discounts_by_item.get(x.get("name")), {}) for x in items]

    def get_pricing_rule_item_groups(pricing_rules):
        names = compose(list, partial(pluck, "name"))(pricing_rules)
        # item_groups_by_parent = compose(partial(key_by, "parent"), frappe.db.sql)(
        #     """
        #         SELECT parent, item_group, uom 
        #         FROM `tabPricing Rule Item Group`
        #         WHERE parent IN %(names)s
        #     """,
        #     values={"names": names},
        #     as_dict=1,
        # )
        item_groups_by_parent = compose(partial(key_by, "parent"), frappe.db.sql)(
            """
                SELECT parent, item_group, uom 
                FROM `tabPricing Rule Item Group`
                WHERE parent IN %(names)s
                UNION ALL
                select `tabPricing Rule Item Code`.parent,`tabItem`.item_group,`tabPricing Rule Item Code`.uom 
                FROM `tabPricing Rule Item Code` LEFT JOIN `tabItem` ON `tabPricing Rule Item Code`.item_code=`tabItem`.item_code
                WHERE `tabPricing Rule Item Code`.parent IN %(names)s
            """,
            values={"names": names},
            as_dict=1,
        )
        return [
            merge(x, item_groups_by_parent.get(x.get("name")), {})
            for x in pricing_rules
        ]

    data = get_pos_data()
    pricing_rules = (
        get_pricing_rule_item_groups(data.get("pricing_rules"))
        if data.get("pricing_rules")
        else []
    )

    def get_tax_data(tax_data, company):
        tax_accounts = [
            x.get("name")
            for x in frappe.db.sql(
                """
                SELECT name FROM `tabAccount`
                WHERE account_type = "Tax"
                AND is_group = 0
                AND company = %(company)s
            """,
                values={"company": company},
                as_dict=1,
            )
        ]
        return valmap(
            lambda x: {k: v for k, v in x.items() if k in tax_accounts}, tax_data
        )

    return merge(
        data,
        {"price_list_data": get_price_list_data(data.get("doc").selling_price_list)},
         {"items": add_discounts(data.get("items"))},
         {"pricing_rules": pricing_rules},
        {
            "tax_data": get_tax_data(
                data.get("tax_data"), data.get("pos_profile").company
            )
        },
    )


@frappe.whitelist()
def get_more_pos_data(profile, company):
    pos_profile = frappe.get_doc("POS Profile", profile)
    if not pos_profile:
        return frappe.throw(_("POS Profile: {} is not valid.".format(profile)))
    warehouse = pos_profile.warehouse or frappe.db.get_value(
        "Company", pos_profile.company, "default_warehouse"
    )
    settings = frappe.get_single("POS Bahrain Settings")
    if not warehouse:
        return frappe.throw(
            _("No valid Warehouse found. Please select warehouse in " "POS Profile.")
        )
    return {
        "batch_no_details": get_batch_no_details(warehouse, settings.use_batch_price),
        "barcode_details": _get_barcode_details() if settings.use_barcode_uom else None,
        "item_prices": _get_item_prices(pos_profile.selling_price_list),
        "uom_details": get_uom_details(),
        "exchange_rates": get_exchange_rates(),
        "do_not_allow_zero_payment": settings.do_not_allow_zero_payment,
        "enforce_full_payment": settings.enforce_full_payment,
        "allow_returns": settings.allow_returns,
        "use_batch_price": settings.use_batch_price,
        "use_barcode_uom": settings.use_barcode_uom,
        "use_custom_item_cart": settings.use_custom_item_cart,
        "use_stock_validator": settings.use_stock_validator,
        "use_sales_employee": settings.show_sales_employee,
        "override_sync_limit": settings.override_sync_limit,
        "sales_employee_details": _get_employees()
        if settings.show_sales_employee
        else None,
        "mode_of_payment_details": _get_mop_details(),
    }


def get_batch_no_details(warehouse, include_batch_price=0):
    extra_fields = (
        "pb_price_based_on, pb_rate, pb_discount," if include_batch_price else ""
    )

    batches = frappe.db.sql(
        """
            SELECT
                name,
                item,
                expiry_date, {extra_fields}
                (
                    SELECT SUM(actual_qty)
                    FROM `tabStock Ledger Entry`
                    WHERE batch_no=b.name AND
                        item_code=b.item AND
                        warehouse=%(warehouse)s
                ) as qty
            FROM `tabBatch` AS b
            WHERE IFNULL(expiry_date, '4000-10-10') >= CURDATE()
            ORDER BY expiry_date
        """.format(
            extra_fields=extra_fields
        ),
        values={"warehouse": warehouse},
        as_dict=1,
    )
    return groupby("item", filter(lambda x: x.get("qty"), batches))


def _get_barcode_details():
    barcodes = frappe.db.sql(
        """
            SELECT barcode, parent AS item_code, pb_uom AS uom
            FROM `tabItem Barcode` WHERE pb_uom IS NOT NULL
        """,
        as_dict=1,
    )
    return {x.barcode: x for x in barcodes}


def _get_item_prices(price_list):
    prices = frappe.db.sql(
        """
            SELECT
                item_code, currency, price_list_rate,
                uom, customer, valid_from, valid_upto
            FROM `tabItem Price` WHERE price_list = %(price_list)s
        """,
        values={"price_list": price_list},
        as_dict=1,
    )
    return groupby("item_code", prices)


def _get_default_item_prices(price_list):
    prices = frappe.db.sql(
        """
            SELECT
                ip.item_code AS item_code,
                ip.price_list_rate AS price_list_rate
            FROM `tabItem Price` AS ip
            LEFT JOIN `tabItem` AS i on i.name = ip.item_code
            WHERE ip.price_list = %(price_list)s AND
                IFNULL(ip.customer, '') = '' AND
                IFNULL(ip.uom, '') IN ('', i.stock_uom) AND
                %(transaction_date)s BETWEEN
                    IFNULL(ip.valid_from, '2000-01-01') AND
                    IFNULL(ip.valid_upto, '2500-12-31')
        """,
        values={"price_list": price_list, "transaction_date": today()},
        as_dict=1,
    )
    return groupby("item_code", prices)


def _get_employees():
    return frappe.get_all(
        "Employee", filters={"status": "Active"}, fields=["name", "employee_name"]
    )


def get_uom_details():
    uoms = frappe.db.sql(
        """
            SELECT
                parent AS item_code,
                uom,
                conversion_factor
            FROM `tabUOM Conversion Detail`
        """,
        as_dict=1,
    )
    return groupby("item_code", uoms)


def _merge_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z


def get_exchange_rates():
    from erpnext.setup.utils import get_exchange_rate

    mops = frappe.db.sql(
        """
            SELECT
                name AS mode_of_payment,
                alt_currency AS currency
            FROM `tabMode of Payment`
            WHERE in_alt_currency=1
        """,
        as_dict=1,
    )
    return {
        mop.mode_of_payment: mop
        for mop in map(
            lambda x: _merge_dicts(
                x,
                {
                    "conversion_rate": get_exchange_rate(
                        x.currency, frappe.defaults.get_user_default("currency")
                    )
                },
            ),
            mops,
        )
    }


def _get_mop_details():
    return frappe.db.sql(
        """
            SELECT name, pb_bank_method FROM `tabMode of Payment`
            WHERE type = 'Bank' AND IFNULL(pb_bank_method, '') != ''
        """,
        as_dict=1,
    )


@frappe.whitelist()
def get_retail_price(item_code):
    retail_price_list = frappe.db.get_value(
        "POS Bahrain Settings", None, "retail_price_list"
    )
    if retail_price_list:
        price = frappe.db.exists(
            "Item Price", {"item_code": item_code, "price_list": retail_price_list}
        )
        if price:
            return frappe.db.get_value("Item Price", price, "price_list_rate")
    return None


@frappe.whitelist()
def get_uom_from(barcode):
    return frappe.db.get_value(
        "Item Barcode", filters={"barcode": barcode}, fieldname="pb_uom"
    )


@frappe.whitelist()
def get_custom_item_cart_fields():
    return frappe.get_all(
        "POS Bahrain Settings Cart Fields",
        fields=["item_field", "label", "fieldtype", "width"],
        order_by="idx",
    )


@frappe.whitelist()
def fetch_item_from_supplier_part_no(supplier, supplier_part_no):
    item = frappe.get_all(
        "Item Supplier",
        fields=["parent AS name"],
        filters=[
            ["supplier", "=", supplier],
            ["supplier_part_no", "=", supplier_part_no],
        ],
        limit_page_length=1,
    )
    return item[0] if item else None


@frappe.whitelist()
def query_uom(doctype, txt, searchfield, start, page_len, filters):
    if not filters.get("item_code"):
        return []
    return frappe.db.sql(
        """
            SELECT uom
            FROM `tabUOM Conversion Detail`
            WHERE uom LIKE %(txt)s {fcond}
            ORDER BY
                IF(LOCATE(%(_txt)s, uom), LOCATE(%(_txt)s, uom), 99999)
            LIMIT %(start)s, %(page_len)s
        """.format(
            fcond=get_filters_cond(
                "UOM Conversion Detail", {"parent": filters.get("item_code")}, []
            )
        ),
        values={
            "txt": "%%%s%%" % txt,
            "_txt": txt.replace("%", ""),
            "start": start,
            "page_len": page_len,
        },
    )


@frappe.whitelist()
def get_conversion_factor(item_code, uom):
    conversion_factor = frappe.db.get_value(
        "UOM Conversion Detail", {"parent": item_code, "uom": uom}, "conversion_factor"
    )
    return conversion_factor


@frappe.whitelist()
def get_item_rate(item_code,uom,batch_no=None, price_list="Standard Selling"):
    get_price = compose(
        lambda x: x[1] if x else None,
        excepts(StopIteration, first, lambda __: None),
        get_item_price,
    )

    return get_price(
        {"price_list": price_list, "uom": uom,"batch_no":batch_no, "transaction_date": today()},
        item_code
    )


@frappe.whitelist()
def get_actual_qty(item_code, warehouse, batch=None):
    has_batch_no = frappe.db.get_value("Item", item_code, "has_batch_no")
    if has_batch_no and batch:
        batch_qty = get_batch_qty(batch, warehouse, item_code) or {}
        return batch_qty.get("actual_batch_qty", 0)
    return (
        frappe.db.get_value(
            "Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty"
        )
        or 0
    )


@frappe.whitelist()
def search_serial_or_batch_or_barcode_number(search_value):
    from erpnext.selling.page.point_of_sale.point_of_sale import (
        search_serial_or_batch_or_barcode_number,
    )

    item_code = frappe.db.get_value(
        "Item", search_value, ["name as item_code"], as_dict=True
    )
    if item_code:
        return item_code

    result = search_serial_or_batch_or_barcode_number(search_value)
    if result and result.get("batch_no"):
        return merge(
            result,
            {
                "pb_expiry_date": frappe.db.get_value(
                    "Batch", result.get("batch_no"), "expiry_date"
                )
            },
        )
    return result or None


@frappe.whitelist()
def get_standard_prices(item_code):
    buying_price_list = frappe.db.get_single_value(
        "Buying Settings", "buying_price_list"
    )
    selling_price_list = frappe.db.get_single_value(
        "Selling Settings", "selling_price_list"
    )
    stock_uom = frappe.db.get_value("Item", item_code, "stock_uom")

    get_price = compose(
        lambda x: x.get("price_list_rate"),
        excepts(StopIteration, first, lambda _0: {}),
        lambda x: frappe.db.sql(
            """
                SELECT price_list_rate FROM `tabItem Price`
                WHERE
                    item_code = %(item_code)s AND
                    price_list = %(price_list)s AND
                    IFNULL(uom, '') IN ('', %(stock_uom)s) AND
                    IFNULL(customer, '') = ''
            """,
            values={"item_code": item_code, "price_list": x, "stock_uom": stock_uom},
            as_dict=1,
        ),
    )

    return {
        "selling_price": get_price(selling_price_list),
        "buying_price": get_price(buying_price_list),
    }


@frappe.whitelist()
def get_one_batch(item_code):
    batches = frappe.db.get_all("Batch", {"item": item_code})
    if len(batches) == 1:
        return batches[0].get("name")
    return None


@frappe.whitelist()
def get_item_cost_center(item_code=None, company=None, project=None, customer=None):
    cost_center = frappe.get_cached_value("Company", company, "cost_center")
    if not item_code:
        return cost_center
    item_defaults = get_item_defaults(item_code, company)
    item_group_defaults = get_item_group_defaults(item_code, company)
    args = {
        "project": project,
        "customer": customer,
        "cost_center": cost_center,
    }
    return get_default_cost_center(args, item_defaults, item_group_defaults, company)
def _get_customer_contacts():
    dynamic_links = {
        x.get("parent"): x.get("link_name")
        for x in frappe.db.sql(
            """
            SELECT parent, link_name FROM `tabDynamic Link`
            WHERE link_doctype = 'Customer'
            AND parenttype = 'Contact'
            """,
            as_dict=1,
        )
    }

    phone_contacts = {
        x.get("name"): x.get("phone", "")
        for x in frappe.db.sql(
            """
            SELECT name, phone 
            FROM `tabContact`
            """,
            as_dict=1,
        )
    }

    return {
        customer: phone_contacts.get(contact, "")
        for contact, customer in dynamic_links.items()
    }