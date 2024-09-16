frappe.ui.form.on('Sales Invoice Item', {
  item_code: function(frm, cdt, cdn) {
	var child = locals[cdt][cdn];
	  if (child.item_tax_template) { 
      calculateRate(frm, cdt, cdn);
	  }
  },
  qty: function(frm, cdt, cdn) {
	  var child = locals[cdt][cdn];
	  if (child.item_tax_template) { 
      calculateRate(frm, cdt, cdn);
	  }
  }
});

function calculateRate(frm, cdt, cdn) {
  var child = locals[cdt][cdn];
  if (!child.item_code) {
    frappe.msgprint("Please select an item.");
    return;
  }
  var quantity = child.qty || 1;
  frappe.call({
      method: "pos_bahrain.doc_events.sales_invoice.fetch_item_tax_template",
      args: {
          tax_type: child.item_tax_template
      },
      callback: function (r) {  
          var data = r.message;
          var tax_rate = data.tax_rate; 
          var standard_rate = child.rate
          var total_amount = standard_rate * quantity
          var total_tax = (total_amount * tax_rate) / 100; 
          var total_gross_amount = standard_rate + total_tax; 
          frappe.model.set_value(cdt, cdn, 'total_gross_amount', total_gross_amount); 
      }
  });
}

frappe.ui.form.on('Sales Invoice', {
  refresh: function (frm) {
    get_employee(frm);
    _create_custom_buttons(frm);
    // pos_bahrain.scripts.extensions.hide_sales_return('Return / Credit Note','Create');
    pos_bahrain.scripts.extensions.hide_sales_return('Payment','Create');
    pos_bahrain.scripts.extensions.hide_sales_return('Payment Request','Create');
    pos_bahrain.scripts.extensions.hide_sales_return('Invoice Discounting','Create');
    pos_bahrain.scripts.extensions.hide_sales_return('Maintenance Schedule','Create');
    pos_bahrain.scripts.extensions.hide_sales_return('Subscription','Create');
  },
  customer: function (frm) {
    _set_customer_account_balance(frm);
  },
  validate: function(frm){
    check_duplicate(frm);
    if(frm.doc.is_return == 1){
      if(frm.doc.return_against){
        set_discount(frm);
      }
    }
  }
 
});

function set_discount(frm){
  if(frm.doc.is_return == 1){
    frappe.call({
      method: "pos_bahrain.doc_events.sales_invoice.set_discount_on_return",
      args: {
        doc: frm.doc.return_against
      },
      callback: function (r) {  
        console.log(r.message)
        if (r.message != 0) {
          match_set_discount(frm, r.message)
        }
      }
    })
  }
}

function match_set_discount(frm, data){
  frm.doc.items.forEach((row)=>{
      data.items.forEach((i)=>{
        console.log(row,i)
          if (i.item_code == row.item_code){
              frappe.model.set_value("Sales Invoice Item", row.name, "discount_percentage", i.discount_percentage);
          }
      })
      frm.refresh_field("items");
  })
}

frappe.ui.form.on('Sales Invoice Item', {
  item_code: function (frm, cdt, cdn) {
    get_total_stock_qty(frm, cdt, cdn)
  },
});

// frappe.ui.form.on('Sales Invoice Item', {
//   rate: function(frm, cdt, cdn) {
//       calculateRate(frm, cdt, cdn);
//   },
//   validate: function(frm, cdt, cdn) {
//       calculateRate(frm, cdt, cdn);
//   }
// });

// function calculateRate(frm, cdt, cdn) {
//   var child = locals[cdt][cdn];
  
//   // Make frappe.call to calculate item tax
//   frappe.call({
//       method: "pos_bahrain.api.sales_invoice.calculate_item_tax",
//       args: {
//           amount: child.amount,
//           item_tax_template: child.item_tax_template
//       },
//       callback: function(response) {
//           if (response.message) {
//               var total_gross_amount = response.message;
//               alert("2")
//               frappe.model.set_value(cdt, cdn, 'total_gross_amount', total_gross_amount);
//           }
//       }
//   });
// }



function check_duplicate(frm) {
  if (frm.doc.is_pos && frm.doc.offline_pos_name && frm.doc.is_return) {
    frappe.call({
      method: "frappe.client.get_list",
      args: {
        'doctype': 'Sales Invoice',
        'filters': [['offline_pos_name', 'LIKE', split_str_og(frm.doc.offline_pos_name) + '%']],
        'fields': ['offline_pos_name'],
        'fieldname': ['offline_pos_name']
      },
      callback: function (r) {
        var biggest = 0;
        var offline_pos;
        r.message.forEach(pos_name => {
          var amended_pos = split_str(pos_name.offline_pos_name)
          if (amended_pos.amend_no > biggest) {
            biggest = amended_pos.amend_no
            offline_pos = amended_pos.amended_str
          }
        });
        frm.set_value("offline_pos_name", offline_pos);
      }
    });
  }
}

