frappe.provide("pos_bahrain.scripts")

export async function set_rate_from_batch(frm, cdt, cdn) {
  if (!frappe.boot.pos_bahrain.use_batch_price) {
    return;
  }
  const { batch_no, conversion_factor = 1 } = frappe.get_doc(cdt, cdn) || {};
  if (!batch_no) {
    return;
  }
  const {
    message: {
      pb_price_based_on: based_on,
      pb_rate: rate,
      pb_discount: discount_percentage,
    } = {},
  } = await frappe.db.get_value('Batch', batch_no, [
    'pb_price_based_on',
    'pb_rate',
    'pb_discount',
  ]);
  if (based_on === 'Based on Rate') {
    frappe.model.set_value(cdt, cdn, { rate: rate * conversion_factor });
  } else if (based_on === 'Based on Discount') {
    frappe.model.set_value(cdt, cdn, { discount_percentage });
  }
}

export async function set_uom(frm, cdt, cdn) {
  if (!frappe.boot.pos_bahrain.use_barcode_uom) {
    return;
  }
  const { barcode, stock_uom } = frappe.get_doc(cdt, cdn) || {};
  if (!barcode) {
    return;
  }
  const { message: uom } = await frappe.call({
    method: 'pos_bahrain.api.item.get_uom_from',
    args: { barcode },
  });
  frappe.model.set_value(cdt, cdn, { uom: uom || stock_uom });
}

pos_bahrain.scripts.sales_invoice = {
  set_uom_query(frm)
  {
    frm.set_query('uom', 'items', function (doc, cdt, cdn) {
      const { item_code } = frappe.get_doc(cdt, cdn) || {};
      return {
        query: 'pos_bahrain.api.item.query_uom',
        filters: { item_code },
      };
    });
  }
}
  


export function set_cost_center_query(frm) {
  frm.set_query('pb_set_cost_center', function (doc) {
    const { company } = doc;
    return { filters: { company, is_group: 0 } };
  });
}

export async function set_table_cost_centers(frm) {
  const { pb_set_cost_center, company, project, customer } = frm.doc;
  if (pb_set_cost_center) {
    frm.doc.items.forEach(({ doctype, name }) => {
      frappe.model.set_value(doctype, name, 'cost_center', pb_set_cost_center);
    });
  } else {
    frm.doc.items.forEach(async function ({ doctype, name, item_code }) {
      const { message: cost_center } = await frappe.call({
        method: 'pos_bahrain.api.item.get_item_cost_center',
        args: { item_code, company, project, customer },
      });
      frappe.model.set_value(doctype, name, 'cost_center', cost_center);
    });
  }
}

export async function set_item_cost_center(frm, cdt, cdn) {
  // wait for get_item_details triggered by 'item_code' to complete
  // and set cost center.
  // `item_name` is just an arbitrary property to watch. `item_name` is
  // considered to be unique so this will fail if otherwise.
  // clearInterval after ~3 mins
  const { pb_set_cost_center } = frm.doc;
  const { item_code, item_name } = frappe.get_doc(cdt, cdn);

  if (pb_set_cost_center) {
    if (item_code) {
      let tries = 0;
      const interval = setInterval(() => {
        const { item_name: fetched_name } = frappe.get_doc(cdt, cdn);
        if (item_name !== fetched_name || tries > 600) {
          frappe.model.set_value(cdt, cdn, 'cost_center', pb_set_cost_center);
          clearInterval(interval);
        }
        tries++;
      }, 300);
    }
  }
}

export async function set_fields(frm) {
  const [{ message: warehouse }, { message: branch }] = await Promise.all([
    frappe.call({
      method: 'pos_bahrain.api.customer.get_user_warehouse',
      args: { user: frappe.session.user },
    }),
    frappe.call({
      method: 'pos_bahrain.api.customer.get_user_branch',
    }),
  ]);
  frm.set_value('set_warehouse', warehouse);
  frm.set_value('pb_branch', branch);
}

const sales_invoice_item = {
  item_code: set_item_cost_center,
  batch_no: set_rate_from_batch,
  barcode: set_uom,
};

export default {
  sales_invoice_item,
  onload: async function (frm) {
    if (frm.is_new()) {
      await set_fields(frm);
    }
  },
  setup: function (frm) {
    set_uom_query(frm);
    set_cost_center_query(frm);
  },
  refresh: function (frm) {
    if (frm.doc.docstatus === 1 && !frm.doc.is_return) {
      if (
        frm.doc.outstanding_amount >= 0 ||
        Math.abs(flt(frm.doc.outstanding_amount)) < flt(frm.doc.grand_total)
      ) {
        frm.add_custom_button(
          __('POS Return / Credit Note'),
          function () {
            frappe.model.open_mapped_doc({
              method: 'pos_bahrain.api.sales_invoice.make_sales_return',
              frm,
            });
          },
        );
      }
    }
  },
  pb_set_cost_center: set_table_cost_centers,
};
