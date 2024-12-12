
import frappe

def execute(filters=None):
    if not filters:
        filters = {}
    columns, data = [], []
    columns = get_columns(filters)
    data = get_data(filters)

    if filters.get("company"):
        data.append({
            "name": None,
            "salary_currency": None,
            "tot": None,
            "total_sales": None,
            "age": None,
            "variance": None
        })
        
        supplier_data = get_supplier_data(filters)
        data.extend(supplier_data)

    if not data:
        frappe.msgprint("No data found for the specified filters. Please ensure the Target Child table is populated in Employee Master.")
    print(data)
    return columns, data


def get_columns(filters):
    columns = [
        {
            "fieldname": "name",
            "fieldtype": "Link",
            "label": "Employee",
            "options": "Employee",
            "width": 200,
        },
        {
            "fieldname": "salary_currency",
            "fieldtype": "Data",
            "label": "Currency",
            "width": 150,
        },
        {
            "fieldname": "tot",
            "fieldtype": "Currency",
            "label": "Per Year",
            "width": 150,
        },
        {
            "fieldname": "total_sales",
            "fieldtype": "Currency",
            "label": "Sales",
            "width": 150,
        },
        {
            "fieldname": "age",
            "fieldtype": "Percent",
            "label": "Age %",
            "width": 150,
        },
    ]

    if filters.get("show_variance") == 1:
        columns.append({
            "fieldname": "variance",
            "fieldtype": "Currency",
            "label": "Variance"
        })

    return columns


def get_data(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    company = filters.get('company')
    show_variance = filters.get('show_variance', 0)
    calculation_based_on = filters.get('calculation_based_on', 'Sales Order')   

    conditions = []
    params = [from_date, to_date]

    if calculation_based_on == 'Sales Order':
        sql_query = """
            SELECT 
                e.name,
                e.employee_name,
                e.salary_currency,
                ROUND(y.tot, 2) AS tot,
                ROUND((SUM(s.total) / tot * 100), 2) AS age,
                ROUND(COALESCE(SUM(s.total), 0), 2) AS total_sales,
                ROUND((tot - SUM(s.total)), 2) AS variance
            FROM 
                `tabEmployee` e
            LEFT JOIN
                (SELECT parent, SUM(currency) AS tot, country
                 FROM `tabTarget Child`
                 GROUP BY parent, country) AS y ON e.name = y.parent
            LEFT JOIN
                `tabSales Order` s ON s.employee = e.name AND y.country = s.country
            WHERE  
                s.docstatus = 1  AND s.transaction_date BETWEEN %s AND %s
        """

        if company:
            sql_query += " AND s.company = %s"
            params.append(company)

        if show_variance == 1:
            sql_query = sql_query.replace(
                "SUM(s.total) AS achivement, (SUM(s.total) / tot * 100) AS age",
                "SUM(s.total) AS achivement, (SUM(s.total) / tot * 100) AS age, (tot - SUM(s.total)) AS variance"
            )

        sql_query += " GROUP BY e.name, e.salary_currency, e.employee_name, y.tot"

    elif calculation_based_on == 'Sales Invoice': 
        sql_query = """
            SELECT 
                e.name,
                e.employee_name,
                e.salary_currency,
                ROUND(y.tot, 2) AS tot,
                s.posting_date,
                ROUND((SUM(s.total) / tot * 100), 2) AS age,
                ROUND(COALESCE(SUM(s.total), 0), 2) AS total_sales,
                ROUND((tot - SUM(s.total)), 2) AS variance
            FROM 
                `tabEmployee` e
            LEFT JOIN
                (SELECT parent, SUM(currency) AS tot, country
                 FROM `tabTarget Child`
                 GROUP BY parent, country) AS y ON e.name = y.parent
            LEFT JOIN
                `tabSales Invoice` s ON s.sales_personal = e.name AND y.country = s.country 
            WHERE  
                s.docstatus = 1   AND s.posting_date BETWEEN %s AND %s
        """

        if company:
            sql_query += " AND s.company = %s"
            params.append(company)

        if show_variance == 1:
            sql_query = sql_query.replace(
                "SUM(s.total) AS achivement, (SUM(s.total) / tot * 100) AS age",
                "SUM(s.total) AS achivement, (SUM(s.total) / tot * 100) AS age, (tot - SUM(s.total)) AS variance"
            )

        sql_query += " GROUP BY e.name, e.salary_currency, e.employee_name, y.tot"

    data = frappe.db.sql(sql_query, tuple(params), as_dict=True)

    if not data:
        frappe.msgprint("No data found for the specified filters. Please ensure the Target Child table is populated in Employee Master.")

    for row in data:
        row['tot'] = round(row['tot'], 2)
        row['total_sales'] = round(row['total_sales'], 2)
        row['age'] = round(row['age'], 2)
        if 'variance' in row:
            row['variance'] = round(row['variance'], 2)

    return data



def get_supplier_data(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    company = filters.get('company')

    params = [from_date, to_date, company]
    sql_query = """
        SELECT 
            x.name,
            x.default_currency as salary_currency,
            ROUND(y.tot, 2) AS tot,
            ROUND(SUM(p.total), 2) AS total_sales,
            ROUND((SUM(p.total) / y.tot * 100), 2) AS age,
            p.company,
            ROUND((y.tot - SUM(p.total)), 2) AS variance,
            c.country
        FROM 
            `tabSupplier` x
        INNER JOIN 
            (SELECT parent, SUM(currency) AS tot FROM `tabTarget Child` GROUP BY parent) AS y ON x.name = y.parent
        LEFT JOIN 
            `tabPurchase Order` p ON x.name = p.supplier 
        left join
            `tabCompany` c on p.company = c.name and p.country = c.country
        WHERE 
            p.docstatus = 1
            AND p.transaction_date BETWEEN %s AND %s and  p.company = %s
            
        GROUP BY 
            x.name, x.default_currency, y.tot, p.company 
    """

    supplier_data = frappe.db.sql(sql_query, tuple(params), as_dict=True)

    for row in supplier_data:
        row['tot'] = round(row['tot'], 2)
        row['total_sales'] = round(row['total_sales'], 2)
        row['age'] = round(row['age'], 2)
        if 'variance' in row:
            row['variance'] = round(row['variance'], 2)

    return supplier_data

