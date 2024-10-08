import { load_filters_on_load } from './utils';

export default function () {
  return {
    onload: load_filters_on_load('Accounts Receivable', (filters) => [
      ...filters.slice(0, 8),
      {
        fieldname: 'cost_center',
        label: __('Cost Center'),
        fieldtype: 'Link',
        options: 'Cost Center',
      },
      ...filters.slice(8),
    ]),
    filters: [],
  };
}
