
import frappe


def on_cancel(doc, method):
    submit_rv = frappe.db.sql(
			"""select t1.name
			from `tabSales Invoice` t1,`tabSales Invoice Item` t2
			where t1.name = t2.parent and t2.delivery_note = %s and t1.docstatus = 1""",
			(doc.name),
		)
    if submit_rv:
        doc = frappe.get_doc("Sales Invoice",submit_rv[0][0] )
        doc.cancel()
        frappe.db.commit()
    