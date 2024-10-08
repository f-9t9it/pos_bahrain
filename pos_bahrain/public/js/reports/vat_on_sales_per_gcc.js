export default function () {
  return {
    filters: [
      {
        fieldname: 'from_date',
        label: __('From Date'),
        fieldtype: 'Date',
        width: '80',
        reqd: 1,
        default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
      },
      {
        fieldname: 'to_date',
        label: __('To Date'),
        fieldtype: 'Date',
        width: '80',
        reqd: 1,
        default: frappe.datetime.get_today(),
      },
      {
        fieldtype: 'Select',
        fieldname: 'vat_type',
        label: 'VAT Type',
        reqd: 1,
        options: [
          'Standard Rated',
          'Zero Rated',
          'Exempted',
          'Imported',
          'Out of Scope',
        ],
        default: 'Standard Rated',
      },
      {
        fieldname: 'company',
        label: __('Company'),
        fieldtype: 'Link',
        options: 'Company',
        required: 1,
        default: frappe.defaults.get_user_default('Company'),
      },
    ],
  };
}
