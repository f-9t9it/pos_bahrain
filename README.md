## Pos Bahrain

## Pos Enhancement over the default POS of ERPNext

  1. Opening Cash (Doctype) - Cashier to enter the opening cash received.
  2. Closing Cash Voucher Customized to Display opening cash for that cashier and the total sales from Opening Cash Voucher time/date till the Closing cash voucher time/date.
  3. Print Barcode from POS - (Example Receipt No. in Barcode Code128A).
  4. Batch Number in POS View with expiry Date.
  5. UOM Field In item list to change UOM of the item.
  6. Make batch number naming Series.
  7. Fetch item number directly in JS using Material Receipt/Purchase receipt Item selection.
  8. Select Default Warehouse in Purchase receipt - (Multi Company Scenario).
  9. Shortcut Key to press Pay in POS - Used F9 to press Pay, Ctrl + P to Print & Ctrl + B for New, ctrl + , focuses on Sales Employee field(When Employee Field is used).
  10. Focus back to Item Search field for user to input next item directly (when Batch item is scanned).
  11. POS to Fetch only those batch and Items which are in stock in the POS profile selected warehouse.
  12. Show Expiry Date while selecting Batch from drop down in Stock Entry (Material Receipt).
  13. Limiting reports to respected company.
  14. Return from offline POS.
  15. Simple Sales and Purchase Register Reports.
  16. Customer Item-Wise Sales Report.
  17. Item Consumption Report.
  18. Item-Wise Sales Return.
  19. Simple Batch Expiry Report.
  20. Customer Sales Summary.
  21. Generate Print format for Closing Voucher.
  22. Restrict Max discount allowed on Offline POS.

## Future Updates
  1. XXXXXXXXXXX

## Version Update
  1. 0.5.0
  Fixed POS Closing voucher bug where all payment entry was grouped by mode of payment.

  2. 0.5.1
  (1) Updated price checker API to include VAT rate and item rate with VAT in API Response.
  (2) Updated Price checker API priority

  3. 0.5.2
  (1) Added employee name in pos closing voucher employee table in list view.

  4. 0.5.3
  (1) Added total invoice count and sales total below employee table

  5. 0.5.4
  (1) Added total collected, total base collected and total expected below payments table

  6. 0.5.5
  (1) updated pos closing voucher, fixed payment entry not shoing and payment entry values not getting added to mode of payment
  7. 0.5.6
  (1) Updated price checker API priority.
  8. 0.5.7
  (1) Added option to enable/disable using credit balance if available.
  9. 0.5.8
  (1) Updated vat on sales per gcc report.
  10. 0.5.9
  (1) Added option to disable core feature of auto deleting batches when a purchase receipt is cancelled.

## Dev Notes

- **Custom Fields** created by this app generally start with `pb_`. There are a few fields that do not follow this convention. Please refer to the `hooks.py` for more info.

#### License

MIT# pos_bahrain
