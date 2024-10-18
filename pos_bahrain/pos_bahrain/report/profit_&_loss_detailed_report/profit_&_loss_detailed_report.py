
import frappe
from frappe import _
from frappe.utils import flt
from erpnext.accounts.report.financial_statements import (
    get_columns,
    get_data,
    get_filtered_list_for_consolidated_report,
    get_period_list,
)


def execute(filters=None):
    period_list = get_period_list(
        filters.from_fiscal_year,
        filters.to_fiscal_year,
        filters.period_start_date,
        filters.period_end_date,
        filters.filter_based_on,
        filters.periodicity,
        company=filters.company,
    )

    income = get_data(
        filters.company,
        "Income",
        "Credit",
        period_list,
        filters=filters,
        accumulated_values=filters.accumulated_values,
        ignore_closing_entries=True,
        ignore_accumulated_values_for_fy=True,
    )
    # frappe.throw(str(income))

    # direct_income = []
    # indirect_income = []
    # for entry in income:
    #     if 'Direct Income' in entry.get('account', '') and entry['parent_account'] != '':
    #         direct_income.append(entry)
    #     elif 'Indirect Income' in entry.get('account', '') and entry['parent_account'] != '':
    #         indirect_income.append(entry)
    direct_income = []
    indirect_income = []
    def get_children(account):
        children = []
        for entry in income:
            if 'parent_account' in entry and entry['parent_account'] == account:
                children.append(entry)
                children.extend(get_children(entry['account']))
        return children

    for entry in income:
        if 'Direct Income' in entry.get('account', '') and entry['parent_account'] :
            direct_income.append(entry)
            direct_income.extend(get_children(entry['account']))
        elif 'Indirect Income' in entry.get('account', '') and entry['parent_account'] :
            indirect_income.append(entry)
            indirect_income.extend(get_children(entry['account']))

    
	 

    expense = get_data(
        filters.company,
        "Expense",
        "Debit",
        period_list,
        filters=filters,
        accumulated_values=filters.accumulated_values,
        ignore_closing_entries=True,
        ignore_accumulated_values_for_fy=True,
    )

    # direct_expense = []
    # indirect_expense = []
    # for entry in expense:
    #     if 'Direct Expense' in entry.get('account', '') and entry['parent_account'] != '':
    #         direct_expense.append(entry)
    #     elif 'Indirect Expense' in entry.get('account', '') and entry['parent_account'] != '':
    #         indirect_expense.append(entry)
    direct_expense = []
    indirect_expense = []
    def get_children(account):
        children = []
        for entry in expense:
            if 'parent_account' in entry and entry['parent_account'] == account:
                children.append(entry)
                children.extend(get_children(entry['account']))
        return children

    for entry in expense:
        if 'Direct Expense' in entry.get('account', '') and entry['parent_account'] :
            direct_expense.append(entry)
            direct_expense.extend(get_children(entry['account']))
        elif 'Indirect Expense' in entry.get('account', '') and entry['parent_account'] :
            indirect_expense.append(entry)
            indirect_expense.extend(get_children(entry['account']))

    gross_profit = calculate_gross_profit(direct_income, direct_expense, period_list, filters.company)
    net_profit = calculate_net_profit(gross_profit, indirect_income, indirect_expense, period_list, filters.company)

    data = []
    data.extend(direct_income or [])
    data.extend(direct_expense or [])
    data.append(gross_profit)   
    data.extend(indirect_income or [])
    data.extend(indirect_expense or [])
    data.append(net_profit)  

    columns = get_columns(filters.periodicity, period_list, filters.accumulated_values, filters.company)

    currency = filters.presentation_currency or frappe.get_cached_value(
        "Company", filters.company, "default_currency"
    )
    chart = get_chart_data(filters, columns, direct_income, indirect_income, direct_expense, indirect_expense, gross_profit, net_profit, currency)

    report_summary, primitive_summary = get_report_summary(
        period_list, filters.periodicity, direct_income, indirect_income, direct_expense, indirect_expense, net_profit, currency, filters
    )

    return columns, data, None, chart, report_summary, primitive_summary


def calculate_gross_profit(direct_income, direct_expense, period_list, company, currency=None):
    gross_profit = {
        "account_name": "'" + _("Gross Profit") + "'",
        "account": "'" + _("Gross Profit") + "'",
        "warn_if_negative": True,
        "currency": currency or frappe.get_cached_value("Company", company, "default_currency"),
    }

    for period in period_list:
        key = period.key
        total_income = flt(direct_income[0].get(key, 0), 3) if direct_income else 0   
        total_expense = flt(direct_expense[0].get(key, 0), 3) if direct_expense else 0  

        gross_profit[key] = total_income - total_expense

    return gross_profit


