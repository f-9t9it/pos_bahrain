import frappe
from toolz import first


@frappe.whitelist()
def get_workflow_user_received(reference_name):
    workflow_comments = frappe.get_all(
        "Comment",
        fields=["comment_email"],
        filters={
            "comment_type": "Workflow",
            "reference_doctype": "Stock Transfer",
            "reference_name": reference_name,
            "content": "Received",
        },
    )
    return first(workflow_comments).get("comment_email") if workflow_comments else None
