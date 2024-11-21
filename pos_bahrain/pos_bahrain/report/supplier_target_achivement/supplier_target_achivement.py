# import frappe


# def execute(filters=None):
#     if not filters:
#         filters = {}
#     columns, data = [], []
#     columns = get_columns(filters)
#     data = get_data(filters)

#     return columns, data


# def get_columns(filters):
#     columns = [
#         {
#             "fieldname": "name",
#             "fieldtype": "Link",
#             "label": "Supplier",
#             "options": "Supplier",
#         },
#         {
#             "fieldname": "default_currency",
#             "fieldtype": "Data",
#             "label": "Currency",
#         },
#         {
#             "fieldname": "per_year",
#             "fieldtype": "Currency",
#             "label": "Per Year",
#         },
#         {
#             "fieldname": "achivement",
#             "fieldtype": "Currency",
#             "label": "Achivement",
#         },
#         {
#             "fieldname": "age",
#             "fieldtype": "Float",
#             "label": "Age",
#         },
#         {
#             "fieldname": "company",
#             "fieldtype": "Link",
#             "label": "Company",
#             "options": "Company",
#         },
#     ]

#     if filters.get("show_variance") == 1:
#         columns.append({
#             "fieldname": "variance",
#             "fieldtype": "Currency",
#             "label": "Variance"
#         })

#     return columns


# def get_data(filters):
#     from_date = filters.get('from_date')
#     to_date = filters.get('to_date')
#     company = filters.get('company')
#     supplier = filters.get('supplier')
#     show_variance = filters.get('show_variance', 0)

#     conditions = []
#     params = [from_date, to_date]

    
#     sql_query = """
#         SELECT x.name,
#                x.default_currency,
#                tot AS per_year,
#                SUM(p.total) AS achivement,
#                (SUM(p.total) / tot * 100) AS age,
#                p.company
#         FROM `tabSupplier` x
#         LEFT JOIN (SELECT parent, SUM(currency) AS tot FROM `tabTarget Child` GROUP BY parent) AS y 
#             ON x.name = y.parent
#         LEFT JOIN `tabPurchase Order` p ON x.name = p.supplier
#         WHERE p.docstatus = 1
#         AND p.transaction_date BETWEEN %s AND %s
#     """

    
#     if company:
#         if isinstance(company, list):
#             sql_query += " AND p.company IN (%s)" % ','.join(['%s'] * len(company))
#             params.extend(company)
#         else:
#             sql_query += " AND p.company = %s"
#             params.append(company)

#     if supplier:
#         sql_query += " AND p.supplier = %s"
#         params.append(supplier)

#     if conditions:
#         sql_query += " AND " + " AND ".join(conditions)

    
#     if show_variance == 1:
#         sql_query = sql_query.replace(
#             "SUM(p.total) AS achivement, (SUM(p.total) / tot * 100) AS age",
#             "SUM(p.total) AS achivement, (SUM(p.total) / tot * 100) AS age, (tot - SUM(p.total)) AS variance"
#         )

#     sql_query += " GROUP BY x.name"

#     data = frappe.db.sql(sql_query, tuple(params), as_dict=True)
#     blank_row = {
#     "name": "",
#     "default_currency": "",
#     "per_year": None,
#     "achivement": None,
#     "age": None,
#     "company": "",
#     "variance": "" if show_variance == 0 else ""
#     }

#     # Insert the blank row at the second position (index 1)
#     data.insert(1, blank_row)
#     return data
import frappe

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
            "label": "Supplier",
            "options": "Supplier",
            "width":200,
        },
        {
            "fieldname": "default_currency",
            "fieldtype": "Data",
            "label": "Currency",
            "width":150,
        },
        {
            "fieldname": "per_year",
            "fieldtype": "Currency",
            "label": "Per Year",
            "width":150,
        },
        {
            "fieldname": "achivement",
            "fieldtype": "Currency",
            "label": "Achivement",
            "width":150,
        },
        {
            "fieldname": "age",
            "fieldtype": "Percent",
            "label": "Age %",
            "width":150,
        },
    ]

    if filters.get("show_variance") == 1:
        columns.append({
            "fieldname": "variance",
            "fieldtype": "Currency",
            "label": "Variance"
        })

    return columns