def calculate_net_profit(gross_profit, indirect_income, indirect_expense, period_list, company, currency=None):
    net_profit = {
        "account_name": "'" + _("Net Profit") + "'",
        "account": "'" + _("Net Profit") + "'",
        "warn_if_negative": True,
        "currency": currency or frappe.get_cached_value("Company", company, "default_currency"),
    }

    for period in period_list:
        key = period.key
        total_gross_profit = flt(gross_profit.get(key, 0), 3) if gross_profit else 0
        total_indirect_income = flt(indirect_income[0].get(key, 0), 3) if indirect_income else 0   
        total_indirect_expense = flt(indirect_expense[0].get(key, 0), 3) if indirect_expense else 0   

        net_profit[key] = total_gross_profit - total_indirect_income - total_indirect_expense

    return net_profit


def get_chart_data(filters, columns, direct_income, indirect_income, direct_expense, indirect_expense, gross_profit, net_profit, currency):
    labels = [d.get("label") for d in columns[2:]]

    income_data, expense_data, gross_profit_data, net_profit_data = [], [], [], []

  
    for p in columns[2:]:
        if direct_income and len(direct_income) > 1:
            income_data.append(direct_income[0].get(p.get("fieldname"), 0))   
        else:
            income_data.append(0)

        if direct_expense and len(direct_expense) > 1:
            expense_data.append(direct_expense[0].get(p.get("fieldname"), 0))  
        else:
            expense_data.append(0)

        if gross_profit:
            gross_profit_data.append(gross_profit.get(p.get("fieldname"), 0))
        else:
            gross_profit_data.append(0)

        if net_profit:
            net_profit_data.append(net_profit.get(p.get("fieldname"), 0))
        else:
            net_profit_data.append(0)

    datasets = [
        {"name": _("Direct Income"), "values": income_data},
        {"name": _("Direct Expense"), "values": expense_data},
        {"name": _("Gross Profit"), "values": gross_profit_data},
        {"name": _("Net Profit"), "values": net_profit_data},
    ]

    chart = {
        "data": {"labels": labels, "datasets": datasets},
        "type": "bar" if not filters.accumulated_values else "line",
        "fieldtype": "Currency",
        "options": "currency",
        "currency": currency,
    }

    return chart


def get_report_summary(
    period_list, periodicity, direct_income, indirect_income, direct_expense, indirect_expense, net_profit, currency, filters, consolidated=False
):
    net_income_direct, net_income_indirect, net_expense_direct, net_expense_indirect, net_profit_value = 0.0, 0.0, 0.0, 0.0, 0.0

    if filters.get("accumulated_in_group_company"):
        period_list = get_filtered_list_for_consolidated_report(filters, period_list)

    for period in period_list:
        key = period if consolidated else period.key
        
       
        if direct_income and len(direct_income) > 1:
            net_income_direct += flt(direct_income[0].get(key, 0), 3)
        
         
        if indirect_income and len(indirect_income) > 1:
            net_income_indirect += flt(indirect_income[0].get(key, 0), 3)

      
        if direct_expense and len(direct_expense) > 1:
            net_expense_direct += flt(direct_expense[0].get(key, 0), 3)
        
         
        if indirect_expense and len(indirect_expense) > 1:
            net_expense_indirect += flt(indirect_expense[0].get(key, 0), 3)

    net_profit_value = net_income_direct + net_income_indirect - net_expense_direct - net_expense_indirect

    if len(period_list) == 1 and periodicity == "Yearly":
        profit_label = _("Profit This Year")
        income_label = _("Total Income This Year")
        expense_label = _("Total Expense This Year")
    else:
        profit_label = _("Net Profit")
        income_label = _("Total Income")
        expense_label = _("Total Expense")

    report_summary = [
        {"value": net_income_direct + net_income_indirect, "label": income_label, "datatype": "Currency", "currency": currency},
        {"type": "separator", "value": "-"},
        {"value": net_expense_direct + net_expense_indirect, "label": expense_label, "datatype": "Currency", "currency": currency},
        {"type": "separator", "value": "=", "color": "blue"},
        {
            "value": net_profit_value,
            "indicator": "Green" if net_profit_value > 0 else "Red",
            "label": profit_label,
            "datatype": "Currency",
            "currency": currency,
        },
    ]
    
    return report_summary, net_profit_value

