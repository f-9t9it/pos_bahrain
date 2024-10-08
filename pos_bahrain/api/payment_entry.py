from __future__ import unicode_literals
import frappe
from frappe import _

@frappe.whitelist()
def add_pos_profile_and_branch_to_payment_entry():
    enabled = frappe.db.get_single_value('POS Bahrain Settings', 'add_pos_profile_and_branch_to_payment_entry')
    if (enabled == 1):
        user = frappe.session.user
        branch_form = frappe.db.sql(""" SELECT name, pb_cost_center FROM `tabBranch` where pb_user='%(user)s'  LIMIT 1 """%{"user":user }, as_dict=1 )
        branch_employee = frappe.db.sql(""" SELECT branch FROM `tabEmployee` where user_id='%(user)s'  LIMIT 1 """%{"user":user }, as_dict=1 )
        pos_profile = frappe.db.sql(""" SELECT parent from `tabPOS Profile User` where user='%(user)s' LIMIT 1 """%{"user":user }, as_dict=1 )

        data = {}
        if branch_form:
            data.update({
                'b_form_branch': branch_form[0].get('name', None),
                'b_form_cost_center':branch_form[0].get('pb_cost_center', None)
                })
        if branch_employee:
            data.update({'b_employee_branch': branch_employee[0].get('branch', None)})

        if pos_profile:
            data.update({'pos_profile':pos_profile[0].get('parent', None) })
        return data
    else:
        return 0
