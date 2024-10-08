export default function withExtendedBatchSelector(Pos) {
  return class PosExtended extends Pos {
    onload() {
      super.onload();
      this.batch_dialog = new frappe.ui.Dialog({
        title: __('Select Batch No'),
        fields: [
          {
            fieldname: 'batch',
            fieldtype: 'Select',
            label: __('Batch No'),
            reqd: 1,
          },
        ],
      });
    }
    async init_master_data(r, freeze) {
      const pos_data = await super.init_master_data(r, freeze);
      const { batch_no_details } = pos_data;
      try {
        if (!batch_no_details) {
          throw new Error();
        }
        this.batch_no_data = Object.keys(batch_no_details).reduce(
          (a, x) =>
            Object.assign(a, {
              [x]: batch_no_details[x].map(({ name }) => name),
            }),
          {}
        );
        this.batch_no_details = batch_no_details;
      } catch (e) {
        frappe.msgprint({
          indicator: 'orange',
          title: __('Warning'),
          message: __(
            'Unable to load extended Item details. Usage will be restricted.'
          ),
        });
      } finally {
        return pos_data;
      }
    }
    mandatory_batch_no() {
      return new Promise(resolve => {
        const { has_batch_no, item_code } = this.items[0];

        // do not open selector but resolve with batch_no set by the get_items method
        // from search_item input field
        if (!has_batch_no || this.item_batch_no[item_code]) {
          return resolve(this.item_batch_no[item_code]);
        }

        this.batch_dialog.get_field('batch').$input.empty();
        this.batch_dialog.get_primary_btn().off('click');
        this.batch_dialog.get_close_btn().off('click');
        (this.batch_no_details[item_code] || []).forEach(
          ({ name, expiry_date, qty }) => {
            this.batch_dialog
              .get_field('batch')
              .$input.append(
                $('<option />', { value: name }).text(
                  `${name} | ${
                    expiry_date
                      ? frappe.datetime.str_to_user(expiry_date)
                      : '--'
                  } | ${qty}`
                )
              );
          }
        );
        this.batch_dialog.get_field('batch').set_input();
        this.batch_dialog.set_primary_action(__('Submit'), () => {
          const batch_no = this.batch_dialog.get_value('batch');
          this.item_batch_no[this.items[0].item_code] = batch_no;
          this.batch_dialog.hide();
          this.set_focus();
          resolve(batch_no);
        });
        this.batch_dialog.get_close_btn().on('click', () => {
          this.item_code = item_code;
          this.render_selected_item();
          this.remove_selected_item();
          this.wrapper.find('.selected-item').empty();
          this.item_code = null;
          this.set_focus();
          resolve();
        });
        this.batch_dialog.show();
        this.batch_dialog.$wrapper.find('.modal-backdrop').off('click');
      });
    }
  };
}
