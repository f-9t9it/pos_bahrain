export default function withCustomerContacts(Pos) {
    return class PosExtended extends Pos {
      async init_master_data(r, freeze) {
        const pos_data = await super.init_master_data(r, freeze);
        const { customer_contacts } = pos_data;
        this.customer_contacts = customer_contacts;
        return pos_data;
      }
      make_customer() {
        super.make_customer();
        const me = this;
        me.party_field.$input.on('awesomplete-select', function (e) {
          const customer = e.originalEvent.text.value;
          me.frm.doc.phone = me.customer_contacts[customer] || '';
        });
      }
    };
  }