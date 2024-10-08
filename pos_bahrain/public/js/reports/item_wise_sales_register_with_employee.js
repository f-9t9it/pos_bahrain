import { load_filters_on_load } from './utils';

import { added_fields } from './sales_register_with_employee';

export default function () {
  return {
    onload: load_filters_on_load('Item-wise Sales Register', (filters) => {
      const new_filters = filters.filter(
        (filter_input) => filter_input.fieldname !== 'date_range'
      );
      return [
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
        ...new_filters,
        ...added_fields,
      ];
    }),
    filters: [],
  };
}
