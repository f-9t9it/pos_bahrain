// Copyright (c) 2021, 	9t9it and contributors
// For license information, please see license.txt
frappe.ui.form.on('Price Check', {
	check: function (frm, cdt, cdn) {
		check_stock(frm, cdt, cdn);
	  },
});	  
frappe.ui.form.on('Price Check', {
	refresh: function(frm){
		cur_frm.disable_save();
		cur_frm.set_value("price","");
		cur_frm.fields_dict.check.$input.on("click", function(evt){
			setTimeout(clear_fields(), 5000)
		})
	},
	check : function(frm){
		check_price(frm);
		// check_stock(frm, cdt, cdn);
		
	},
	// check_stock_entry_det: function (frm, cdt, cdn) {
	// 	check_stock_entry(frm, cdt, cdn);
	//   },
});


function clear_fields(){
	console.log("Clear field ::::::::::::::::::::::s")
}
function check_price(frm){
	console.log("check called")
	frappe.call({
		method:
		  'pos_bahrain.api.price_checker.search_barcode',
		args: { 
			"barcode" : frm.doc.barcode 
		},
		callback: function(r){
			if(r.message == "Item/Price not found"){
				frappe.msgprint("Item/Price not found")
				cur_frm.set_value("barcode","")
				cur_frm.set_value("item_name","")
				cur_frm.set_value("price","")
				return
			}
			else{
				cur_frm.set_value("barcode","")
				cur_frm.set_value("item_name",r.message[0].item_name)
				cur_frm.set_value("price",r.message[0].price_list_rate)
				cur_frm.refresh_fields()

			}
			cur_frm.fields_dict.my_field.$input.on("click", function(evt){

			})
			
		}
	  });
}

function check_stock(frm, cdt, cdn) {
	  console.log("1")
	  frappe.call({
		"method": "pos_bahrain.api.price_checker.warehouse_stock",
		"args": {
		  "barcode": frm.doc.barcode,
		 },
		callback: function (r) {
		  console.log(r)
		  cur_frm.clear_table("price_check_warehouse_stock");
		  r.message.forEach(stock => {
			var child = cur_frm.add_child("price_check_warehouse_stock");
			frappe.model.set_value(child.doctype, child.name, "warehouse", stock.warehouse)
			frappe.model.set_value(child.doctype, child.name, "qty", stock.actual_qty)
			});
		//   cur_frm.refresh_fields()
			  
		}
	  });
	
};

function check_stock_entry(frm, cdt, cdn) {
	console.log("1")
	frappe.call({
	  "method": "pos_bahrain.api.stock_entry.get_stock_entry",
	  "args": {
		"batch": frm.doc.batch_number,
	   },
	  callback: function (r) {
		console.log(r)
		cur_frm.clear_table("stock_entry_api_details");
		r.message.forEach(stock => {
		  var child = cur_frm.add_child("stock_entry_api_details");
		  cur_frm.set_value("batch_number","")
		  frappe.model.set_value(child.doctype, child.name, "stock_entry_no", stock.stock_entry_no)
		  frappe.model.set_value(child.doctype, child.name, "stock_entry_type", stock.stock_entry_type)
		  frappe.model.set_value(child.doctype, child.name, "batch_no", stock.batch_no)
		  frappe.model.set_value(child.doctype, child.name, "qty", stock.qty)
		  frappe.model.set_value(child.doctype, child.name, "item_code", stock.item_code)
		  frappe.model.set_value(child.doctype, child.name, "t_warehouse", stock.t_warehouse)
		  frappe.model.set_value(child.doctype, child.name, "stock_uom", stock.stock_uom)
		  frappe.model.set_value(child.doctype, child.name, "manufacturing_date", stock.manufacturing_date)
		  frappe.model.set_value(child.doctype, child.name, "expiry_date", stock.expiry_date)
		  frappe.model.set_value(child.doctype, child.name, "item_name", stock.item_name)
		  frappe.model.set_value(child.doctype, child.name, "s_warehouse", stock.s_warehouse)
		  });
	    cur_frm.refresh_fields()
			
	  }
	  
	});
	cur_frm.fields_dict.my_field.$input.on("click", function(evt){

	})
};