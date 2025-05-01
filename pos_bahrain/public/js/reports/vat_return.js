frappe.provide('pos_bahrain.reports');

export default pos_bahrain.reports.vat_return =  [
      {
        fieldname: 'from_date',
        label: __('From Date'),
        fieldtype: 'Date',
        width: '80',
        reqd: 1,
        default: frappe.datetime.month_start(),
      },
      {
        fieldname: 'to_date',
        label: __('To Date'),
        fieldtype: 'Date',
        width: '80',
        reqd: 1,
        default: frappe.datetime.month_end(),
      },
      {
        fieldname: 'company',
        label: __('Company'),
        fieldtype: 'Link',
        options: 'Company',
        required: 1,
        default: frappe.defaults.get_user_default('Company'),
      },
    ]
  
  
