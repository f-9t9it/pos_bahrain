import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}
    
    columns, data = [], []
    columns = get_columns(filters)
    data = get_data(filters)
    
    return columns, data

def get_columns(filters):
    columns = [
        {
            "fieldname": "name",
            "fieldtype": "Link",
            "label": "ANALYTICAONE GROUP (Saudi, Bahrain, Qatar, Jordan, Oman, and UAE)",
            "options": "Company",
            "width": 200,
        },
    ]
    
    if filters.get("report_type") == "Yearly":
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        for i, month in enumerate(month_names, 1):
            columns.append({
                "fieldname": f"month_{i}",
                "fieldtype": "Currency",
                "label": _(month),
                "width": 120,
            })
    elif filters.get("report_type") == "Date Range":
        columns.append({
            "fieldname": "total",
            "fieldtype": "Currency",
            "label": _("Total"),
            "width": 120,
        })

    if filters.get("report_type") == "Yearly":
        columns.append({
            "fieldname": "grand_total",
            "fieldtype": "Currency",
            "label": _("Grand Total"),
            "width": 120,
        })

    return columns

def get_data(filters):
    data = []

    calculation_based_on = filters.get("calculation_based_on", "Sales Invoice")
    date_field = "s.posting_date" if calculation_based_on == "Sales Invoice" else "s.transaction_date"
    table_name = "tabSales Invoice" if calculation_based_on == "Sales Invoice" else "tabSales Order"

    query = f"""
        SELECT 
            c.name,
            c.default_currency,
            CASE 
                WHEN c.default_currency = "SAR" THEN SUM(s.total)
                ELSE SUM(s.total) / e.exchange_rate
            END AS tot,
            MONTH({date_field}) AS month,
            YEAR({date_field}) AS year
        FROM 
            `tabCompany` c
        LEFT JOIN 
            `{table_name}` s ON c.name = s.company
        LEFT JOIN (
            SELECT 
                from_currency,
                to_currency,
                exchange_rate,
                date,
                ROW_NUMBER() OVER (PARTITION BY from_currency ORDER BY date DESC) AS rn
            FROM 
                `tabCurrency Exchange`
            WHERE 
                to_currency = "SAR"
        ) e ON c.default_currency = e.from_currency AND e.rn = 1  -- Join with latest exchange rate
        WHERE 
            s.docstatus = 1
    """
    
    if filters.get("report_type") == "Date Range":
        query += f" AND {date_field} BETWEEN %(from_date)s AND %(to_date)s"

    if filters.get("report_type") == "Yearly" and filters.get("year"):
        query += f" AND YEAR({date_field}) = %(year)s"

    query += f"""
        GROUP BY 
            c.name, c.default_currency, YEAR({date_field}), MONTH({date_field})
    """

    result = frappe.db.sql(query, filters, as_dict=True)
    if not result:
        frappe.throw("Add Currency Exchange For All Currency")
    companies = {}

    if filters.get("report_type") == "Yearly":
        for row in result:
            company = row['name']
            if company not in companies:
                companies[company] = {f"month_{i}": 0 for i in range(1, 13)}
                companies[company].update({'name': company, 'default_currency': row['default_currency']})

            companies[company][f"month_{row['month']}"] = row['tot']

        for company in companies.values():
            company['grand_total'] = sum(company[f"month_{i}"] for i in range(1, 13))

        data = list(companies.values())

    elif filters.get("report_type") == "Date Range":
        companies = {}
        for row in result:
            company = row['name']
            if company not in companies:
                companies[company] = {
                    'name': company,
                    'default_currency': row['default_currency'],
                    'total': 0
                }
            companies[company]['total'] += row['tot']

        data = list(companies.values())

    return data