function split_str(str_) {
  var amended_str;
  var amend_no = 0;
  var split_str = str_.split("-");
  if (split_str.length == 2) {
    amend_no = 1
    amended_str = (str_ + " - 1");
  }
  if (split_str.length == 3) {
    amend_no = Number(split_str[2]) + 1;
    amended_str = split_str[0] + "-" + split_str[1] + "- " + amend_no;
  }
  return { "amended_str": amended_str, "amend_no": amend_no };
}

function split_str_og(str_) {
  var amended_str_ws;
  var amended_str;
  var split_str = str_.split("-");
  if (split_str.length == 3) {
    var amend_no = Number(split_str[2]) + 1;
    amended_str_ws = split_str[0] + "-" + split_str[1];
    amended_str = amended_str_ws.replace(/\s+$/, '')
  }
  else amended_str = str_
  return amended_str;
}

function _create_custom_buttons(frm) {
  if (frm.doc.docstatus !== 1) {
    return;
  }
  frm.add_custom_button(__("Purchase Invoice"), function () {
    _make_purchase_invoice(frm);
  }, __("Create"));
}


function _make_purchase_invoice(frm) {
  frappe.model.open_mapped_doc({
    method: "pos_bahrain.api.sales_invoice.make_purchase_invoice",
    frm,
  });
}


async function _set_customer_account_balance(frm) {
  if(frm.doc.customer != null){
    const account_balance = await _get_customer_account_balance(frm.doc.customer);
    frm.set_value("pb_available_balance", account_balance);
  } 
}


async function _get_customer_account_balance(customer) {
  const { message: data } = await frappe.call({
    method: "pos_bahrain.api.sales_invoice.get_customer_account_balance",
    args: { customer },
  })
  return data;
}

function get_employee(frm) {
  if (!frm.doc.pb_sales_employee && frm.doc.__islocal) {
    frappe.call({
      method: "pos_bahrain.api.sales_invoice.get_logged_employee_id",
      callback: function (r) {
        if (r.message != 0) {
          frm.set_value("pb_sales_employee", r.message)
        }
      }
    })
  }
}

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

frappe.ui.form.on('Sales Invoice', {
  validate: function (frm) {
    if (cur_frm.doc.is_return) {
      cur_frm.set_value("main_invoice", "");
      cur_frm.set_value("return_si_no", "");
      cur_frm.set_value("credit_note_invoice", "");
      cur_frm.set_value("main_si", "");
      cur_frm.set_value("credit_note_balance", cur_frm.doc.grand_total);
     }
  }
})
cur_frm.fields_dict.return_si_no.get_query = function(doc) {
	return {
		filters: {
			customer: doc.customer,
			company:doc.company,
			docstatus:1,
			is_return : 1
					
		}
	}
}
// frappe.ui.form.on('Sales Invoice Advance',"advances_add", function(){
//   if (cur_frm.doc.advances){
//   for (var i =0; i < cur_frm.doc.advances.length; i++){
//    if (cur_frm.doc.items[i].reference_type = "Sales Invoice") {  
//   cur_frm.doc.credit_note_invoice=cur_frm.doc.advances[i].reference_name
//   // var main_si = frappe.db.get_value("Sales Invoice",{"name":cur_frm.doc.advances[i].reference_name},"return_against")
//   // cur_frm.doc.main_si =main_si.return_against

//   }
//    }
//    }
//   })
  frappe.ui.form.on("Sales Invoice Advance", {
    advances_add: function (frm, cdt, cdn) {
        sales_invoice_advance(frm, cdt, cdn);
    },
    refresh: function (frm, cdt, cdn) {
      sales_invoice_advance(frm, cdt, cdn);
  },
    advances_remove: function (frm, cdt, cdn) {
        sales_invoice_advance(frm, cdt, cdn);
    }, 
//     validate: function (frm, cdt, cdn) {
//       sales_invoice_advance(frm, cdt, cdn);
//   },   
});
function sales_invoice_advance(frm, cdt, cdn) {
var d = locals[cdt][cdn];
var total_advance = 0;
frm.doc.advances.forEach(function(d) { total_advance += d.allocated_amount});
frm.set_value('total_advance', total_advance);
 }	
