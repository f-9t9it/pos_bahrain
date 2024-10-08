import frappe
from frappe import _
from frappe.utils.data import add_days
from frappe.utils.pdf import get_pdf


def send_email_to_manager():
    """
    Send email to the manager
    :return:
    """
    use_daily_email = frappe.db.get_single_value('POS Bahrain Settings', 'use_daily_email')

    if not use_daily_email:
        return

    manager_email = frappe.db.get_single_value('POS Bahrain Settings', 'manager_email')

    if not manager_email:
        frappe.throw(_('Manager email not set. Set it at POS Bahrain Settings.'))

    yesterday_date = add_days(frappe.utils.nowdate(), -1)

    filters = {
        'company': frappe.defaults.get_user_default("company"),
        'from_date': yesterday_date,
        'to_date': yesterday_date,
        'group_by': 'Invoice'
    }

    report = frappe.get_doc('Report', 'Gross Profit')
    columns, data = report.get_data(limit=100, filters=filters, as_dict=True)

    columns.insert(0, frappe._dict(fieldname='idx', label='', width='30px'))
    for i in range(len(data)):
        data[i]['idx'] = i + 1

    html = frappe.render_template('frappe/templates/emails/auto_email_report.html', {
        'title': 'Gross Profit',
        'description': 'Daily Gross Profit',
        'columns': columns,
        'data': data,
        'report_name': 'Gross Profit'
    })

    frappe.sendmail(
        recipients=[manager_email],
        subject='Gross Profit Daily',
        message=_('See attachments below'),
        attachments=[{
            'fname': 'gross_profit_daily.pdf',
            'fcontent': get_pdf(html, {'orientation': 'Landscape'})
        }]
    )
