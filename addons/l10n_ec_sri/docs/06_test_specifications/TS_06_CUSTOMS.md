# TEST SPECIFICATION: CUSTOMS
## TS_06 - Import/Export Ecuador (SENAE)

**Document ID**: TS-006 | **Version**: 1.0 | **Date**: 2026-01-22
**Owner**: QA Lead

---

## TEST CASES

| ID | Test Case | Input | Expected | Criteria |
|:---|:----------|:------|:---------|:---------|
| TS-06-01 | CIF Calculation | FOB+Freight+Ins | CIF correct | Formula verified |
| TS-06-02 | Ad-Valorem 20% | CIF $11,000 | $2,200 | `CIF * 0.20` |
| TS-06-03 | FODINFA 0.5% | CIF $11,000 | $55 | `CIF * 0.005` |
| TS-06-04 | ICE Calculation | Applicable product | ICE computed | Rate table |
| TS-06-05 | IVA on Import | All duties+CIF | 15% on total | Formula verified |
| TS-06-06 | Total Duties | Full import | All taxes sum | Matches manual |
| TS-06-07 | Landed Cost | Allocate to items | Cost updated | FIFO/Average |
| TS-06-08 | Multi-currency | EUR purchase | USD conversion | Exchange rate |
| TS-06-09 | Customs Expense | Record payment | Journal balanced | GL correct |
| TS-06-10 | IVA Tax Credit | Import IVA | Credit recorded | 1.1.2.01 Debit |
| TS-06-11 | Goods Receipt | PO + Duties | Stock valued | Landed cost |
| TS-06-12 | Partial Shipment | 50% received | Pro-rata duties | Correct allocation |

---

**Test Specification Classification**: ISO 9001:2015 Controlled
