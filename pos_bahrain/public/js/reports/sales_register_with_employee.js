import { load_filters_on_load } from './utils';

export const added_fields = [
  {
    fieldname: 'sales_employee',
    label: __('Sales Employee'),
    fieldtype: 'Link',
    options: 'Employee',
  },
  {
    fieldname: 'commission_rate',
    label: __('Commission Rate (%)'),
    fieldtype: 'Float',
  },
];

export default function () {
  return {
    onload: load_filters_on_load('Sales Register', (filters) => [
      ...filters,
      ...added_fields,
    ]),
    filters: [],
  };
}
