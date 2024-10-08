import frappe


@frappe.whitelist()
def get_tax(company, template_type, tax_template):
    rates = frappe.db.sql(
        """
            SELECT rate, account_head FROM `tab{tax_doctype}`
            WHERE
                parenttype = %(template_type)s AND
                parent = %(tax_template)s
        """.format(
            tax_doctype=_get_tax_doctype(template_type)
        ),
        values={"template_type": template_type, "tax_template": tax_template},
        as_dict=1,
    )
    if len(rates) > 1:
        frappe.throw(frappe._("Rate can only be fetched for one tax"))
    if len(rates) == 0:
        frappe.throw(frappe._("No tax found in tax template"))
    return rates[0]


def _get_tax_doctype(template_type):
    sales_tax = "Sales Taxes and Charges"
    if template_type == "{} Template".format(sales_tax):
        return sales_tax
    purchase_tax = "Purchase Taxes and Charges"
    if template_type == "{} Template".format(purchase_tax):
        return purchase_tax
    frappe.throw(frappe._("Unknown Tax template type"))
