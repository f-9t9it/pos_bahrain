import { load_filters_on_load } from './utils';

export default function () {
  return {
    onload: load_filters_on_load(
      'Bank Reconciliation Statement',
      (filters) => filters
    ),
    filters: [],
  };
}
