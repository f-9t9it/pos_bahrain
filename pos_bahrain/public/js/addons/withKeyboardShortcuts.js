export default function withKeyboardShortcuts(Pos) {
  return class PosExtended extends Pos {
    make_control() {
      super.make_control();
      this._bind_keyboard_shortcuts();
    }
    _bind_keyboard_shortcuts() {
      const trigger_new_cart = () => {
        if (this.msgprint && this.msgprint.display) {
          this.msgprint.msg_area.find('.new_doc').click();
        } else {
          this.page.btn_primary.trigger('click');
        }
      };
      const trigger_print = () => {
        if (this.msgprint && this.msgprint.display) {
          this.msgprint.msg_area.find('.print_doc').click();
        } else {
          this.page.btn_secondary.trigger('click');
        }
      };

      $(document).on('keydown', e => {
        if (frappe.get_route_str() === 'pos') {
          if (e.keyCode === 120) {
            // F9
            e.preventDefault();
            e.stopPropagation();
            if (this.dialog && this.dialog.display) {
              // hide payment dialog if visible
              this.dialog.hide();
            } else {
              $(this.numeric_keypad)
                .find('.pos-pay')
                .trigger('click');
            }
          } else if (e.ctrlKey && e.keyCode === 80) {
            // Ctrl + P
            e.preventDefault();
            e.stopPropagation();
            if (this.dialog && this.dialog.display) {
              this.dialog.header
                .find('.buttons > .submit_print')
                .trigger('click');
              trigger_new_cart();
            } else if (this.frm.doc.docstatus == 1) {
              trigger_print();
            }
          } else if (e.ctrlKey && e.keyCode === 66) {
            // Ctrl + B
            e.preventDefault();
            e.stopPropagation();
            trigger_new_cart();
          } else if (e.ctrlKey && e.keyCode === 188) {
            if (this.sales_employee_field) {
              this.sales_employee_field.set_focus();
            }
          }
        }
      });
    }
  };
}
