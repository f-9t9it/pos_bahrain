export default function withSubmittedInvoice(Pos) {
  return class PosExtended extends Pos {
    async init_master_data(r, freeze) {
      const pos_data = await super.init_master_data(r, freeze);

      const { override_sync_limit } = pos_data;
      this.override_sync_limit = !!cint(override_sync_limit);
      if (override_sync_limit) {
        this.sync_limit = await frappe.db.get_single_value('POS Bahrain Settings', 'sync_limit');
        console.log(this.sync_limit);
        console.log(this.override_sync_limit);
      }

      return pos_data;
    }
    get_submitted_invoice() {
      if (!this.override_sync_limit) {
        return super.get_submitted_invoice();
      }

      let index = 0;
      let invoices = [];

      const docs = this.get_doc_from_localstorage();
      if (docs) {
        invoices = $.map(docs, (data) => {
          for (const key in data) {
            if (data[key].docstatus === 1 && index < this.sync_limit) {
              data[key].docstatus = 0;
              index = index + 1;
              return data;
            }
          }
        });
      }

      return invoices;
    }
  };
}