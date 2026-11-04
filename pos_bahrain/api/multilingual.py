import frappe
from erpnext.accounts.utils import get_children as accounts_get_children

@frappe.whitelist()
def get_children(doctype, parent, company, is_root=False):
	pos_bahrain_settings = frappe.get_doc("POS Bahrain Settings")
	
	from erpnext.accounts.report.financial_statements import sort_accounts

	parent_fieldname = "parent_" + frappe.scrub(doctype)
	fields = ["name as value",  "is_group as expandable"]
	user_lang = frappe.translate.get_user_lang(frappe.session.user)
	if pos_bahrain_settings.enable_multilingual == 1 and user_lang == "ar":
		fields.append("account_name_arabic as value2")
	filters = [["docstatus", "<", 2]]

	filters.append([f'ifnull(`{parent_fieldname}`,"")', "=", "" if is_root else parent])

	if is_root:
		fields += ["root_type", "report_type", "account_currency"] if doctype == "Account" else []
		filters.append(["company", "=", company])

	else:
		fields += ["root_type", "account_currency"] if doctype == "Account" else []
		fields += [parent_fieldname + " as parent"]

	acc = frappe.get_list(doctype, fields=fields, filters=filters)

	if doctype == "Account":
		sort_accounts(acc, is_root, key="value")

	return acc

