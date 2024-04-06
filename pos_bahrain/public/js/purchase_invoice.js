frappe.ui.form.on('Purchase Invoice Item', {
    item_code: function (frm, cdt, cdn) {
        console.log("test")
        get_total_stock_qty(frm, cdt, cdn)
    },
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
      if (frm.doc.update_stock == 1 && frm.doc.is_return == 1)
      {
        frm.set_query("batch_no", "items", function(doc, cdt, cdn) {
          let d = locals[cdt][cdn];
          return {
            query:"erpnext.controllers.queries.get_batch_no",
          "filters": {
            'item_code': d.item_code,
            'warehouse':d.warehouse,
            'posting_date':frm.doc.posting_date,
            'is_return_invoice': frm.doc.is_return          
          },
        }
        
        })
      
  
      }
    
  
      
    },
  
    update_stock: function(frm)
    {
      if (frm.doc.update_stock == 1 && frm.doc.is_return == 1)
      {
        frm.set_query("batch_no", "items", function(doc, cdt, cdn) {
          let d = locals[cdt][cdn];
          return {
            query:"erpnext.controllers.queries.get_batch_no",
          "filters": {
            'item_code': d.item_code,
            'warehouse':d.warehouse,
            'posting_date':frm.doc.posting_date,
            'is_return_invoice': frm.doc.is_return          
          },
          
        }
        
        })
      
  
      }
  
      
    },
   
  
  });