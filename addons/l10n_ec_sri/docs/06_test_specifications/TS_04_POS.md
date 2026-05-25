# TEST SPECIFICATION: POS
## TS_04 - Point of Sale Ecuador Compliance

**Document ID**: TS-004 | **Version**: 1.0 | **Date**: 2026-01-22
**Owner**: QA Lead

---

## TEST CASES

| ID | Test Case | Input | Expected | Criteria |
|:---|:----------|:------|:---------|:---------|
| TS-04-01 | POS Invoice < 2 sec | Standard sale | Invoice in < 2s | Timer check |
| TS-04-02 | Consumidor Final ≤ $50 | $45 no ID | Accepted | No validation error |
| TS-04-03 | Consumidor Final > $50 | $60 no ID | Blocked | Error message |
| TS-04-04 | Named Invoice | $100 + RUC | Accepted | Partner on invoice |
| TS-04-05 | Cash Payment | Pay $50 cash | Change calculated | Correct change |
| TS-04-06 | Card Payment | Pay card | Card processed | Receipt printed |
| TS-04-07 | Split Payment | $50 cash + $50 card | Both recorded | Two payment lines |
| TS-04-08 | Print RIDE | Complete sale | PDF printed | Valid format |
| TS-04-09 | Session Open | Open POS | Balance prompt | Cash entry required |
| TS-04-10 | Session Close | End day | Z Report | Totals match |
| TS-04-11 | Cash Discrepancy | Count differs | Alert shown | Manager approval |
| TS-04-12 | Offline Mode | No internet | Queue invoices | Sync when online |
| TS-04-13 | Product Barcode | Scan barcode | Product added | Correct price |
| TS-04-14 | Discount Apply | 10% discount | Price reduced | Tax recalculated |
| TS-04-15 | Return/Refund | Return item | Credit note | Linked to original |

---

**Test Specification Classification**: ISO 9001:2015 Controlled
