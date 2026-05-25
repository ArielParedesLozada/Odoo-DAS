# TEST SPECIFICATION: REPORTS
## TS_07 - Tax & Regulatory Reports Ecuador

**Document ID**: TS-007 | **Version**: 1.0 | **Date**: 2026-01-22
**Owner**: QA Lead

---

## TEST CASES

| ID | Test Case | Input | Expected | Criteria |
|:---|:----------|:------|:---------|:---------|
| TS-07-01 | ATS Generation | Month data | Valid XML | Schema validates |
| TS-07-02 | ATS Purchases | Vendor bills | All included | Count matches |
| TS-07-03 | ATS Sales | Customer invoices | All included | Count matches |
| TS-07-04 | ATS Cancelled | Voided docs | Listed in anulados | Sequences correct |
| TS-07-05 | Form 103 Data | IR withholding | Totals match | Per code sum |
| TS-07-06 | Form 104 Data | IVA collected/paid | Correct split | Base + Tax |
| TS-07-07 | Balance Sheet | GL balances | Assets = L + E | Equation balanced |
| TS-07-08 | P&L Report | Income/Expense | Net Income OK | Rev - Exp |
| TS-07-09 | Cash Flow | Period movements | 3 sections correct | Operating/Invest/Finance |
| TS-07-10 | Supercias XBRL | Annual data | Valid XBRL | Schema validates |
| TS-07-11 | IESS Planilla | Payroll data | Valid format | IESS accepts |
| TS-07-12 | Utilidades Report | Profit + loads | Distribution OK | 10% + 5% split |

---

**Test Specification Classification**: ISO 9001:2015 Controlled
