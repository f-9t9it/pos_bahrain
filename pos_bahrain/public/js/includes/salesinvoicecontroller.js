const SalesInvoiceController = erpnext.accounts.SalesInvoiceController.extend({
	hide_fields : function(doc) {
		parent_fields = ['project', 'due_date', 'is_opening', 'source','from_date', 'to_date'];
	
		if(cint(doc.is_pos) == 1) {
			hide_field(parent_fields);
		} else {
			for (i in parent_fields) {
				var docfield = frappe.meta.docfield_map[doc.doctype][parent_fields[i]];
				if(!docfield.hidden) unhide_field(parent_fields[i]);
			}
		}
	}
  });
  
  $.extend(cur_frm.cscript, new SalesInvoiceController({ frm: cur_frm }));