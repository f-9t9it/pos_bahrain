// Copyright (c) 2020, 	9t9it and contributors
// For license information, please see license.txt

frappe.provide("pos_bahrain.scripts.backported_stock_reconciliation")

frappe.ui.form.on(
  'Backported Stock Reconciliation',
  pos_bahrain.scripts.backported_stock_reconciliation
);

frappe.ui.form.on(
  'Backported Stock Reconciliation Item',
  pos_bahrain.scripts.backported_stock_reconciliation
    .backported_stock_reconciliation_item
);

class BackportedStockReconciliation extends erpnext.stock.StockController {
  setup() {
    const me = this;

    this.setup_posting_date_time_check();

    if (
      me.frm.doc.company &&
      erpnext.is_perpetual_inventory_enabled(me.frm.doc.company)
    ) {
      this.frm.add_fetch('company', 'cost_center', 'cost_center');
    }

    this.frm.fields_dict['expense_account'].get_query = function () {
      if (erpnext.is_perpetual_inventory_enabled(me.frm.doc.company)) {
        return {
          filters: {
            company: me.frm.doc.company,
            is_group: 0,
          },
        };
      }
    };

    this.frm.fields_dict['cost_center'].get_query = function () {
      if (erpnext.is_perpetual_inventory_enabled(me.frm.doc.company)) {
        return {
          filters: {
            company: me.frm.doc.company,
            is_group: 0,
          },
        };
      }
    };
  }

  refresh() {
    if (this.frm.doc.docstatus == 1) {
      this.show_stock_ledger();
      if (erpnext.is_perpetual_inventory_enabled(this.frm.doc.company)) {
        this.show_general_ledger();
      }
    }
  }
}



cur_frm.cscript = new BackportedStockReconciliation({ frm: cur_frm });
