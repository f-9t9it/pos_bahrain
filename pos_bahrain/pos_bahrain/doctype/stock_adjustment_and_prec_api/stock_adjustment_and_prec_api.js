// Copyright (c) 2022, 	9t9it and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stock Adjustment And PREC API', {
	refresh: function(frm) {
		cur_frm.disable_save();
		// cur_frm.set_value("price","");
		cur_frm.fields_dict.check.$input.on("click", function(evt){
			setTimeout(clear_fields(), 5000)
		})
	},
	item : function(frm, cdt, cdn){
		fetch_batch_entry(frm, cdt, cdn);
		// check_stock(frm, cdt, cdn);
		
	},
	prec_item : function(frm){
		get_prec_item_details(frm);
		// check_stock(frm, cdt, cdn);
		
	},
	
});
frappe.ui.form.on("PREC Details", {
	qty: function (frm, cdt, cdn) {
		get_prec_item_amount(frm, cdt, cdn);
	},
	});
function clear_fields(){
	console.log("Clear field :::::::::::::::::::::s")
}

function fetch_batch_entry(frm, cdt, cdn) {
	console.log("1")
	frappe.call({
	  "method": "pos_bahrain.api.stock_entry.search_batch_details",
	  "args": {
		"batch": frm.doc.item,
	   },
	  callback: function (r) {
		console.log(r)
		// cur_frm.clear_table("details");
		r.message.forEach(stock => {
		  var child = cur_frm.add_child("details");
		  cur_frm.set_value("item","")
		  frappe.model.set_value(child.doctype, child.name, "batch_no", stock.batch_no)
		  frappe.model.set_value(child.doctype, child.name, "item_code", stock.item_code)
		  frappe.model.set_value(child.doctype, child.name, "warehouse", stock.warehouse)
		  frappe.model.set_value(child.doctype, child.name, "qty", stock.qty)
		  frappe.model.set_value(child.doctype, child.name, "stock_uom", stock.stock_uom)
		//   frappe.model.set_value(child.doctype, child.name, "item_name", stock.item_name)
		  });
	    cur_frm.refresh_fields()
			
	  }
	  
	});
	cur_frm.fields_dict.my_field.$input.on("click", function(evt){

	})
};

function create_stock_adjustment(frm) {
	console.log("1")
	frappe.call({
	  "method": "pos_bahrain.api.stock_entry.create_stock_adjust",
	  "args": {
		// "batch": frm.doc.item,
	   },
	  callback: function (r) {
		console.log(r)
		// cur_frm.clear_table("details");
		// r.message.forEach(stock => {
		//   var child = cur_frm.add_child("details");
		//   cur_frm.set_value("item","")
		//   frappe.model.set_value(child.doctype, child.name, "batch_no", stock.batch_no)
		//   frappe.model.set_value(child.doctype, child.name, "item_code", stock.item_code)
		//   frappe.model.set_value(child.doctype, child.name, "warehouse", stock.warehouse)
		//   frappe.model.set_value(child.doctype, child.name, "qty", stock.qty)
		//   frappe.model.set_value(child.doctype, child.name, "stock_uom", stock.stock_uom)
		// //   frappe.model.set_value(child.doctype, child.name, "item_name", stock.item_name)
		//   });
	    // cur_frm.refresh_fields()
			
	  }
	  
	});
	// cur_frm.fields_dict.my_field.$input.on("click", function(evt){

	// })
};
// frappe.ui.form.on("Stock Entry Api Details", "check", function(frm, cdt, cdn) {
// 	var d = locals[cdt][cdn];
// 	// if (d.check) {
// 			   frappe.call({
// 				method:"pos_bahrain.api.stock_entry.create_stock_adjust",
// 				args: { 
// 					batch_no: d.batch_no,
// 					item_code:d.item_code,
// 					warehouse:d.warehouse,
// 					qty:d.update_qty,
// 					stock_uom:d.stock_uom,
// 				},
// 				callback: function(r) {
// 				  var pi = r.message
// 				  alert("Stock Recociliation Created",r);
// 					// frm.reload_doc();
// 				}
				
// 	});
// //   } 

// })
frappe.ui.form.on("Stock Adjustment And PREC API", "update", function(frm, cdt, cdn) {
    $.each(frm.doc.details || [], function(i, d) {
        if(d.check){
        frappe.call({
                method: "pos_bahrain.api.stock_entry.create_stock_adjust",
                args: { 
					batch_no: d.batch_no,
					item_code:d.item_code,
					warehouse:d.warehouse,
					qty:d.update_qty,
					stock_uom:d.stock_uom,
				},
                callback: function(r) {
					var pi = r.message
					alert("Stock Recociliation Created",r);
                }
            });	
        }
    
     })
      refresh_field("items");
    })


	/////////////////PREC Get Data////////

	function get_prec_item_details(frm, cdt, cdn) {
		console.log("1")
		frappe.call({
		  "method": "pos_bahrain.api.purchase_receipt.search_prec_item",
		  "args": {
			"item": frm.doc.prec_item,
			"warehouse": frm.doc.warehouse,
		   },
		  callback: function (r) {
			console.log(r)
			// cur_frm.clear_table("details");
			r.message.forEach(stock => {
			  var child = cur_frm.add_child("prec_details");
			  cur_frm.set_value("prec_item","")
			  frappe.model.set_value(child.doctype, child.name, "item_code", stock.item_code)
			  frappe.model.set_value(child.doctype, child.name, "item_name", stock.item_name)
			  frappe.model.set_value(child.doctype, child.name, "description", stock.description)
			  frappe.model.set_value(child.doctype, child.name, "warehouse", stock.warehouse)
			  frappe.model.set_value(child.doctype, child.name, "available_qty", stock.available_qty)
			  frappe.model.set_value(child.doctype, child.name, "stock_uom", stock.uom1)
			  frappe.model.set_value(child.doctype, child.name, "conversion_factor_stock_uom", stock.conversion_factor1)
			  frappe.model.set_value(child.doctype, child.name, "uom", stock.uom2)
			  frappe.model.set_value(child.doctype, child.name, "conversion_factor", stock.conversion_factor2)
			  frappe.model.set_value(child.doctype, child.name, "last_purchase_rate", stock.stock_uom_last_purchase_rate)

			  });
			cur_frm.refresh_fields()
				
		  }
		  
		});
		cur_frm.fields_dict.my_field.$input.on("click", function(evt){
	
		})
	};
	frappe.ui.form.on("Stock Adjustment And PREC API", "create_purchase_receipt", function(frm, cdt, cdn) {
		$.each(frm.doc.prec_details || [], function(i, d) {
			// if(d.check){
			frappe.call({
					method: "pos_bahrain.api.purchase_receipt.create_prec",
					args: { 
						supplier: cur_frm.doc.supplier,
						supplier_invoice_no: cur_frm.doc.supplier_invoice_no,
						supplier_invoice_date: cur_frm.doc.supplier_invoice_date,
						item_code:d.item_code,
						warehouse:cur_frm.doc.warehouse,
						qty:d.qty,
						stock_uom:d.stock_uom,
						// uom:d.uom,
						// conversion_factor_stock_uom:d.conversion_factor12,
						conversion_factor:conversion_factor_stock_uom,
						rate : d.rate
					},
					callback: function(r) {
						var pi = r.message
						alert("Purchase Receipt Generated",r);
					}
				});	
			//}
		
		 })
		  refresh_field("items");
		})
	function get_prec_item_amount(frm, cdt, cdn) {
		$.each(frm.doc.prec_details || [], function(i, d) {
			d.amount=d.qty+d.rate;
		  });
		refresh_field("prec_details");
		}
		