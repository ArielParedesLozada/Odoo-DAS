# TEST SPECIFICATION: PAYROLL (HR/NÓMINA)
## TS_03 - Ecuador Labor & IESS Compliance

**Document ID**: TS-003 | **Version**: 1.0 | **Date**: 2026-01-22
**Owner**: QA Lead (Expert Crew)
**Regulatory Refs**: [KB_IESS_CONTRIBUTIONS](../11_regulatory_knowledge_base/KB_IESS_CONTRIBUTIONS.md), [KB_LABOR_SBU_DECIMOS](../11_regulatory_knowledge_base/KB_LABOR_SBU_DECIMOS.md)

---

## 1. TEST SCOPE

Validate Ecuador payroll calculations: IESS, Décimos, Fondos de Reserva, Utilidades, Income Tax, Termination.

---

## 2. TEST CASES

### 2.1 IESS Contributions

| ID | Test Case | Input | Expected | Acceptance Criteria |
|:---|:----------|:------|:---------|:--------------------|
| TS-03-01 | IESS Personal 9.45% | Wage $1000 | $94.50 deducted | `abs(result - 94.50) < 0.01` |
| TS-03-02 | IESS Patronal 12.15% | Wage $1000 | $121.50 expense | `abs(result - 121.50) < 0.01` |
| TS-03-03 | IESS Ceiling (25×SBU) | Wage $15,000 | Contrib on $12,050 max | `base <= 12050` |
| TS-03-04 | Partial Month Entry | 15 days worked | Pro-rated calculation | `result = wage * (15/30) * 0.0945` |
| TS-03-05 | Novedad EN (Entry) | Start date mid-month | EN code in planilla | File shows EN + date |

### 2.2 Décimo Tercero

| ID | Test Case | Input | Expected | Acceptance Criteria |
|:---|:----------|:------|:---------|:--------------------|
| TS-03-06 | Full Year D13 | 12 months @ $1000 | $1000 payment | `result = 1000` |
| TS-03-07 | Partial Year D13 | 6 months @ $1200 | $600 payment | `result = (6/12) * 1200` |
| TS-03-08 | Mensualizado D13 | Monthly opt-in | ~$83.33/month | `result = wage / 12` |
| TS-03-09 | D13 Provisioning | Accrual journal | 8.33% expense monthly | GL entry correct |

### 2.3 Décimo Cuarto

| ID | Test Case | Input | Expected | Acceptance Criteria |
|:---|:----------|:------|:---------|:--------------------|
| TS-03-10 | Full Year D14 | 12 months service | 1 SBU ($482) | `result = 482` |
| TS-03-11 | Partial Year D14 | 8 months service | $321.33 | `result = 482 * (8/12)` |
| TS-03-12 | Regional Date | Costa region | Aug 15 deadline | System enforces date |
| TS-03-13 | Regional Date | Sierra region | Apr 15 deadline | System enforces date |

### 2.4 Fondos de Reserva

| ID | Test Case | Input | Expected | Acceptance Criteria |
|:---|:----------|:------|:---------|:--------------------|
| TS-03-14 | Before 13 months | 10 months service | $0 | No FR calculated |
| TS-03-15 | After 13 months | 14 months service | 8.33% of wage | `result = wage * 0.0833` |
| TS-03-16 | Mensualizado FR | Monthly payment | Paid to employee | Shows in payslip |
| TS-03-17 | Acumulado FR | IESS deposit | Export to planilla | Not in payslip |

### 2.5 Income Tax Withholding

| ID | Test Case | Input | Expected | Acceptance Criteria |
|:---|:----------|:------|:---------|:--------------------|
| TS-03-18 | Below threshold | $15K annual | $0 withheld | No IR deduction |
| TS-03-19 | First bracket | $18K annual | 5% on excess | Correct formula |
| TS-03-20 | Middle bracket | $40K annual | Per 2026 table | Matches SRI table |
| TS-03-21 | GP deduction | Form 107 issued | Expenses applied | Net income reduced |

### 2.6 Termination (Liquidación)

| ID | Test Case | Input | Expected | Acceptance Criteria |
|:---|:----------|:------|:---------|:--------------------|
| TS-03-22 | Voluntary Resignation | 2 years service | D13+D14+Vacation | No indemnity |
| TS-03-23 | Despido Intempestivo | 3 years service | +25% per year | Proper indemnity |
| TS-03-24 | Desahucio | 2 years + 15 days | +25% per year + bonus | Correct formula |
| TS-03-25 | Vacation Balance | 18 unused days | Daily rate × 18 | Paid correctly |

### 2.7 Utilidades

| ID | Test Case | Input | Expected | Acceptance Criteria |
|:---|:----------|:------|:---------|:--------------------|
| TS-03-26 | Pool Calculation | $100K profit | $15K pool | `result = 100000 * 0.15` |
| TS-03-27 | Days Distribution | 365 days total | 10% by days worked | Per-employee correct |
| TS-03-28 | Family Loads | 3 dependents | 5% by loads | Extra per dependent |
| TS-03-29 | Maximum Cap | High earner | ≤ 24 SBU per person | `result <= 24 * 482` |

---

## 3. EXECUTION MATRIX

| Phase | Test IDs | Environment | Data |
|:------|:---------|:------------|:-----|
| Unit | 01-17 | Dev | Mock employees |
| Integration | 18-25 | Staging | Real contracts |
| UAT | 26-29 | Production-like | Historical data |

---

## 4. DEFECT SEVERITY

| Severity | Definition | Response |
|:---------|:-----------|:---------|
| Critical | Wrong IESS amounts | Block release |
| High | Wrong décimos | Fix within 24h |
| Medium | Rounding errors | Fix in sprint |
| Low | Display issues | Backlog |

---

**Test Specification Classification**: ISO 9001:2015 Controlled
