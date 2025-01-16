
from __future__ import unicode_literals
import frappe
from datetime import datetime, timedelta

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns(filters)
    data = get_data(filters)

    return columns, data

def get_columns(filters):
    return [
        {
            "fieldname": "account",
            "fieldtype": "Link",
            "label": "Bank Account",
            "options": "Account",
            "width":150
        },
        {
            "fieldname": "balance",
            "fieldtype": "Currency",
            "label": "Amount",
            "width":150
        },
        {
            "fieldname": " ",
            "fieldtype": " ",
            "label": " ",
            "width":150
        },
        {
            "fieldname": "date",
            "fieldtype": "Date",
            "label": "Date",
            "width":150,
        },
        {
            "fieldname": "daily_sale",
            "fieldtype": "Currency",
            "label": "Last year Daily Sales",
            "width":150,
        },
        {
            "fieldname": "daily_expenses",
            "fieldtype": "Currency",
            "label": "Last Year Daily Expenses = Direct + Indirect",
            "width":150,
        },
        {
            "fieldname": "purchase_amount",
            "fieldtype": "Currency",
            "label": "Purchase Amount",
            "width":150,
        },
        {
            "fieldname": "Custom",
            "fieldtype": "Currency",
            "label": "Custom",
            "width":150,
        },
        {
            "fieldname": "vat",
            "fieldtype": "Currency",
            "label": "Vat",
            "width":150,
        },
        {
            "fieldname": "comment",
            "fieldtype": "Data",
            "label": "Comment",
            "width":150,
        },
        {
            "fieldname": "est_cash",
            "fieldtype": "Currency",
            "label": "Estimated Cash in Hand",
            "width":150,
        },
    ]

def get_data(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    support_amount = filters.get('support_amount', 0)
    estimated_percentage = filters.get('estimated', 0)

    conditions = []
    params = {
        'from_date': from_date,
        'to_date': to_date
    }

    sql_query = """
        SELECT
            a.account,
            SUM(IFNULL(g.debit, 0)) AS debit,
            SUM(IFNULL(g.credit, 0)) AS credit,
            SUM(IFNULL(g.debit, 0) - IFNULL(g.credit, 0)) AS balance
        FROM `tabAccount List` a
        LEFT JOIN `tabGL Entry` g ON g.account = a.account
        WHERE g.posting_date >= %(from_date)s AND g.posting_date <= %(to_date)s
        GROUP BY a.account
        ORDER BY a.account
    """

    data = frappe.db.sql(sql_query, params, as_dict=True)

    total_debit = sum(d['debit'] or 0 for d in data)
    total_credit = sum(d['credit'] or 0 for d in data)
    total_balance = sum(d['balance'] or 0 for d in data) + support_amount

    support_row = {
        'account': 'Support Amount',
        'debit': support_amount,
        'credit': 0,
        'balance': support_amount
    }
    data.append(support_row)

    total_row = {
        'account': 'Total',
        'debit': total_debit,
        'credit': total_credit,
        'balance': total_balance
    }
    data.append(total_row)

    blank_row = {
        'account': "",
        'debit': "",
        'credit': "",
        'balance': ""
    }
    data.append(blank_row)

    date_list = generate_dates(from_date, to_date)
    
    monthly_totals = {}  

    for date in date_list:
        last_year_date = (datetime.strptime(date, '%Y-%m-%d') - timedelta(days=366)).strftime('%Y-%m-%d')
        
        daily_expenses = get_daily_expenses(last_year_date) or 0
        daily_sale = get_daily_sale(last_year_date) or 0

        if estimated_percentage:
            daily_sale = daily_sale + (daily_sale * estimated_percentage)
        
        est_cash = (total_balance or 0) + (daily_sale or 0) - (daily_expenses or 0)

        month_year = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m')

        if month_year not in monthly_totals:
            monthly_totals[month_year] = {
                'daily_sale': 0,
                'daily_expenses': 0,
                'est_cash': 0
            }

        monthly_totals[month_year]['daily_sale'] += daily_sale
        monthly_totals[month_year]['daily_expenses'] += daily_expenses
        monthly_totals[month_year]['est_cash'] += est_cash

        date_row = {
            'account': "",
            'debit': "",
            'credit': "",
            'balance': "",
            'date': date,
            'daily_expenses': daily_expenses,
            'daily_sale': daily_sale,
            'est_cash': est_cash
        }
        data.append(date_row)

        last_day_of_month = datetime.strptime(date, '%Y-%m-%d').replace(day=28) + timedelta(days=4)   
        last_day = (last_day_of_month - timedelta(days=last_day_of_month.day)).day   
        
        if datetime.strptime(date, '%Y-%m-%d').day == last_day:
            month_row = {
                'account': f'Month Total ({month_year})',
                'daily_sale': monthly_totals[month_year]['daily_sale'],
                'daily_expenses': monthly_totals[month_year]['daily_expenses'],
                'est_cash': monthly_totals[month_year]['est_cash']
            }
            data.append(month_row)

    final_totals_row = {
        'account': 'Final Total',
        'daily_sale': sum(month['daily_sale'] for month in monthly_totals.values()),
        'daily_expenses': sum(month['daily_expenses'] for month in monthly_totals.values()),
        'est_cash': sum(month['est_cash'] for month in monthly_totals.values())
    }
    data.append(final_totals_row)

    return data

def get_daily_sale(date):
    sql_query = """
        SELECT
            SUM(IFNULL(credit, 0)) AS daily_sale
        FROM `tabGL Entry`
        WHERE posting_date = %(date)s
          AND (account IN ('Sales - WCPW'))
    """
    params = {'date': date}
    result = frappe.db.sql(sql_query, params, as_dict=True)
    
    if result:
        return result[0].get('daily_sale', 0)
     
    return 0

def get_daily_expenses(date):
    sql_query = """
        SELECT
            SUM(IFNULL(debit, 0)) + SUM(IFNULL(credit, 0)) AS daily_expenses
        FROM `tabGL Entry`
        WHERE posting_date = %(date)s
          AND (account IN ('Direct Expenses - WCPW', 'Indirect Expenses - WCPW'))
    """
    params = {'date': date}
    result = frappe.db.sql(sql_query, params, as_dict=True)
    
    if result:
        return result[0].get('daily_expenses', 0)
    return 0

def generate_dates(from_date, to_date):
    date_list = []
    start_date = datetime.strptime(from_date, '%Y-%m-%d')
    end_date = datetime.strptime(to_date, '%Y-%m-%d')

    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)

    return date_list
