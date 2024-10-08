import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, nowdate, getdate
from frappe import _


@frappe.whitelist()
def make_sales_invoice(source_name, target_doc=None):
    si_exist = frappe.db.sql("""select parent from `tabSales Invoice Item` where pb_quotation='%(quotation)s' LIMIT 1"""%{'quotation':source_name})
    if (si_exist):
        frappe.throw("""Sales Invoice exists for this quotation : <a href= '#Form/Sales Invoice/%(si)s'>%(si)s</a>"""%{'si':si_exist[0][0]} )
    return _make_sales_invoice(source_name, target_doc)


def _make_sales_invoice(source_name, target_doc=None, ignore_permissions=False):
    customer = _make_customer(source_name, ignore_permissions)

    def set_missing_values(source, target):
        if customer:
            target.customer = customer.name
            target.customer_name = customer.customer_name
        target.ignore_pricing_rule = 1
        target.flags.ignore_permissions = ignore_permissions
        target.run_method("set_missing_values")
        target.run_method("calculate_taxes_and_totals")

        # Terms and Conditions
        target.tc_name = target.meta.get_field("tc_name").default
        if target.tc_name:
            target.terms = frappe.db.get_value(
                "Terms and Conditions", target.tc_name, "terms"
            )

    def update_item(obj, target, source_parent):
        target.cost_center = None
        target.stock_qty = flt(obj.qty) * flt(obj.conversion_factor)
        target.pb_quotation = obj.parent

    doclist = get_mapped_doc(
        "Quotation",
        source_name,
        {
            "Quotation": {
                "doctype": "Sales Invoice",
                "validation": {"docstatus": ["=", 1]},
            },
            "Quotation Item": {
                "doctype": "Sales Invoice Item",
                "postprocess": update_item,
            },
            "Sales Taxes and Charges": {
                "doctype": "Sales Taxes and Charges",
                "add_if_empty": True,
            },
            "Sales Team": {"doctype": "Sales Team", "add_if_empty": True},
        },
        target_doc,
        set_missing_values,
        ignore_permissions=ignore_permissions,
    )

    return doclist


def _make_customer(source_name, ignore_permissions=False):
    quotation = frappe.db.get_value(
        "Quotation",
        source_name,
        ["order_type", "party_name", "customer_name"],
        as_dict=1,
    )

    if quotation and quotation.get("party_name"):
        if not frappe.db.exists("Customer", quotation.get("party_name")):
            lead_name = quotation.get("party_name")
            customer_name = frappe.db.get_value(
                "Customer",
                {"lead_name": lead_name},
                ["name", "customer_name"],
                as_dict=True,
            )
            if not customer_name:
                from erpnext.crm.doctype.lead.lead import _make_customer

                customer_doclist = _make_customer(
                    lead_name, ignore_permissions=ignore_permissions
                )
                customer = frappe.get_doc(customer_doclist)
                customer.flags.ignore_permissions = ignore_permissions
                if quotation.get("party_name") == "Shopping Cart":
                    customer.customer_group = frappe.db.get_value(
                        "Shopping Cart Settings", None, "default_customer_group"
                    )

                try:
                    customer.insert()
                    return customer
                except frappe.NameError:
                    if (
                        frappe.defaults.get_global_default("cust_master_name")
                        == "Customer Name"
                    ):
                        customer.run_method("autoname")
                        customer.name += "-" + lead_name
                        customer.insert()
                        return customer
                    else:
                        raise
                except frappe.MandatoryError:
                    frappe.local.message_log = []
                    frappe.throw(
                        _("Please create Customer from Lead {0}").format(lead_name)
                    )
            else:
                return customer_name
        else:
            return frappe.get_doc("Customer", quotation.get("party_name"))

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def link_query_override(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
	return frappe.db.sql("""
			SELECT
				`tabCustomer`.name, `tabCustomer`.mobile_no, `tabCustomer`.email_id
			FROM
				`tabCustomer`
			WHERE 
				( `tabCustomer`.`name` LIKE %(txt)s OR
				`tabCustomer`.`email_id` LIKE %(txt)s OR
				`tabCustomer`.`customer_name` LIKE %(txt)s OR
				`tabCustomer`.`mobile_no` LIKE %(txt)s OR 
				`tabCustomer`.`pb_email_address` LIKE %(txt)s OR 
				`tabCustomer`.`pb_mobile_number` LIKE %(txt)s )
			ORDER BY
				`tabCustomer`.`%(key)s`
			""" % {
				"key": searchfield,
				"start": start,
				"page_len": page_len,
			"txt": "%(txt)s"
		}, {"txt": ("%%%s%%" % txt)}, as_dict=as_dict)
