export default function withCustomItemCart(Pos) {
    return class PosExtended extends Pos {
        async init_master_data(r, freeze) {
            const pos_data = await super.init_master_data(r, freeze);
            const { use_custom_item_cart } = pos_data;

            this.use_custom_item_cart = cint(use_custom_item_cart);

            if (this.use_custom_item_cart) {
                const { message: item_cart_fields } = await frappe.call({
                    method: 'pos_bahrain.api.item.get_custom_item_cart_fields',
                    freeze,
                    freeze_message: __('Getting custom item cart fields'),
                });

                if (!item_cart_fields) {
                    frappe.throw(
                        __('Set the item cart fields under POS Bahrain Settings')
                    );
                }

                this.item_cart_fields = item_cart_fields;
                this.make_discount_field(); // for async
                this._make_styles();
            }

            return pos_data;
        }
        make_discount_field() {
            super.make_discount_field();

            const { use_custom_item_cart } = this;

            if (use_custom_item_cart) {
                const $header = this.wrapper.find(".item-cart > .pos-bill-header").empty();
                this._render_custom_item_cart_fields($header);
            }
        }
        show_items_in_item_cart() {
            const { use_custom_item_cart } = this;

            if (!use_custom_item_cart) {
                super.show_items_in_item_cart();
                return;
            }

            // from erpnext POS
            const $items = this.wrapper.find(".items").empty();
            const $no_items_message = this.wrapper.find(".no-items-message");
            $no_items_message.toggle(this.frm.doc.items.length === 0);

            $.each(this.frm.doc.items || [], (i, item) => {
                this._render_pos_list_row($items, item);
            });
        }
        _render_custom_item_cart_fields($header) {
            const { item_cart_fields } = this;
            item_cart_fields.forEach(field => {
                $header.append(`
                    <span class="cell" id="${field.item_field}">${__(field.label)}</span>
                `);
            })
        }
        _render_pos_list_row($items, item) {
            const { item_cart_fields } = this;
            const pos_list_row_field = item_cart_fields.map(field => {
                const value = item[field.item_field];
                return `
                    <div class="cell" id="${field.item_field}">
                        ${this._format_value(value, field.fieldtype)}
                    </div>
                `;
            });

            $items.append(`
                <div class="pos-list-row pos-bill-item" data-item-code="${item.item_code}">
                    ${pos_list_row_field.join("\n")}
                </div>
            `);
        }
        _format_value(value, fieldtype) {
            if (fieldtype === "Currency") {
                return format_currency(value);
            } else {
                return value;
            }
        }
        _make_styles() {
            const col_styles = this._make_col_styles().join("\n");
            $('head').append(`
                <style type="text/css">
                    body[data-route="pos"] .pos-list-row .cell { overflow-wrap: break-word; }
                    ${col_styles}
                </style>
            `);
        }
        _make_col_styles() {
            const { item_cart_fields } = this;
            const styles = [];
            item_cart_fields.forEach(field => {
                if (field.width > 0) {
                    styles.push(`.cell#${field.item_field} { width: ${field.width}%; }`);
                }
            });
            return styles;
        }
    };
}