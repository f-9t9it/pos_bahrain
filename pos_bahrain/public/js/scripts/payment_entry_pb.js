function get_account_types(field, payment_type, party_type) {
  const cash_accounts = ['Bank', 'Cash'];
  const party_accounts = [frappe.boot.party_account_types[party_type]];
  if (
    (field === 'paid_from' && payment_type === 'Pay') ||
    (field === 'paid_to' && payment_type === 'Receive')
  ) {
    return ['in', cash_accounts];
  }
  if (
    (field === 'paid_from' && payment_type === 'Receive') ||
    (field === 'paid_to' && payment_type === 'Pay')
  ) {
    return ['in', party_accounts];
  }
  return null;
}

export default function () {
  return {
    setup: function (frm) {
      ['paid_from', 'paid_to'].forEach((field) => {
        frm.set_query(field, ({ company, payment_type, party_type }) => {
          return {
            filters: {
              account_type: get_account_types(field, payment_type, party_type),
              is_group: 0,
              company,
            },
          };
        });
      });
    },
  };
}
