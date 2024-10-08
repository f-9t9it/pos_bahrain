import frappe
from frappe.model.mapper import get_mapped_doc
from erpnext.controllers.accounts_controller import get_advance_payment_entries,get_advance_journal_entries
from frappe.utils import flt
# from erpnext.accounts.doctype.payment_entry.payment_entry import build_gl_map

# Customer = Cost Center & Set Cost Center
# Set Cost Center = Supplier
# Date = Date & Supplier Invoice Date


@frappe.whitelist()
def make_purchase_invoice(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.due_date = source.posting_date
        target.bill_date = source.posting_date
    # target_doc.bill_no = source_name.name,
        target.run_method("set_missing_values")
        target.run_method("calculate_taxes_and_totals")

    doc = get_mapped_doc("Sales Invoice", source_name, {
        "Sales Invoice": {
            "doctype": "Purchase Invoice",
            "validation": {
                "docstatus": ["=", 1],
            },
        },
        "Sales Invoice Item": {
            "doctype": "Purchase Invoice Item",
        },
        "Payment Schedule": {
            "doctype": "Payment Schedule",
        },
    
    }, target_doc, set_missing_values)
    doc.bill_no = source_name
    doc.shipping_address = ""

    return doc


@frappe.whitelist()
def make_sales_return(source_name, target_doc=None):
    from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_sales_return
    sales_return = make_sales_return(source_name, target_doc)
    return _prepend_returned_si(sales_return)


def _prepend_returned_si(si):
    prepend_return_pos_name = frappe.db.get_single_value("POS Bahrain Settings", "prepend_return_pos_name")
    if prepend_return_pos_name and si.offline_pos_name:
        si.offline_pos_name = "RET-{}".format(si.offline_pos_name)
    return si


@frappe.whitelist()
def get_customer_account_balance(customer):
    customer_account = frappe.get_all(
        "GL Entry",
        filters={
            "party_type": "Customer",
            "party": customer,
        },
        fields=["sum(credit) - sum(debit) as balance"],
    )
    if not customer_account:
        return None
    balance = customer_account[0].get("balance")
    return balance if balance and balance > 0 else None

@frappe.whitelist()
def get_logged_employee_id():
    user = frappe.session.user
    uid = frappe.db.sql("""SELECT name FROM `tabEmployee` where user_id='%(user)s'"""%
        {"user": user},
        as_dict=0)
    return uid[0][0] if uid else 0

#Fetch Credit notes in advances in Sales Invoice
# class CustomAccountsController(AccountsController):
@frappe.whitelist()
def set_advances_ov(self):
    # import frappe
    # from erpnext.controllers.accounts_controller import set_advances
    """Returns list of advances against Account, Party, Reference"""
    res = self.get_advance_entries()
    self.set("advances", [])
    advance_allocated = 0
    print("//////////////////",res)
    for d in res:
        if d.against_order:
            allocated_amount = flt(d.amount)
        else:
            if self.get("party_account_currency") == self.company_currency:
                amount = self.get("base_rounded_total") or self.base_grand_total
            else:
                amount = self.get("rounded_total") or self.grand_total

            allocated_amount = min(amount - advance_allocated, d.amount)
        advance_allocated += flt(allocated_amount)

        advance_row = {
            "doctype": self.doctype + " Advance",
            "reference_type": d.reference_type,
            "reference_name": d.reference_name,
            "reference_row": d.reference_row,
            "remarks": d.remarks,
            "advance_amount": flt(d.amount),
            "allocated_amount": allocated_amount,
            "ref_exchange_rate": flt(d.exchange_rate),  # exchange_rate of advance entry
        }
        # advance_row = {
        #     "doctype": self.doctype + " Advance",
        #     "reference_type": "Sales Invoice",
        #     "reference_name": "SI222-13161",
        #     "reference_row": 1,
        #     "remarks": "",
        #     "advance_amount": 2.969,
        #     "allocated_amount": 2.969,
        #     "ref_exchange_rate": 1  # exchange_rate of advance entry
        # }

        self.append("advances", advance_row)

def get_advance_entries(self, include_unallocated=True):
    if self.doctype == "Sales Invoice":
        party_account = self.debit_to
        party_type = "Customer"
        party = self.customer
        amount_field = "credit_in_account_currency"
        order_field = "sales_order"
        order_doctype = "Sales Order"
    else:
        party_account = self.credit_to
        party_type = "Supplier"
        party = self.supplier
        amount_field = "debit_in_account_currency"
        order_field = "purchase_order"
        order_doctype = "Purchase Order"
    order_list = list(set(d.get(order_field) for d in self.get("items") if d.get(order_field)))
    journal_entries = get_advance_journal_entries(
        party_type, party, party_account, amount_field, order_doctype, order_list, include_unallocated
    )

    payment_entries = get_advance_payment_entries(
        party_type, party, party_account, order_doctype, order_list, include_unallocated
    )
    sales_invoices = get_si_credit_notes(party_type, party)
    # credit_note_entries = get_credit_note_entries(self,party_type, party, party_account, include_unallocated)
    res = journal_entries + payment_entries+sales_invoices
    # res = credit_note_entries
    # print(".......................",credit_note_entries)
    return res
# AccountsController.set_advances =  set_advances_ov
# def get_credit_note_entries(self,
#     party_type,
#     party,
#     party_account,
#     include_unallocated=True,
# ):
#     dr_or_cr = (
#         "credit_in_account_currency"
#     )

#     conditions = []
#     if include_unallocated:
#         conditions.append("ifnull(t1.reference_name, '')=''")

#     # if order_list:
#     # 	order_condition = ", ".join(["%s"] * len(order_list))
#     # 	conditions.append(
#     # 		" ('Sales Invoice' = '{0}' and ifnull(t1.name, '') in ({1}))".format(
#     # 			order_doctype, order_condition
#     # 		)
#     # 	)

#     reference_condition = " and (" + " or ".join(conditions) + ")" if conditions else ""

#     # nosemgrep
#     credit_note_entries = frappe.db.sql(
#         """
#         select
#             'Sales Invoice' as reference_type, t1.name as reference_name,
#             t1.remarks as remarks, -(t1.grand_total) as amount, 1 as exchange_rate
#         from
#             `tabSales Invoice` t1
#         where t1.customer = %(customer)s
#             and t1.is_return = 1 and t1.docstatus = 1
#         order by t1.posting_date""", {"customer":self.customer},

#         as_dict=1,
#     )

#     return list(credit_note_entries)
def get_si_credit_notes(party_type, party, limit=None, condition=None):
	unallocated_payment_entries = []
	limit_cond = "limit %s" % limit if limit else ""

	unallocated_payment_entries = frappe.db.sql("""
			select "Sales Invoice" as reference_type, name as reference_name, posting_date,
			remarks, abs(credit_note_balance) as amount
			from `tabSales Invoice`
			where
				customer = %s 
				and docstatus = 1 and is_return = 1 and credit_note_balance <-0.5 {condition}
			order by posting_date {0}
		""".format(limit_cond, condition=condition or ""),
		(party), as_dict=1)

	return list(unallocated_payment_entries)

#Advance Credit Note reconcile
@frappe.whitelist()
def reconcile_against_document_ov(args):  # nosemgrep
    """
    Cancel PE or JV, Update against document, split if required and resubmit
    """
    # To optimize making GL Entry for PE or JV with multiple references
    reconciled_entries = {}
    for row in args:
        if not reconciled_entries.get((row.voucher_type, row.voucher_no)):
            reconciled_entries[(row.voucher_type, row.voucher_no)] = []

        reconciled_entries[(row.voucher_type, row.voucher_no)].append(row)

    for key, entries in reconciled_entries.items():
        voucher_type = key[0]
        voucher_no = key[1]

        # cancel advance entry
        doc = frappe.get_doc(voucher_type, voucher_no)
        frappe.flags.ignore_party_validation = True
        gl_map = doc.build_gl_map()
        create_payment_ledger_entry(gl_map, cancel=1, adv_adj=1)

        for entry in entries:
            # check_if_advance_entry_modified(entry)
            validate_allocated_amount(entry)

            # update ref in advance entry
            if voucher_type == "Journal Entry":
                update_reference_in_journal_entry(entry, doc, do_not_save=True)
            else:
                update_reference_in_payment_entry(entry, doc, do_not_save=True)

        doc.save(ignore_permissions=True)
        # re-submit advance entry
        doc = frappe.get_doc(entry.voucher_type, entry.voucher_no)
        gl_map = doc.build_gl_map()
        create_payment_ledger_entry(gl_map, cancel=0, adv_adj=1)

        frappe.flags.ignore_party_validation = False

        if entry.voucher_type in ("Payment Entry", "Journal Entry"):
            if hasattr(doc, "update_expense_claim"):
                doc.update_expense_claim()

@frappe.whitelist()
def update_against_document_in_jv_ov(self):
        """
            Links invoice and advance voucher:
                1. cancel advance voucher
                2. split into multiple rows if partially adjusted, assign against voucher
                3. submit advance voucher
        """

        if self.doctype == "Sales Invoice":
            party_type = "Customer"
            party = self.customer
            party_account = self.debit_to
            dr_or_cr = "credit_in_account_currency"
        else:
            party_type = "Supplier"
            party = self.supplier
            party_account = self.credit_to
            dr_or_cr = "debit_in_account_currency"

        # lst = []
        pe_jv_lst, si_lst = [], []
        for d in self.get('advances'):
            # if flt(d.allocated_amount) > 0 and d.reference_type != "Sales Invoice":
            if flt(d.allocated_amount) > 0 :    
                args = frappe._dict({
                    'voucher_type': d.reference_type,
                    'voucher_no': d.reference_name,
                    'voucher_detail_no': d.reference_row,
                    'against_voucher_type': self.doctype,
                    'against_voucher': self.name,
                    'account': party_account,
                    'party_type': party_type,
                    'party': party,
                    'is_advance': 'Yes',
                    'dr_or_cr': dr_or_cr,
                    'unadjusted_amount': flt(d.advance_amount),
                    'allocated_amount': flt(d.allocated_amount),
                    'exchange_rate': (self.conversion_rate
                        if self.party_account_currency != self.company_currency else 1),
                    'grand_total': (self.base_grand_total
                        if self.party_account_currency == self.company_currency else self.grand_total),
                    'outstanding_amount': self.outstanding_amount
                })
                # lst.append(args)
                if d.reference_type != "Sales Invoice":
                    pe_jv_lst.append(args)
                else:
                    si_lst.append(args)
                

        # if lst:
        if pe_jv_lst:
            from erpnext.accounts.utils import reconcile_against_document
            # reconcile_against_document(lst)
            reconcile_against_document(pe_jv_lst)
        if si_lst:
            from erpnext.accounts.doctype.payment_reconciliation.payment_reconciliation import (reconcile_dr_cr_note,)
            # reconcile_dr_cr_note(si_lst, self.company)
            
        
def validate_pos_paid_amount_ov(self):
		if len(self.payments) == 0 and self.is_pos and self.grand_total== 0:
			frappe.throw(_("At least one mode of payment is required for POS invoice."))

def get_payments(doc):
    if doc.doctype == "Sales Invoice":
        sales_orders = _get_sales_orders(doc.name)
        so_payments = get_payments_against("Sales Order", sales_orders)
        si_payments = get_payments_against("Sales Invoice", [doc.name])
        self_payments = _get_si_self_payments(doc)
        return so_payments + si_payments + self_payments
    if doc.doctype == "Sales Order":
        so_payments = get_payments_against("Sales Order", [doc.name])
        sales_invoices = _get_sales_invoices(doc.name)
        si_payments = get_payments_against("Sales Invoice", sales_invoices)

        get_si_self_payment = compose(
            _get_si_self_payments, partial(frappe.get_doc, "Sales Invoice")
        )
        si_self_payments = compose(list, concat, partial(map, get_si_self_payment))(
            sales_invoices
        )
        return so_payments + si_payments + si_self_payments
    return []
    
def get_payments_against(doctype, names):
    if not names:
        return []
    return frappe.db.sql(
        """
            SELECT
                pe.name AS payment_name,
                'Payment Entry' AS payment_doctype,
                pe.posting_date AS posting_date,
                pe.mode_of_payment AS mode_of_payment,
                per.reference_doctype AS reference_doctype,
                per.reference_name AS reference_name,
                SUM(per.allocated_amount) AS paid_amount
            FROM `tabPayment Entry Reference` AS per
            LEFT JOIN `tabPayment Entry` AS pe ON
                per.parent = pe.name
            WHERE
                pe.docstatus = 1 AND
                per.reference_doctype = %(doctype)s AND
                per.reference_name IN %(names)s
            GROUP BY pe.name
        """,
        values={"doctype": doctype, "names": list(names)},
        as_dict=1,
    )