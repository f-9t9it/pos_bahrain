frappe.views.QueryReport = class QueryReportExtended extends frappe.views.QueryReport {
  async get_report_settings() {
    await super.get_report_settings();
    if (!this.report_settings.get_datatable_options) {
      this.report_settings.get_datatable_options = function(datatable_options) {
        datatable_options.layout = "fluid";
        return datatable_options;
      };
    }
  }
}

$(document).ready(function() {
  // for page-query-report
  $('#page-query-report .container.page-body')
    .removeClass('container')
    .addClass('container-fluid');
});