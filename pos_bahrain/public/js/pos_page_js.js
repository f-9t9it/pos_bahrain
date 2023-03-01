erpnext.pos.PointOfSale = erpnext.pos.PointOfSale.extend({
  onload: function() {
    this._super();
    this.setinterval_to_sync_master_data(600000);
  },
  init_master_data: async function(r, freeze = true) {
    this._super(r);
    try {
      const { message: pos_data = {} } = await frappe.call({
        method: 'pos_bahrain.api.item.get_more_pos_data',
        args: {
          profile: this.pos_profile_data.name,
          company: this.doc.company,
        },
        freeze,
        freeze_message: __('Syncing Item details'),
      });

      await this.set_opening_entry();
      return pos_data;
    } catch (e) {
      frappe.msgprint({
        indicator: 'orange',
        title: __('Warning'),
        message: __(
          'Unable to load extended Item details. Usage will be restricted.'
        ),
      });
    }
  },
  setinterval_to_sync_master_data: function(delay) {
    setInterval(async () => {
      const { message } = await frappe.call({ method: 'frappe.handler.ping' });
      if (message) {
        const r = await frappe.call({
          method: 'erpnext.accounts.doctype.sales_invoice.pos.get_pos_data',
        });
        localStorage.setItem('doc', JSON.stringify(r.message.doc));
        this.init_master_data(r, false);
        this.load_data(false);
        this.make_item_list();
        this.set_missing_values();
      }
    }, delay);
  },
  set_opening_entry: async function() {
    const { message: pos_voucher } = await frappe.call({
      method: 'pos_bahrain.api.pos_voucher.get_unclosed',
      args: {
        user: frappe.session.user,
        pos_profile: this.pos_profile_data.name,
        company: this.doc.company,
      },
    });
    if (pos_voucher) {
      this.pos_voucher = pos_voucher;
    } else {
      const dialog = new frappe.ui.Dialog({
        title: __('Enter Opening Cash'),
        fields: [
          {
            fieldtype: 'Datetime',
            fieldname: 'period_from',
            label: __('Start Date Time'),
            default: frappe.datetime.now_datetime(),
          },
          {
            fieldtype: 'Currency',
            fieldname: 'opening_amount',
            label: __('Amount'),
          },
        ],
      });
      dialog.show();
      dialog.get_close_btn().hide();
      dialog.set_primary_action('Enter', async () => {
        try {
          const { message: voucher_name } = await frappe.call({
            method: 'pos_bahrain.api.pos_voucher.create_opening',
            args: {
              posting: dialog.get_value('period_from'),
              opening_amount: dialog.get_value('opening_amount'),
              company: this.doc.company,
              pos_profile: this.pos_profile_data.name,
            },
          });
          if (!voucher_name) {
            throw Exception;
          }
          this.pos_voucher = voucher_name;
        } catch (e) {
          frappe.msgprint({
            message: __('Unable to create POS Closing Voucher opening entry.'),
            title: __('Warning'),
            indicator: 'orange',
          });
        } finally {
          dialog.hide();
          dialog.$wrapper.remove();
        }
      });
    }
  },
  show_items_in_item_cart: function() {
    this._super();
    this.wrapper
      .find('.items')
      .find('.pos-bill-item > .cell:nth-child(3)')
      .each((i, el) => {
        const value = el.innerText;
        if (value !== '0') {
          el.innerText = flt(value, this.precision);
        }
      });
  },
  make_menu_list: function() {
    this._super();
    this.page.menu
      .find('a.grey-link:contains("Cashier Closing")')
      .parent()
      .hide();
    this.page.add_menu_item('POS Closing Voucher', async () => {
      if (this.connection_status) {
        if (!this.pos_voucher) {
          await this.set_opening_entry();
        }
        frappe.dom.freeze('Syncing');
        this.sync_sales_invoice();
        await frappe.after_server_call();
        frappe.set_route('Form', 'POS Closing Voucher', this.pos_voucher, {
          period_to: frappe.datetime.now_datetime(),
        });
        frappe.dom.unfreeze();
        this.pos_voucher = null;
      } else {
        frappe.msgprint({
          message: __('Please perform this when online.'),
        });
      }
    });
  },
  update_paid_amount_status: function (update_paid_amount) {
		if (this.frm.doc.offline_pos_name) {
			update_paid_amount = update_paid_amount ? false : true;
		}

		this.refresh(update_paid_amount);
	},

	refresh: function (update_paid_amount) {
		var me = this;
		this.refresh_fields(update_paid_amount);
		this.set_primary_action();
		this.apply_pricing_rule();
	},
  
  refresh_fields: function(update_paid_amount) {
    this.apply_pricing_rule();
    this.discount_amount_applied = false;
    this._calculate_taxes_and_totals();
    this.calculate_discount_amount();
    this.show_items_in_item_cart();
    this.set_taxes();
    this.calculate_outstanding_amount(update_paid_amount);
    this.set_totals();
    this.update_total_qty();
  },
  update_total_qty: function() {
    var me = this;
    var qty_total = 0;
    $.each(this.frm.doc['items'] || [], function(i, d) {
      if (d.item_code) {
        qty_total += d.qty;
      }
    });
    this.frm.doc.qty_total = qty_total;
    this.wrapper.find('.qty-total').text(this.frm.doc.qty_total);
  },
  update_serial_no: function() {
		// var me = this;

		// //Remove the sold serial no from the cache
		// $.each(this.frm.doc.items, function(index, data) {
		// 	var sn = data.serial_no.split('\n')
		// 	if(sn.length) {
		// 		var serial_no_list = me.serial_no_data[data.item_code]
		// 		if(serial_no_list) {
		// 			$.each(sn, function(i, serial_no) {
		// 				if(in_list(Object.keys(serial_no_list), serial_no)) {
		// 					delete serial_no_list[serial_no]
		// 				}
		// 			})
		// 			me.serial_no_data[data.item_code] = serial_no_list;
		// 		}
		// 	}
		// })
	},
  create_invoice: function() {
    var me = this;
    var invoice_data = {};
    function get_barcode_uri(text) {
      return JsBarcode(document.createElement('canvas'), text, {
        height: 40,
        displayValue: false,
      })._renderProperties.element.toDataURL();
    }
    this.si_docs = this.get_doc_from_localstorage();
    if (this.frm.doc.offline_pos_name) {
      this.update_invoice();
    } else {
      this.frm.doc.offline_pos_name = $.now();
      this.frm.doc.pos_name_barcode_uri = get_barcode_uri(
        this.frm.doc.offline_pos_name
      );
      this.frm.doc.posting_date = frappe.datetime.get_today();
      this.frm.doc.posting_time = frappe.datetime.now_time();
      this.frm.doc.pos_total_qty = this.frm.doc.qty_total;
	  this.frm.doc.phone = this.customer_doc.get_values().phone;
	  this.frm.doc.customer_name = this.customer_doc.get_values().full_name;
	  this.frm.doc.email_id = this.customer_doc.get_values().email_id;
	  this.frm.doc.city = this.customer_doc.get_values().city;
	  this.frm.doc.state = this.customer_doc.get_values().state;
	  this.frm.doc.address_line1 = this.customer_doc.get_values().address_line1;
	  this.frm.doc.address_line2 = this.customer_doc.get_values().address_line2;
      this.frm.doc.pos_profile = this.pos_profile_data['name'];
      this.frm.doc.pb_set_cost_center = this.pos_profile_data['write_off_cost_center'];
      invoice_data[this.frm.doc.offline_pos_name] = this.frm.doc;
      this.si_docs.push(invoice_data);
      this.update_localstorage();
      this.set_primary_action();
    }
    return invoice_data;
  },
  sync_sales_invoice: function() {
    const me = this;

    // instead of replacing instance variables
    const si_docs = this.get_submitted_invoice() || [];
    const email_queue_list = this.get_email_queue() || {};
    const customers_list = this.get_customers_details() || {};
    const pos_profile = this.pos_profile_data || {};

    if (si_docs.length || email_queue_list || customers_list) {
      frappe.call({
        method: "erpnext.accounts.doctype.sales_invoice.pos.make_invoice",
        freeze: true,
        args: {
          doc_list: si_docs,
          email_queue_list,
          customers_list,
          pos_profile
        },
        callback: function (r) {
          if (r.message) {
            me.freeze = false;
            me.customers = r.message.synced_customers_list;
            me.customer_name = r.message.customer_name;
            me.address = r.message.synced_address;
            me.contacts = r.message.synced_contacts;
            me.removed_items = r.message.invoice;
            me.removed_email = r.message.email_queue;
            me.removed_customers = r.message.customers;
            me.remove_doc_from_localstorage();
            me.remove_email_queue_from_localstorage();
            me.remove_customer_from_localstorage();
            me.prepare_customer_mapper();
            me.autocomplete_customers();
            me.render_list_customers();
          }
        }
      });
    }
  },
  refresh: function() {
    this._super();
    if (!this.pos_voucher) {
      this.set_opening_entry();
    }
  },
  remove_selected_item: function() {
    const selected_item_idx = parseInt(this.selected_cart_idx) + 1;
    this.remove_item = []
    this.remove_item.push(selected_item_idx);
    this.remove_zero_qty_items_from_cart()
    this.update_paid_amount_status(false);

    // clean ui
    this.selected_row.hide();
    this.selected_cart_idx = null;
    this.selected_row = null;
  },
  render_list_customers: function() {
    var me = this;
  
    this.removed_items = [];
    // this.list_customers.empty();
    this.si_docs = this.get_doc_from_localstorage();
    if (!this.si_docs.length) {
      this.list_customers.find('.list-customers-table').html("");
      return;
    }
  
    var html = "";
    if(this.si_docs.length) {
      this.si_docs.forEach(function (data, i) {
        for (var key in data) {
          html += frappe.render_template("pos_invoice_list", {
            sr: i + 1,
            name: key,
            customer: data[key].customer,
            customer_name: data[key].customer_name,
            mobile_no: data[key].mobile_no,
            email_id: data[key].email_id,
            phone: data[key].phone,
            paid_amount: format_currency(data[key].paid_amount, me.frm.doc.currency),
            grand_total: format_currency(data[key].grand_total, me.frm.doc.currency),
            data: me.get_doctype_status(data[key])
          });
        }
      });
    }
    this.list_customers.find('.list-customers-table').html(html);
  
    this.list_customers.on('click', '.customer-row', function () {
      me.list_customers.hide();
      me.numeric_keypad.show();
      me.list_customers_btn.toggleClass("view_customer");
      me.pos_bill.show();
      me.list_customers_btn.show();
      me.frm.doc.offline_pos_name = $(this).parents().attr('invoice-name');
      me.edit_record();
    })
  
    //actions
    $(this.wrapper).find('.list-select-all').click(function () {
      me.list_customers.find('.list-delete').prop("checked", $(this).is(":checked"))
      me.removed_items = [];
      if ($(this).is(":checked")) {
        $.each(me.si_docs, function (index, data) {
          for (key in data) {
            me.removed_items.push(key)
          }
        });
      }
  
      me.toggle_delete_button();
    });
  
    $(this.wrapper).find('.list-delete').click(function () {
      me.frm.doc.offline_pos_name = $(this).parent().parent().attr('invoice-name');
      if ($(this).is(":checked")) {
        me.removed_items.push(me.frm.doc.offline_pos_name);
      } else {
        me.removed_items.pop(me.frm.doc.offline_pos_name)
      }
  
      me.toggle_delete_button();
    });
  },
  bind_delete_event: function() {
		var me = this;

		$(this.page.wrapper).on('click', '.btn-danger', function(){
			frappe.confirm(__("Delete permanently?"), function () {
				me.delete_records();
				me.list_customers.find('.list-customers-table').html("");
				me.render_list_customers();
			})
		})
	},

	set_focus: function () {
		if (this.default_customer || this.frm.doc.customer) {
			this.set_customer_value_in_party_field();
			this.search_item.$input.focus();
		} else {
			this.party_field.$input.focus();
		}
	},

	make_customer: function () {
		var me = this;

		if(!this.party_field) {
			if(this.page.wrapper.find('.pos-bill-toolbar').length === 0) {
				$(frappe.render_template('customer_toolbar', {
					allow_delete: this.pos_profile_data["allow_delete"]
				})).insertAfter(this.page.$title_area.hide());
			}

			this.party_field = frappe.ui.form.make_control({
				df: {
					"fieldtype": "Data",
					"options": this.party,
					"label": this.party,
					"fieldname": this.party.toLowerCase(),
					"placeholder": __("Select or add new customer")
				},
				parent: this.page.wrapper.find(".party-area"),
				only_input: true,
			});

			this.party_field.make_input();
			setTimeout(this.set_focus.bind(this), 500);
			me.toggle_delete_button();
		}

		this.party_field.awesomeplete =
			new Awesomplete(this.party_field.$input.get(0), {
				minChars: 0,
				maxItems: 99,
				autoFirst: true,
				list: [],
				filter: function (item, input) {
					if (item.value.includes('is_action')) {
						return true;
					}

					input = input.toLowerCase();
					item = this.get_item(item.value);
					result = item ? item.searchtext.includes(input) : '';
					if(!result) {
						me.prepare_customer_mapper(input);
					} else {
						return result;
					}
				},
				item: function (item, input) {
					var d = this.get_item(item.value);
					var html = "<span>" + __(d.label || d.value) + "</span>";
					if(d.customer_name) {
						html += '<br><span class="text-muted ellipsis">' + __(d.customer_name) + '</span>';
					}
					if(d.phone) {
						html += '<br><span class="text-muted ellipsis">' + __(d.phone) + '</span>';
					}
					if(d.mobile_no) {
						html += '<br><span class="text-muted ellipsis">' + __(d.mobile_no) + '</span>';
					}
					if(d.cr_no) {
						html += '<br><span class="text-muted ellipsis">' + __(d.cr_no) + '</span>';
					}
					if(d.email_id) {
						html += '<br><span class="text-muted ellipsis">' + __(d.email_id) + '</span>';
					}
					return $('<li></li>')
						.data('item.autocomplete', d)
						.html('<a><p>' + html + '</p></a>')
						.get(0);
				}
			});

		this.prepare_customer_mapper()
		this.autocomplete_customers();

		this.party_field.$input
			.on('input', function (e) {
				if(me.customers_mapper.length <= 1) {
					me.prepare_customer_mapper(e.target.value);
				}
				me.party_field.awesomeplete.list = me.customers_mapper;
			})
			.on('awesomplete-select', function (e) {
				var customer = me.party_field.awesomeplete
					.get_item(e.originalEvent.text.value);
				if (!customer) return;
				// create customer link
				if (customer.action) {
					customer.action.apply(me);
					return;
				}
				me.toggle_list_customer(false);
				me.toggle_edit_button(true);
				me.update_customer_data(customer);
				me.refresh();
				me.set_focus();
				me.list_customers_btn.removeClass("view_customer");
			})
			.on('focus', function (e) {
				$(e.target).val('').trigger('input');
				me.toggle_edit_button(false);

				if(me.frm.doc.items.length) {
					me.toggle_list_customer(false)
					me.toggle_item_cart(true)
				} else {
					me.toggle_list_customer(true)
					me.toggle_item_cart(false)
				}
			})
			.on("awesomplete-selectcomplete", function (e) {
				var item = me.party_field.awesomeplete
					.get_item(e.originalEvent.text.value);
				// clear text input if item is action
				if (item.action) {
					$(this).val("");
				}
				me.make_item_list(item.customer_name);
				me.make_item_list(item.phone);
			});
	},

	prepare_customer_mapper: function(key) {
		var me = this;
		var customer_data = '';

		if (key) {
			key = key.toLowerCase().trim();
			var re = new RegExp('%', 'g');
			var reg = new RegExp(key.replace(re, '\\w*\\s*[a-zA-Z0-9]*'));

			customer_data =  $.grep(this.customers, function(data) {
				contact = me.contacts[data.name];
				if(reg.test(data.name.toLowerCase())
					|| reg.test(data.customer_name.toLowerCase())
					|| (contact && reg.test(contact["phone"]))
					|| (contact && reg.test(contact["mobile_no"]))
					|| (contact && reg.test(contact["email_id"]))
					|| (data.cr_no && reg.test(data.cr_no))
					|| (data.customer_group && reg.test(data.customer_group.toLowerCase()))){
						return data;
				}
			})
		} else {
			customer_data = this.customers;
		}

		this.customers_mapper = [];

		customer_data.forEach(function (c, index) {
			if(index < 30) {
				contact = me.contacts[c.name];
				if(contact && !c['phone']) {
					c["phone"] = contact["phone"];
					c["email_id"] = contact["email_id"];
					c["mobile_no"] = contact["mobile_no"];
				}

				me.customers_mapper.push({
					label: c.name,
					value: c.name,
					customer_name: c.customer_name,
					mobile_no: c.mobile_no,
					customer_group: c.customer_group,
					territory: c.territory,
					cr_no:c.cr_no,
					phone: contact ? contact["phone"] : '',
					mobile_no: contact ? contact["mobile_no"] : '',
					email_id: contact ? contact["email_id"] : '',
					searchtext: ['customer_name', 'customer_group', 'name', 'value','cr_no',
						'label', 'email_id', 'phone', 'mobile_no']
						.map(key => c[key]).join(' ')
						.toLowerCase()
				});
			} else {
				return;
			}
		});

		this.customers_mapper.push({
			label: "<span class='text-primary link-option'>"
			+ "<i class='fa fa-plus' style='margin-right: 5px;'></i> "
			+ __("Create a new Customer")
			+ "</span>",
			value: 'is_action',
			action: me.add_customer
		});
	},

	autocomplete_customers: function() {
		this.party_field.awesomeplete.list = this.customers_mapper;
	},

	toggle_edit_button: function(flag) {
		this.page.wrapper.find('.edit-customer-btn').toggle(flag);
	},

	toggle_list_customer: function(flag) {
		this.list_customers.toggle(flag);
	},

	toggle_item_cart: function(flag) {
		this.wrapper.find('.pos-bill-wrapper').toggle(flag);
	},

	add_customer: function() {
		this.frm.doc.customer = "";
		this.update_customer(true);
		this.numeric_keypad.show();
	},

	update_customer: function (new_customer) {
		var me = this;

		this.customer_doc = new frappe.ui.Dialog({
			'title': 'Customer',
			fields: [
				{
					"label": __("Full Name"),
					"fieldname": "full_name",
					"fieldtype": "Data",
					"reqd": 1
				},
				{
					"fieldtype": "Section Break"
				},
				{
					"label": __("Email Id"),
					"fieldname": "email_id",
					"fieldtype": "Data"
				},
				{
					"fieldtype": "Column Break"
				},
				{
					"label": __("Contact Number"),
					"fieldname": "phone",
					"fieldtype": "Data"
				},
				{
					"fieldtype": "Section Break"
				},
				{
					"label": __("Address Name"),
					"read_only": 1,
					"fieldname": "name",
					"fieldtype": "Data"
				},
				{
					"label": __("Address Line 1"),
					"fieldname": "address_line1",
					"fieldtype": "Data"
				},
				{
					"label": __("Address Line 2"),
					"fieldname": "address_line2",
					"fieldtype": "Data"
				},
				{
					"fieldtype": "Column Break"
				},
				{
					"label": __("City"),
					"fieldname": "city",
					"fieldtype": "Data"
				},
				{
					"label": __("State"),
					"fieldname": "state",
					"fieldtype": "Data"
				},
				{
					"label": __("ZIP Code"),
					"fieldname": "pincode",
					"fieldtype": "Data"
				},
				{
					"label": __("Customer POS Id"),
					"fieldname": "customer_pos_id",
					"fieldtype": "Data",
					"hidden": 1
				}
			]
		})
		this.customer_doc.show()
		this.render_address_data()

		this.customer_doc.set_primary_action(__("Save"), function () {
			me.make_offline_customer(new_customer);
			me.pos_bill.show();
			me.list_customers.hide();
		});
	},
render_address_data: function() {
		var me = this;
		this.address_data = this.address[this.frm.doc.customer] || {};
		if(!this.address_data.email_id || !this.address_data.phone) {
			this.address_data = this.contacts[this.frm.doc.customer];
		}

		this.customer_doc.set_values(this.address_data)
		if(!this.customer_doc.fields_dict.full_name.$input.val()) {
			this.customer_doc.set_value("full_name", this.frm.doc.customer_name)
		}

		if(!this.customer_doc.fields_dict.customer_pos_id.value) {
			this.customer_doc.set_value("customer_pos_id", frappe.datetime.now_datetime())
		}
	},

	get_address_from_localstorage: function() {
		this.address_details = this.get_customers_details()
		return this.address_details[this.frm.doc.customer]
	},

	make_offline_customer: function(new_customer) {
		this.frm.doc.customer = this.frm.doc.customer || this.customer_doc.get_values().full_name;
		this.frm.doc.customer_pos_id = this.customer_doc.fields_dict.customer_pos_id.value;
		this.customer_details = this.get_customers_details();
		this.customer_details[this.frm.doc.customer] = this.get_prompt_details();
		this.party_field.$input.val(this.frm.doc.customer);
		this.update_address_and_customer_list(new_customer)
		this.autocomplete_customers();
		this.update_customer_in_localstorage()
		this.update_customer_in_localstorage()
		this.customer_doc.hide()
	},

	update_address_and_customer_list: function(new_customer) {
		var me = this;
		if(new_customer) {
			this.customers_mapper.push({
				label: this.frm.doc.customer,
				value: this.frm.doc.customer,
				customer_group: "",
				territory: ""
			});
		}

		this.address[this.frm.doc.customer] = JSON.parse(this.get_prompt_details())
	},

	get_prompt_details: function() {
		this.prompt_details = this.customer_doc.get_values();
		this.prompt_details['country'] = this.pos_profile_data.country;
		this.prompt_details['territory'] = this.pos_profile_data["territory"];
		this.prompt_details['customer_group'] = this.pos_profile_data["customer_group"];
		this.prompt_details['customer_pos_id'] = this.customer_doc.fields_dict.customer_pos_id.value;
		return JSON.stringify(this.prompt_details)
	},

	update_customer_data: function (doc) {
		var me = this;
		this.frm.doc.customer = doc.label || doc.customer_name;
		this.frm.doc.customer_name = doc.customer_name;
		this.frm.doc.mobile_no = doc.mobile_no;
		this.frm.doc.phone = doc.phone;
		this.frm.doc.email_id = doc.email_id;
		this.frm.doc.customer_group = doc.customer_group;
		this.frm.doc.territory = doc.territory;
		this.pos_bill.show();
		this.numeric_keypad.show();
	},

	make_item_list: function (customer) {
		var me = this;
		if (!this.price_list) {
			frappe.msgprint(__("Price List not found or disabled"));
			return;
		}

		me.item_timeout = null;

		var $wrap = me.wrapper.find(".item-list");
		me.wrapper.find(".item-list").empty();

		if (this.items.length > 0) {
			$.each(this.items, function(index, obj) {
				let customer_price_list = me.customer_wise_price_list[customer];
				let item_price
				if (customer && customer_price_list && customer_price_list[obj.name]) {
					item_price = format_currency(customer_price_list[obj.name], me.frm.doc.currency);
				} else {
					item_price = format_currency(me.price_list_data[obj.name], me.frm.doc.currency);
				}
				if(index < me.page_len) {
					$(frappe.render_template("pos_item", {
						item_code: escape(obj.name),
						item_price: item_price,
						title: obj.name === obj.item_name ? obj.name : obj.item_name,
						item_name: obj.name === obj.item_name ? "" : obj.item_name,
						item_image: obj.image,
						item_stock: __('Stock Qty') + ": " + me.get_actual_qty(obj),
						item_uom: obj.stock_uom,
						color: frappe.get_palette(obj.item_name),
						abbr: frappe.get_abbr(obj.item_name)
					})).tooltip().appendTo($wrap);
				}
			});

			$wrap.append(`
				<div class="image-view-item btn-more text-muted text-center">
					<div class="image-view-body">
						<i class="mega-octicon octicon-package"></i>
						<div>Load more items</div>
					</div>
				</div>
			`);

			me.toggle_more_btn();
		} else {
			$("<p class='text-muted small' style='padding-left: 10px'>"
				+__("Not items found")+"</p>").appendTo($wrap)
		}

		if (this.items.length == 1
			&& this.search_item.$input.val()) {
			this.search_item.$input.val("");
			this.add_to_cart();
		}
	},
});


erpnext.pos.PointOfSale = pos_bahrain.addons.extend_pos(
  erpnext.pos.PointOfSale
);
