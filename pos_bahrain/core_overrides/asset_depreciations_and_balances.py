import frappe
from erpnext.accounts.report.asset_depreciations_and_balances import asset_depreciations_and_balances


# Check: https://github.com/frappe/erpnext/pull/22021
def _get_assets(filters):
    return frappe.db.sql("""
        SELECT 
            results.asset_category,
            sum(results.accumulated_depreciation_as_on_from_date) as accumulated_depreciation_as_on_from_date,
            sum(results.depreciation_eliminated_during_the_period) as depreciation_eliminated_during_the_period,
            sum(results.depreciation_amount_during_the_period) as depreciation_amount_during_the_period
        from (SELECT a.asset_category,
            ifnull(
                sum(case 
                    when ds.schedule_date < %(from_date)s and (ifnull(a.disposal_date, 0) = 0 or a.disposal_date >= %(from_date)s)
                    then ds.depreciation_amount 
                    else 0 end), 0) as accumulated_depreciation_as_on_from_date,
            ifnull(
                sum(case 
                    when ifnull(a.disposal_date, 0) != 0 and a.disposal_date >= %(from_date)s and a.disposal_date <= %(to_date)s and ds.schedule_date <= a.disposal_date 
                    then ds.depreciation_amount 
                    else 0 end), 0) as depreciation_eliminated_during_the_period,
            ifnull(
                sum(case
                    when ds.schedule_date >= %(from_date)s and ds.schedule_date <= %(to_date)s and (ifnull(a.disposal_date, 0) = 0 or ds.schedule_date <= a.disposal_date) 
                    then ds.depreciation_amount else 0 end), 0) as depreciation_amount_during_the_period
            from `tabAsset` a, `tabDepreciation Schedule` ds
            where a.docstatus=1 
            and a.company=%(company)s 
            and a.purchase_date <= %(to_date)s 
            and a.name = ds.parent 
            and ifnull(ds.journal_entry, '') != ''
            group by a.asset_category
            union
        SELECT a.asset_category,
            ifnull(
                sum(case
                    when ifnull(a.disposal_date, 0) != 0 and (a.disposal_date < %(from_date)s or a.disposal_date > %(to_date)s)
                    then 0 else a.opening_accumulated_depreciation end), 0) as accumulated_depreciation_as_on_from_date,
            ifnull(
                sum(case 
                    when a.disposal_date >= %(from_date)s and a.disposal_date <= %(to_date)s 
                    then a.opening_accumulated_depreciation else 0 end), 0) as depreciation_eliminated_during_the_period,
            0 as depreciation_amount_during_the_period
        from `tabAsset` a
        where a.docstatus=1 and a.company=%(company)s and a.purchase_date <= %(to_date)s
        group by a.asset_category) as results
        group by results.asset_category
    """, {
        "to_date": filters.to_date,
        "from_date": filters.from_date,
        "company": filters.company
    }, as_dict=1)


asset_depreciations_and_balances.get_assets = _get_assets
