// Copyright (c) 2016, 	9t9it and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.provide('pos_bahrain.reports')

frappe.query_reports['VAT Return'] = 
{
    filters : pos_bahrain.reports.vat_return,
    formatter: function (value, row, column, data, default_formatter) {
        const formatted = default_formatter(value, row, column, data);
        if (data.bold) {
          return $(`<span>${formatted}</span>`)
            .css('font-weight', 'bold')
            .wrap('<p />')
            .parent()
            .html();
        }
        return formatted;
      },
}

