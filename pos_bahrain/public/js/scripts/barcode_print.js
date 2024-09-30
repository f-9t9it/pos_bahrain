frappe.provide('pos_bahrain.scripts')
import { set_uom_query } from './sales_invoice';
import scan_barcode from './extensions/scan_barcode.js';

function set_link_query(frm) {
  frm.set_query('print_dt', {
    filters: [['name', 'in', 'Purchase Receipt, Purchase Invoice, Stock Entry']],
  });
  frm.fields_dict.print_dt.df.only_select = 1;
}

function set_batch_query(frm) {
  frm.set_query('batch', 'items', function(doc, cdt, cdn) {
    const child = frappe.get_doc(cdt, cdn) || {};
    const { item_code } = child;
    const warehouse = doc.warehouse || frm.doc.set_warehouse;
    return {
      filters: { item_code, warehouse },
      query: 'erpnext.controllers.queries.get_batch_no',
    };
  });
}

function set_warehouse_query(frm) {
  const query = { filters: { is_group: 0 } };
  frm.set_query('set_warehouse', query);
  frm.set_query('warehouse', 'items', query);
}

async function set_item_price(frm, cdt, cdn) {
  const { price_list } = frm.doc;
  const { item_code, uom } = frappe.get_doc(cdt, cdn);
  if (item_code && uom) {
    const { message: rate } = await frappe.call({
      method: 'pos_bahrain.api.item.get_item_rate',
      args: { item_code, uom, price_list },
    });
    frappe.model.set_value(cdt, cdn, 'rate', rate);
  }
}

async function set_actual_qty(frm, cdt, cdn) {
  const doc = frappe.get_doc(cdt, cdn) || {};
  const { item_code, batch } = doc;
  const warehouse = doc.warehouse || frm.doc.set_warehouse;
  if (item_code && warehouse) {
    const { message: actual_qty } = await frappe.call({
      method: 'pos_bahrain.api.item.get_actual_qty',
      args: { item_code, warehouse, batch },
    });
    frappe.model.set_value(cdt, cdn, 'actual_qty', actual_qty);
  }
}

async function set_batch(frm, cdt, cdn) {
  const { item_code } = frappe.get_doc(cdt, cdn);
  if (item_code) {
    const { message: batch } = await frappe.call({
      method: 'pos_bahrain.api.item.get_one_batch',
      args: { item_code },
    });
    frappe.model.set_value(cdt, cdn, 'batch', batch);
  }
}

function load_print_docs_from_route(frm) {
  const [page, print_dt, print_dn] = frappe.get_prev_route();
  if (
    page === 'Form' &&
    ['Purchase Invoice', 'Purchase Receipt'].includes(print_dt)
  ) {
    frm.set_value({ print_dt, print_dn });
  }
}

pos_bahrain.scripts.barcode_print.barcode_print_item = {
  items_add: function(frm, cdt, cdn) {
    const row = frappe.get_doc(cdt, cdn);
    frm.script_manager.copy_from_first_row('items', row, ['warehouse']);
  },
  item_code: function(frm, cdt, cdn) {
    set_item_price(frm, cdt, cdn);
    set_actual_qty(frm, cdt, cdn);
    set_batch(frm, cdt, cdn);
  },
  uom: set_item_price,
  batch: set_actual_qty,
  warehouse: set_actual_qty,
};
pos_bahrain.scripts.barcode_print = {
  setup: function(frm) {
    set_link_query(frm);
    set_uom_query(frm);
    set_batch_query(frm);
    set_warehouse_query(frm);
  },
  refresh: function(frm) {
    frm.disable_save();
    frm.page.show_menu();
    const is_print_preview =
      frm.page.current_view_name === 'print' || frm.hidden;
    const action_label = is_print_preview ? 'Edit' : 'Print';
    frm.page.set_primary_action(action_label, async function() {
      let has_errored;
      const m = await frm.save(undefined, undefined, undefined, () => {
        has_errored = true;
      });
      if (!has_errored) {
        frm.print_doc();
      }
    });
    frm.page.set_secondary_action('Clear', async function() {
      frm.clear_table('items');
      frm.refresh_field('items');
    });
    frm.page.btn_secondary.toggle(!is_print_preview);
    load_print_docs_from_route(frm);
  },
  print_dn: async function(frm) {
    const { print_dt, print_dn } = frm.doc;
    if (print_dt && print_dn) {
      await frappe.call({
        method: 'set_items_from_reference',
        doc: frm.doc,
      });
      frm.refresh();
    }
  },
  scan_barcode,
  set_warehouse: function(frm) {
    frm.doc.items.forEach(({ doctype: cdt, name: cdn }) => {
      frappe.model.set_value(cdt, cdn, 'warehouse', frm.doc.set_warehouse);
    });
  },
};
