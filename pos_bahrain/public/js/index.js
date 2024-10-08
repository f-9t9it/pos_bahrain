import * as scripts from './scripts';
import * as reports from './reports';
import * as addons from './addons';

frappe.provide('pos_bahrain');

frappe.ui.form.on('Sales Invoice', scripts.sales_invoice);
frappe.ui.form.on(
  'Sales Invoice Item',
  scripts.sales_invoice.sales_invoice_item
);

frappe.ui.form.on('Sales Order', scripts.sales_order);
frappe.ui.form.on('Sales Order Item', scripts.sales_order.sales_order_item);

frappe.ui.form.on('Delivery Note', scripts.delivery_note);

frappe.ui.form.on('Purchase Invoice', scripts.purchase_invoice);
frappe.ui.form.on(
  'Purchase Invoice Item',
  scripts.purchase_invoice.purchase_invoice_item
);

frappe.ui.form.on('Purchase Order', scripts.purchase_order);
frappe.ui.form.on(
  'Purchase Order Item',
  scripts.purchase_order.purchase_order_item
);
frappe.ui.form.on('Branch', scripts.branch);
frappe.ui.form.on('Purchase Receipt', scripts.purchase_receipt);
frappe.ui.form.on(
  'Purchase Receipt Item',
  scripts.purchase_receipt.purchase_receipt_item
);

frappe.ui.form.on('Material Request', scripts.material_request);

frappe.ui.form.on('Stock Entry', scripts.stock_entry);

frappe.ui.form.on('Item', scripts.item);

frappe.ui.form.on('Item Price', scripts.item_price);

frappe.ui.form.on(
  'Payment Entry Reference',
  scripts.payment_entry.payment_entry_reference
);

pos_bahrain = { scripts, reports, addons };