frappe.ui.form.on('Sales Invoice',"before_save", function(){
  if (cur_frm.doc.advances){
  for (var i =0; i < cur_frm.doc.advances.length; i++){
    cur_frm.doc.credit_note_invoice=""
    cur_frm.doc.main_si=""
  // var main_si = frappe.db.get_value("Sales Invoice",{"name":cur_frm.doc.advances[i].reference_name},"return_against")
  // if (cur_frm.doc.advances[i].reference_type = "Sales Invoice") {  
  if (cur_frm.doc.advances[i].allocated_amount > 0 && cur_frm.doc.advances[i].reference_type == "Sales Invoice") {    
  cur_frm.doc.credit_note_invoice=cur_frm.doc.advances[i].reference_name
  // cur_frm.doc.main_si =main_si.return_against
  // }
  }
   }
   }
  })
  frappe.ui.form.on('Sales Invoice',"before_submit", function(){
    if (cur_frm.doc.advances){
      for (var i =0; i < cur_frm.doc.advances.length; i++){
        // cur_frm.doc.credit_note_invoice=""
        // cur_frm.doc.main_si=""
      // var main_si = frappe.db.get_value("Sales Invoice",{"name":cur_frm.doc.advances[i].reference_name},"return_against")
      // if (cur_frm.doc.advances[i].reference_type = "Sales Invoice") {  
      if (cur_frm.doc.advances[i].allocated_amount > 0 && cur_frm.doc.advances[i].reference_type == "Sales Invoice") {    
      cur_frm.doc.credit_note_invoice=cur_frm.doc.advances[i].reference_name
      // cur_frm.doc.main_si =main_si.return_against
      // }
      }
       }
       }
      })
  function sales_invoice_payment(frm, cdt, cdn) {
        // var d = locals[cdt][cdn];
        // // var amount = 0;
        // if (frm.doc.is_pos && frm.doc.ignore_payments_for_return){
        // frm.doc.payments.forEach(function(d) { d.amount = 0});
        // // frm.set_value('amount', amount);
        //  }
        //  else if(frm.doc.is_pos && !frm.doc.ignore_payments_for_return){
        //   frm.doc.payments.forEach(function(d) { d.amount = frm.doc.rounded_total}); 
        //  }
        if (frm.doc.is_return==0){
        if(frm.doc.ignore_payments_for_return == 1 && frm.doc.docstatus==0 && frm.doc.paid_amount!=0){
    	    $.each(frm.doc.payments,  function(i,  d) {
                 d.amount = 0;
                 d.base_amount=0;
                 frm.doc.paid_amount=0;
                 });
            
            frm.refresh();
	    }}
      else {
        if(frm.doc.ignore_payments_for_return == 1 && frm.doc.docstatus==0 && frm.doc.paid_amount!=0){
    	    $.each(frm.doc.payments,  function(i,  d) {
                 d.amount = 0;
                 d.base_amount=0;
                 });
            
            frm.refresh();
	    }  
      }
        }	
//  frappe.ui.form.on("Sales Invoice", "ignore_payments_for_return", function(frm, doctype, name){
//     // if (frm.doc.is_return && frm.doc.ignore_payments_for_return){
//     if (frm.doc.ignore_payments_for_return){
//     cur_frm.clear_table("payments"); 
//     // frm.doc.is_pos = 1;
//     cur_frm.refresh_fields();
//     }
//     });
  frappe.ui.form.on("Sales Invoice", {
    ignore_payments_for_return: function (frm, cdt, cdn) {
      sales_invoice_payment(frm, cdt, cdn);
      },
    refresh: function (frm, cdt, cdn) {
      sales_invoice_payment(frm, cdt, cdn);
        },
   });
  // frappe.ui.form.on("Sales Invoice", "after_insert", function(frm, doctype, name){
  //     if (frm.doc.ignore_payments_for_return){
  //     cur_frm.clear_table("payments"); 
  //     // frm.doc.is_pos = 0
  //     // cur_frm.refresh_fields();
  //     }
  //     });
      frappe.ui.form.on("Sales Invoice Item", "qty", function(frm, cdt, cdn) {
        $.each(frm.doc.advances || [], function(i, d) {
            d.allocated_amount=cur_frm.doc.rounded_total-cur_frm.doc.base_write_off_amount;
        });
        refresh_field("advances");
        })
        frappe.ui.form.on("Sales Invoice Item", "rate", function(frm, cdt, cdn) {
        $.each(frm.doc.advances || [], function(i, d) {
            d.allocated_amount=cur_frm.doc.rounded_total-cur_frm.doc.base_write_off_amount;
        });
        refresh_field("advances");
        })
        // frappe.ui.form.on("Sales Invoice", "validate", function(frm, cdt, cdn) {
        // $.each(frm.doc.advances || [], function(i, d) {
        //     if(cur_frm.doc.grand_total<=d.advance_amount){
        //     d.allocated_amount=cur_frm.doc.rounded_total-cur_frm.doc.base_write_off_amount;
        //     }
        //     else{
        //        d.allocated_amount=d.advance_amount;
        //     }
        // });
        // refresh_field("advances");
        
        // })
        frappe.ui.form.on("Sales Invoice Item", {
          items_remove: function(frm, cdt, cdn) {
         if (cur_frm.doc.is_return==1) {     
           var d = locals[cdt][cdn];
           frm.set_value('outstanding_amount', 0);
             refresh_field("items");
           }
          }
           });
