# from frappe import _
# from toolz import merge


# def make_column(key, label=None, type="Data", width=120, **kwargs):
#     return merge({
#         "label": _(label or key.replace("_", " ").title()),
#         "fieldname": key,
#         "fieldtype": type,
#         "width": width,
#     }, kwargs)
import frappe
from frappe import _
from frappe.utils import getdate,now, format_datetime
from dateutil import relativedelta
from toolz import merge, compose, first
import calendar
from functools import reduce

def make_column(key, label=None, type="Data", width=120, **kwargs):
    return merge({
        "label": _(label or key.replace("_", " ").title()),
        "fieldname": key,
        "fieldtype": type,
        "width": width,
    }, kwargs)


def make_period_list(start_date, end_date):
    def make_date(data):
        current_date = start_date + relativedelta.relativedelta(months=data)
        x, last_day = calendar.monthrange(current_date.year, current_date.month)
        return {
            'start_date': current_date.replace(day=1) if start_date.month != current_date.month else start_date,
            'end_date': current_date.replace(day=last_day) if end_date.month != current_date.month else end_date
        }

    def make_data(data):
        month = data.get("start_date").strftime("%b")
        year = data.get("start_date").strftime("%Y")
        return frappe._dict({
            'from_date': data.get('start_date'),
            'to_date': data.get('end_date'),
            'year_start_date': data.get('start_date'),
            'year_end_date': data.get('end_date'),
            'key': f'{month.lower()}_{year}',
            'label': f'{month} {year}'
        })

    start_date = getdate(start_date)
    end_date = getdate(end_date)
    if start_date > end_date:
        frappe.throw(_('Please set start date before the end date'))
    r = relativedelta.relativedelta(end_date.replace(day=1), start_date.replace(day=1))
    period_by_months = list(map(make_date, range(r.months + 1)))
    return list(map(make_data, period_by_months))

def with_report_generation_time(rows, keys, field=None):
    if not rows or not frappe.db.get_single_value(
        "POS Bahrain Settings", "include_report_generation_time"
    ):
        return rows
    template = reduce(lambda a, x: merge(a, {x: None}), keys, {})
    get_stamp = compose(format_datetime, now)
    return [merge(template, {field or first(keys): get_stamp()})] + rows