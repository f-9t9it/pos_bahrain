// This is for easy reference of the .selected row (hacks)
export default function withIdx(Pos) {
    return class PosExtended extends Pos {
        show_items_in_item_cart() {
            super.show_items_in_item_cart();
            this._set_pos_bill_item_idx();
            $(this.wrapper).find('.pos-bill-item').removeClass('active');
            if (this.selected_cart_idx) {
                $(this.wrapper)
                    .find(`.pos-bill-item[data-idx="${this.selected_cart_idx}"]`)
                    .addClass('active');
            }
        }
        _set_pos_bill_item_idx() {
            const $items = $('div.items').children();
            $.each($items || [], function(i, item) {
               $(item).attr('data-idx', i);
            });
        }
        make_new_cart() {
            this.selected_cart_idx = null;
            super.make_new_cart();
        }
        bind_events() {
            super.bind_events();
            $(this.wrapper).on('click', '.pos-item-wrapper', e => {
                this.selected_cart_idx = null;
            })
        }
        bind_items_event() {
            // from ERPNext POS
            const me = this;
            $(this.wrapper).on('click', '.pos-bill-item', function(e) {
                $(me.wrapper).find('.pos-bill-item').removeClass('active');
                $(this).addClass('active');
                me.numeric_val = "";
                me.numeric_id = "";
                me.item_code = $(this).attr("data-item-code");

                // idx
                me.selected_cart_idx = $(e.currentTarget).attr("data-idx");

                me.render_selected_item();
                me.bind_qty_event();
                me.update_rate();
                $(me.wrapper).find(".selected-item").scrollTop(1000);
            });
        }
    };
}