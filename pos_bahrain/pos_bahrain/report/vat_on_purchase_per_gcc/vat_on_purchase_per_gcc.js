// Copyright (c) 2016, 	9t9it and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.provide('pos_bahrain.reports');


frappe.query_reports[
  'VAT on Purchase per GCC'
] = {filters: pos_bahrain.reports.vat_on_sales_per_gcc,}
