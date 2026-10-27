frappe.ui.form.on('Purchase Invoice Item', {
    item_code: function (frm, cdt, cdn) {
        console.log("test")
        get_total_stock_qty(frm, cdt, cdn)
    },
    pb_supplier_part_no:function (frm, cdt, cdn) {
    set_item_from_supplier_pn(frm, cdt, cdn)
    }
});

function get_total_stock_qty(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    if (d.item_code === undefined) {
        return;
    }
    frappe.call({
        method: "pos_bahrain.api.stock.get_total_stock_qty",
        args: {
            item_code: d.item_code
        },
        callback: function (r) {
            frappe.model.set_value(cdt, cdn, "total_available_qty", r.message);
        }
    })
}

frappe.ui.form.on('Purchase Invoice', {
	validate: function(frm) {
	       if(frm.doc.is_paid == 0 && frm.doc.docstatus==0){
        frm.set_value("paid_amount", 0);
        frm.set_value("base_paid_amount", 0);
	}
}
})
frappe.ui.form.on('Purchase Invoice', {
  refresh: function(frm)
  {
  cur_frm.fields_dict['items'].grid.get_field('uom').get_query = function(doc, cdt, cdn) {
      const row = frappe.get_doc(cdt, cdn);
      return {
        query: 'pos_bahrain.api.item.query_uom',
        filters: { item_code: row.item_code }
      };
    };

    
  },

  update_stock: function(frm)
  {
    if (frm.doc.update_stock == 1)
    {
      frm.set_query("batch_no", "items", function(doc, cdt, cdn) {
        let d = locals[cdt][cdn];
        return {
          query:"erpnext.controllers.queries.get_batch_no",
        "filters": {
          'item_code': d.item_code,
          'warehouse':frm.doc.set_warehouse,
          'posting_date':frm.doc.posting_date
        }
        
      }
      
      })
    

    }

    
  },
 

});


async function set_item_from_supplier_pn(frm, cdt, cdn) {
  const { supplier } = frm.doc;
  const { pb_supplier_part_no: supplier_part_no } = frappe.get_doc(cdt, cdn);
  const { message: item } = await frappe.call({
    method: 'pos_bahrain.api.item.fetch_item_from_supplier_part_no',
    args: { supplier, supplier_part_no },
  });
  frappe.model.set_value(cdt, cdn, 'item_code', item && item.name);
}