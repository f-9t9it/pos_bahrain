import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}
    
    columns = get_columns(filters)
    data = get_data(filters)
    
    black_row = get_black_row(filters)
    payment_data = get_payment_data(filters)
    
    data.append(black_row)
    data.extend(payment_data)
    print(data)
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
                ELSE SUM(s.total) * e.exchange_rate
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
        ) e ON c.default_currency = e.from_currency AND e.rn = 1
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
    
    companies = {}
    missing_currencies = set()

    if filters.get("report_type") == "Yearly":
        for row in result:
            company = row['name']
            tot = row['tot'] if row['tot'] is not None else 0

            if row['default_currency'] not in missing_currencies and row['default_currency'] != "SAR" and row['tot'] is None:
                missing_currencies.add(row['default_currency'])

            if company not in companies:
                companies[company] = {f"month_{i}": 0 for i in range(1, 13)}
                companies[company].update({'name': company, 'default_currency': row['default_currency']})

            companies[company][f"month_{row['month']}"] = round(tot, 2)

        for company in companies.values():
            company['grand_total'] = round(sum(company[f"month_{i}"] for i in range(1, 13)), 2)

        data = list(companies.values())

        total_row = {'name': 'Total', 'default_currency': 'SAR'}
        for month in range(1, 13):
            total_row[f"month_{month}"] = round(sum(company[f"month_{month}"] for company in companies.values()), 2)
        total_row['grand_total'] = round(sum(total_row[f"month_{month}"] for month in range(1, 13)), 2)
        data.append(total_row)

    elif filters.get("report_type") == "Date Range":
        companies = {}
        for row in result:
            company = row['name']
            tot = row['tot'] if row['tot'] is not None else 0
            
            if row['default_currency'] not in missing_currencies and row['default_currency'] != "SAR" and row['tot'] is None:
                missing_currencies.add(row['default_currency'])

            if company not in companies:
                companies[company] = {
                    'name': company,
                    'default_currency': row['default_currency'],
                    'total': 0
                }
            companies[company]['total'] += tot

        data = list(companies.values())

        total_row = {'name': 'Total', 'default_currency': 'SAR', 'total': 0}
        total_row['total'] = round(sum(company['total'] for company in companies.values()), 2)
        data.append(total_row)

    if missing_currencies:
        missing_currencies_str = ", ".join(missing_currencies)
        frappe.throw(_("Please add currency exchange for the following currencies: {0} to SAR").format(missing_currencies_str))

    if not data:
        frappe.throw("No data found for the specified filters.")
     
    return data


def get_black_row(filters):
    return {
        'name': '',
        'default_currency': '',
        'total': 0,
        'grand_total': 0
    }

def get_payment_data(filters):
    base_payment_query = """
        SELECT 
            c.name AS company,
            p.paid_to_account_currency AS currency,
            MONTH(p.posting_date) AS month,
            YEAR(p.posting_date) AS year,
            CASE 
                WHEN c.default_currency = "SAR" THEN SUM(p.paid_amount) 
                ELSE SUM(p.paid_amount) * e.exchange_rate 
            END AS tot
        FROM
            `tabCompany` c
        LEFT JOIN
            `tabPayment Entry` p ON p.company = c.name
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
        ) e ON c.default_currency = e.from_currency AND e.rn = 1
        WHERE
            p.payment_type = "Receive"
            AND p.party_type = "Customer"
            AND p.docstatus = 1
    """

    if filters.get("report_type") == "Date Range":
        if filters.get("from_date") and filters.get("to_date"):
            payment_query = base_payment_query + f" AND p.posting_date BETWEEN %(from_date)s AND %(to_date)s"
        else:
            return []

    elif filters.get("report_type") == "Yearly" and filters.get("year"):
        payment_query = base_payment_query + f" AND YEAR(p.posting_date) = %(year)s"

    payment_query += """
        GROUP BY 
            p.company,
            p.paid_to_account_currency,
            YEAR(p.posting_date),
            MONTH(p.posting_date)
    """

    payment_result = frappe.db.sql(payment_query, filters, as_dict=True)

    if not payment_result:
        frappe.log_error("No payment entries found for the given filters.", exc_type="Warning")
        return []

    missing_currencies = set()
    payment_data = {}
    monthly_totals = {}
    grand_total = 0

    for row in payment_result:
        company = row['company']
        currency = row['currency']
        month = row['month']
        total_payment = row['tot'] if row['tot'] is not None else 0

        if company not in payment_data:
            payment_data[company] = {
                'name': company,
                'default_currency': currency,
                'grand_total': 0,
                'total': 0,
            }

        payment_data[company][f"month_{month}"] = round(total_payment, 2)
        payment_data[company]['total'] += total_payment
        payment_data[company]['grand_total'] += total_payment

        if f"month_{month}" not in monthly_totals:
            monthly_totals[f"month_{month}"] = 0
        monthly_totals[f"month_{month}"] += total_payment

        grand_total += total_payment

        if currency not in missing_currencies and currency != "SAR" and total_payment is None:
            missing_currencies.add(currency)

    total_row = {
        'name': "Total",
        'default_currency': "SAR",   
        'grand_total': round(grand_total, 2),
        'total': round(grand_total, 2),
    }

    for month in monthly_totals:
        total_row[month] = round(monthly_totals[month], 2)

    payment_data["Total"] = total_row

    if missing_currencies:
        missing_currencies_str = ", ".join(missing_currencies)
        frappe.throw(_("Please add currency exchange for the following currencies : {0} to SAR").format(missing_currencies_str))

    return list(payment_data.values())


