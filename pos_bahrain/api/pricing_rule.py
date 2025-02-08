import frappe 


from erpnext.accounts.doctype.pricing_rule.utils import get_other_conditions, set_transaction_type, filter_pricing_rules_for_qty_amount, remove_free_item, get_product_discount_rule, apply_pricing_rule_for_free_items


def _apply_pricing_rule_on_transaction(doc):

	conditions = "apply_on = 'Transaction'"

	values = {}
	conditions = get_other_conditions(conditions, values, doc)

	args = frappe._dict({
		'doctype': doc.doctype,
		'transaction_type': None,
	})
	set_transaction_type(args)
	tran_type_condition = '{} = 1'.format(args.transaction_type)

	sql = """
		SELECT
			`tabPricing Rule`.*
		FROM
			`tabPricing Rule`
		WHERE
			{conditions} and
			{tran_type_condition} and
			`tabPricing Rule`.disable = 0
	""".format(
		conditions=conditions,
		tran_type_condition=tran_type_condition,
	)

	pricing_rules = frappe.db.sql(sql, values, as_dict=1)

	if pricing_rules:
		pricing_rules = filter_pricing_rules_for_qty_amount(doc.total_qty,
			doc.total, pricing_rules)

		if not pricing_rules:
			remove_free_item(doc)

		for d in pricing_rules:
			if d.price_or_product_discount == 'Price':
				if d.apply_discount_on:
					doc.set('apply_discount_on', d.apply_discount_on)

				for field in ['additional_discount_percentage', 'discount_amount']:
					pr_field = ('discount_percentage'
						if field == 'additional_discount_percentage' else field)

					if not d.get(pr_field): continue

					if d.validate_applied_rule and doc.get(field) is not None and doc.get(field) < d.get(pr_field):
						frappe.msgprint(_("User has not applied rule on the invoice {0}")
							.format(doc.name))
					else:
						if not d.coupon_code_based:
							doc.set(field, d.get(pr_field))
						elif doc.get('coupon_code'):
							# coupon code based pricing rule
							coupon_code_pricing_rule = frappe.db.get_value('Coupon Code', doc.get('coupon_code'), 'pricing_rule')
							if coupon_code_pricing_rule == d.name:
								# if selected coupon code is linked with pricing rule
								doc.set(field, d.get(pr_field))
							else:
								# reset discount if not linked
								doc.set(field, 0)
						else:
							# if coupon code based but no coupon code selected
							doc.set(field, 0)

				doc.calculate_taxes_and_totals()
			elif d.price_or_product_discount == 'Product':
				item_details = frappe._dict({'parenttype': doc.doctype})
				get_product_discount_rule(d, item_details, doc=doc)
				apply_pricing_rule_for_free_items(doc, item_details.free_item_data)
				doc.set_missing_values()
				doc.calculate_taxes_and_totals()
