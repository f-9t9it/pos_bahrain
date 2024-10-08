export default function withGetChildItemByIdx(Pos) {
    return class PosExtended extends Pos {
        get_child_item(item_code) {
            const idx = this.wrapper.find('.pos-bill-item.active').data('idx');
            return $.map(this.frm.doc.items, function(doc, id) {
                if (id === idx) {
                    return doc;
                }
            });
        }
    };
}