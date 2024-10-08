import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt
from toolz import first


@frappe.whitelist()
def make_stock_entry(source_name, target_doc=None):
    def update_item(obj, target, source_parent):
        qty = (
            flt(flt(obj.stock_qty) - flt(obj.ordered_qty)) / target.conversion_factor
            if flt(obj.stock_qty) > flt(obj.ordered_qty)
            else 0
        )
        target.qty = qty
        target.transfer_qty = qty * obj.conversion_factor
        target.conversion_factor = obj.conversion_factor

        if source_parent.material_request_type == "Material Transfer":
            target.t_warehouse = obj.warehouse
        else:
            target.s_warehouse = obj.warehouse

    def set_missing_values(source, target):
        target.target_branch = _get_branch_by_warehouse(source.pb_to_warehouse)

    doclist = get_mapped_doc(
        "Material Request",
        source_name,
        {
            "Material Request": {
                "doctype": "Stock Transfer",
                "validation": {
                    "docstatus": ["=", 1],
                    "material_request_type": [
                        "in",
                        ["Material Transfer"],
                    ],
                },
            },
            "Material Request Item": {
                "doctype": "Stock Transfer Item",
                "field_map": {
                    "name": "material_request_item",
                    "parent": "material_request",
                    "uom": "stock_uom",
                },
                "postprocess": update_item,
                "condition": lambda doc: doc.ordered_qty < doc.stock_qty,
            },
        },
        target_doc,
        set_missing_values,
    )

    return doclist


def _get_branch_by_warehouse(warehouse):
    data = frappe.db.sql(
        """
        SELECT name FROM `tabBranch`
        WHERE warehouse = %s
        """,
        warehouse,
        as_dict=1
    )
    if not data:
        frappe.throw(_("No branch is associated with Warehouse {}".format(warehouse)))
    return first(data).get("name")
