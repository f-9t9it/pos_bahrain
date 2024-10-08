export default function withBatchField(Pos) {
    return class PosExtended extends Pos {
        render_selected_item() {
            super.render_selected_item();
            this._render_batch_field();
        }
        _render_batch_field() {
            const item = this.item_data.find(item => item.item_code === unescape(this.item_code));
            if (item.has_batch_no) {
                const $selected_item_action = this.wrapper.find('.pos-selected-item-action');
                $(`
                    <div class="pos-list-row">
                        <div class="cell">${__('Batch No')}:</div>
                        <select type="text" class="form-control cell pos-item-batch" />
                    </div>
                `).prependTo($selected_item_action);

                const idx = this.wrapper.find('.pos-bill-item.active').data('idx');
                const item = this.frm.doc.items[idx];
                const $select = this.wrapper.find('.pos-item-batch');
                this.batch_no_data[unescape(this.item_code)].forEach(batch_no => {
                    const opts = {
                        value: batch_no,
                        selected: item && batch_no === item.batch_no
                    };
                    $('<option />', opts)
                        .text(batch_no)
                        .appendTo($select);
                });

                $select.on('change', e => {
                   e.stopPropagation();
                   item.batch_no = e.target.value;
                   this.render_selected_item();
                });
            }
        }
    };
}