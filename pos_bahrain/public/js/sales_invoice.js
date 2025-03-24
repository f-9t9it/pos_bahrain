frappe.ui.form.on('Sales Invoice', {
  before_save: function(frm) { set_series(frm); },
  onload: function(frm) { set_series(frm); },
  pos_profile: function(frm) { set_series(frm); },
  is_pos: function(frm) { 
    setTimeout(() => { set_series(frm); }, 500); 
  }
});

function set_series(frm) {
  if (frm.is_new() && frm.doc.pos_profile && frm.doc.is_pos) {
    frappe.db.get_value('POS Profile', frm.doc.pos_profile, 'naming_series', (r) => {
      if (r && r.naming_series) {
        frm.set_value("naming_series", r.naming_series);
        frm.refresh_field("naming_series"); 
      }
    });
  }
}


frappe.ui.form.on('Sales Invoice', {
 onload:function (frm){
    frm.set_df_property("custom_credit_note_list", "hidden",  true)
    frm.set_df_property("return_si_no", "read_only",  false)
    frm.set_df_property("main_invoice", "read_only",  false)
    frm.set_df_property("main_invoice", "hidden",  false)
    remove_credit_button_sales_return_settings(frm)
  
  
  },
  refresh: function (frm) {
    remove_credit_button_sales_return_settings(frm)
    get_employee(frm);
    _create_custom_buttons(frm);
	var bt = ['Payment',  'Payment Request', 'Invoice Discounting', 'Maintenance Schedule', 'Subscription']
		bt.forEach(function(bt){
			frm.page.remove_inner_button(bt, 'Create')
		});
  },
  customer: function (frm) {
    _set_customer_account_balance(frm);
	get_oustanding_invoices(frm)
  },
  validate: function(frm){
    set_discount(frm)
    check_duplicate(frm);
  },
 pb_use_credit_if_available: function(frm)
  {
    if(frm.doc.pb_use_credit_if_available == 1)
    {
      frm.set_df_property("custom_credit_note_list", "hidden",  false)
     
    }
    if(frm.doc.pb_use_credit_if_available == 0)
    {
      frm.set_df_property("custom_credit_note_list", "hidden",  true)
     
    }
   
  },
 
});

frappe.ui.form.on('Credit Note List',{
invoice(frm, cdt, cdn)
{
  let credit_note= locals[cdt][cdn];
  frappe.call({
    method: "pos_bahrain.doc_events.sales_invoice.get_sales_invoices_with_outstanding",
    args: {
      customer: frm.doc.customer
    },
    callback: function (r) {
      if (r.message != [])
      {
        let invoice_amount = r.message.find(inv => inv.name === credit_note.invoice)
        console.log(invoice_amount)
        credit_note.outstanding_amount = invoice_amount.outstanding_amount * -1
        frm.refresh_fields()
      }}
    })
  
}

})




function get_oustanding_invoices(frm){
  frappe.call({
    method: "pos_bahrain.doc_events.sales_invoice.get_sales_invoices_with_outstanding",
    args: {
      customer: frm.doc.customer
    },
    callback: function (r) {
  
      if (r.message != [])
      {
        frm.fields_dict.custom_credit_note_list.grid.get_field('invoice').get_query =
      function() {
        return {
          filters: {
              name: ['in', r.message.map(invoice => invoice.name)]
          }
        
      } 
      }
      }
      
    }
  })
}

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
// frappe.ui.form.on('Sales Invoice',"before_save", function(){
//   if (cur_frm.doc.advances){
//   for (var i =0; i < cur_frm.doc.advances.length; i++){
//     cur_frm.doc.credit_note_invoice=""
//     cur_frm.doc.main_si=""
//   // var main_si = frappe.db.get_value("Sales Invoice",{"name":cur_frm.doc.advances[i].reference_name},"return_against")
//   // if (cur_frm.doc.advances[i].reference_type = "Sales Invoice") {  
//   // if (cur_frm.doc.advances[i].allocated_amount > 0 && cur_frm.doc.advances[i].reference_type == "Sales Invoice") {    
//   // cur_frm.doc.credit_note_invoice=cur_frm.doc.advances[i].reference_name
//   // // cur_frm.doc.main_si =main_si.return_against
//   // // }
//   // } -  removed credit note invoice pulling
//    }
//    }
//   })
  frappe.ui.form.on('Sales Invoice',"before_submit", function(){
    // if (cur_frm.doc.advances){
    //   for (var i =0; i < cur_frm.doc.advances.length; i++){
    //     // cur_frm.doc.credit_note_invoice=""
    //     // cur_frm.doc.main_si=""
    //   // var main_si = frappe.db.get_value("Sales Invoice",{"name":cur_frm.doc.advances[i].reference_name},"return_against")
    //   // if (cur_frm.doc.advances[i].reference_type = "Sales Invoice") {  
    //   if (cur_frm.doc.advances[i].allocated_amount > 0 && cur_frm.doc.advances[i].reference_type == "Sales Invoice") {    
    //   cur_frm.doc.credit_note_invoice=cur_frm.doc.advances[i].reference_name
    //   // cur_frm.doc.main_si =main_si.return_against
    //   // }
    //   }
    //    }
    //    } -  removed credit note invoice pulling
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


function remove_credit_button_sales_return_settings(frm){
  frappe.db.get_doc("POS Bahrain Settings").then(pos_settings => {
    if (pos_settings.hide_sales_return_except == 1 && 
      !frappe.user_roles.includes(pos_settings.hide_sales_return_role)) {
      
      setTimeout(() => {
        $('[data-label="Return%20%2F%20Credit%20Note"]').hide();
        $('[data-label="POS%20Return%20%2F%20Credit%20Note"]').hide();
                }, 200);
            }
        });

    }