def get_region_data(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    company = filters.get('company')
    supplier = filters.get('supplier')
    show_variance = filters.get('show_variance', 0)

    # Start building the SQL query
    sql_query = """
        SELECT 
            y.region,
            y.country,
            x.name,
            x.default_currency,
            y.currency,
            SUM(p.total) AS achievement,
            SUM(p.total) / SUM(y.currency) * 100 AS age
        FROM `tabSupplier` x
        LEFT JOIN `tabTarget Child` AS y ON x.name = y.parent
        
        LEFT JOIN `tabPurchase Order` p ON x.name = p.supplier and y.region = p.region
        WHERE p.docstatus = 1
        AND p.transaction_date BETWEEN %s AND %s
    """
    
    params = [from_date, to_date]
    # LEFT JOIN `tabPurchase Order` p ON x.name = p.supplier
    # Apply filters for company and supplier
    if company:
        if isinstance(company, list):
            sql_query += " AND p.company IN (%s)" % ','.join(['%s'] * len(company))
            params.extend(company)
        else:
            sql_query += " AND p.company = %s"
            params.append(company)

    if supplier:
        sql_query += " AND p.supplier = %s"
        params.append(supplier)

    # Add conditions for show_variance if enabled
    # if show_variance == 1:
    #     sql_query += """
    #         LEFT JOIN `tabTarget Child` t ON x.name = t.parent
    #     """
    
    sql_query += """
        GROUP BY 
            y.region,
            x.name,
            x.default_currency,
            y.currency,
            y.country
    """
    
    # Execute the query
    data = frappe.db.sql(sql_query, tuple(params), as_dict=True)

    if not data:
        frappe.msgprint("There is not data in Target Table")
    regions = {}
    totals = {'saudi_arabia': {'achivement': 0, 'age': 0, 'currency': 0}, 'other_regions': {}}

    # Process the data
    for row in data:
        if show_variance == 1:
            row['variance'] = row.get('variance', 0)
        region = row['region']
        country = row.get('country')

        if country == "Saudi Arabia":
            if region not in regions:
                regions[region] = {
                    'achivement': 0,
                    'age': 0,
                    'currency': row['currency'],
                    'default_currency': row['default_currency'],
                    'country': country
                }

            regions[region]['achivement'] += row['achievement']
            regions[region]['age'] += row['age']

            totals['saudi_arabia']['achivement'] += row['achievement']
            totals['saudi_arabia']['age'] += row['age']

            if show_variance == 1:
                regions[region]['variance'] = row['currency'] - row['achievement']
                totals['saudi_arabia']['variance'] = row['currency'] - row['achievement']
        else:
            totals['other_regions'].setdefault(region, {'achivement': 0, 'age': 0, 'currency': 0, 'default_currency': 0})
            totals['other_regions'][region]['achivement'] += row['achievement']
            totals['other_regions'][region]['age'] += row['age']
            totals['other_regions'][region]['currency'] += row['currency']
            totals['other_regions'][region]['default_currency'] = row['default_currency']

            if show_variance == 1:
                totals['other_regions'][region]['variance'] = row['currency'] - row['achievement']

    return {'regions': regions, 'totals': totals}



def get_data(filters):
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    company = filters.get('company')
    supplier = filters.get('supplier')
    show_variance = filters.get('show_variance', 0)

    conditions = []
    params = [from_date, to_date]

    sql_query = """
        SELECT x.name,
               x.default_currency,
               tot AS per_year,
               SUM(p.total) AS achivement,
               (SUM(p.total) / tot * 100) AS age,
               p.company,
               (tot - SUM(p.total)) AS variance
        FROM `tabSupplier` x
        LEFT JOIN (SELECT parent, SUM(currency) AS tot FROM `tabTarget Child` GROUP BY parent) AS y 
            ON x.name = y.parent
        LEFT JOIN `tabPurchase Order` p ON x.name = p.supplier 
        WHERE p.docstatus = 1
        AND p.transaction_date BETWEEN %s AND %s
    """

    if company:
        if isinstance(company, list):
            sql_query += " AND p.company IN (%s)" % ','.join(['%s'] * len(company))
            params.extend(company)
        else:
            sql_query += " AND p.company = %s"
            params.append(company)

    if supplier:
        sql_query += " AND p.supplier = %s"
        params.append(supplier)

    if show_variance == 1:
        sql_query = sql_query.replace(
            "SUM(p.total) AS achivement, (SUM(p.total) / tot * 100) AS age",
            "SUM(p.total) AS achivement, (SUM(p.total) / tot * 100) AS age, (tot - SUM(p.total)) AS variance"
        )

    sql_query += " GROUP BY x.name, x.default_currency"

    data = frappe.db.sql(sql_query, tuple(params), as_dict=True)
    # frappe.msgprint(str(data))
    if not data:
        frappe.msgprint("There is not data in Target Table")
    blank_row = {
        "name": "",
        "default_currency": "",
        "per_year": "",
        "achivement": "",
        "age": "",
        "company": "",
        "variance": "" if show_variance == 0 else ""
    }

    data.insert(1, blank_row)

    region_data = get_region_data(filters)

    saudi_region_data = {}
    other_region_data = {}

    for region, region_values in region_data['regions'].items():
        country = region_values.get('country')
        if country and country.strip().lower() == "saudi arabia".lower():
            saudi_region_data[region] = region_values
        else:
            other_region_data[region] = region_values

    for region, region_values in saudi_region_data.items():
        region_row = {
            "name": region, 
            "default_currency": region_values.get('default_currency', ''),
            "per_year": region_values.get('currency', 0), 
            "achivement": region_values['achivement'],
            "age": region_values['age'],
            "company": "",   
            "variance": region_values.get('variance', 0) if show_variance == 1 else "",
        }
        data.append(region_row)

    total_row_saudi_arabia = {
        "name": "Total (Saudi Arabia)",
        "default_currency": "",
        "per_year": "",
        "achivement": region_data['totals']['saudi_arabia']['achivement'],
        "age": region_data['totals']['saudi_arabia']['age'],
        "company": "",
        "variance": region_data['totals']['saudi_arabia'].get('variance', 0),
    }
    data.append(total_row_saudi_arabia)

    if region_data['totals']['other_regions']:
        for region, region_values in region_data['totals']['other_regions'].items():
            region_row = {
                "name": region,
                "default_currency": region_values.get('default_currency', ''),   
                "per_year": region_values.get('currency', 0),  
                "achivement": region_values['achivement'],  
                "age": region_values['age'], 
                "company": "",  
                "variance": region_values.get('variance', 0) if show_variance == 1 else "",
            }
            data.append(region_row)
    # frappe.msgprint(str(data))
    return data








