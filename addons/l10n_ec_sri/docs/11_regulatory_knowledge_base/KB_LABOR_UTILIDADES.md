# REGULATORY KNOWLEDGE BASE: UTILIDADES (PROFIT SHARING)
## Verified from ecuadorlegalonline.com - January 2026

**Source**: https://www.ecuadorlegalonline.com/laboral/reparto-utilidades/
**Legal Basis**: Código del Trabajo Art. 97-100
**Last Verified**: 2026-01-22

---

## 1. DEFINITION

Utilidades represent a portion of a company's net profits distributed among workers. Per **Art. 97 del Código del Trabajo**, companies must allocate **15%** of their annual net profits to employees.

---

## 2. KEY PARAMETERS

| Attribute | Value |
|:----------|:------|
| **Total Pool** | **15%** of net annual profits (utilidades líquidas) |
| **Distribution** | 10% by days worked + 5% by family loads |
| **Payment Deadline** | **April 15** |
| **Late Deposit** | Min. Trabajo within 30 days, else 2× penalty |
| **Legal Basis** | CT Art. 97-100 |

---

## 3. DISTRIBUTION FORMULA

### 3.1 10% Component (All Workers)
Distributed based on **days worked** during the fiscal year.

```
Factor A = Days worked by employee
Factor B = Total days worked by ALL employees

Employee Share (10%) = (10% of profits) × (Factor A / Factor B)
```

### 3.2 5% Component (Family Loads)
Distributed based on **days worked × family loads**.

```
Factor 1 = Days worked × Number of family loads
Factor 2 = Sum of Factor 1 for ALL employees

Employee Share (5%) = (5% of profits) × (Factor 1 / Factor 2)
```

---

## 4. CALCULATION EXAMPLE

**Scenario**:
- Company net profit: $200,000
- 15% pool = $30,000 (10% = $20,000, 5% = $10,000)
- Employee worked 300 days with 2 family loads
- Total company days worked: 50,000
- Total company Factor 1: 20,000

**Calculation**:
```
10% share = $20,000 × (300 / 50,000) = $120.00
5% share = $10,000 × (300 × 2 / 20,000) = $300.00
TOTAL = $420.00
```

---

## 5. ELIGIBILITY

### 5.1 Who Receives Utilidades
- Full-time workers under dependency relationship
- Part-time workers (proportional)
- Ex-workers who worked during the fiscal year

### 5.2 Proportional Payment
Workers who did not work the full year receive proportional share based on:
- Days actually worked
- Family loads during employment period

### 5.3 Requirements
1. **Marriage certificate** (if applicable)
2. **Birth certificates** of minor children or those with disabilities
3. **Employment relationship** during the fiscal year
4. **Documentation** submitted before company closes liquidation

---

## 6. FAMILY LOADS (CARGAS FAMILIARES)

| Relationship | Qualifies? |
|:-------------|:-----------|
| Spouse | Yes |
| Children under 18 | Yes |
| Children with disability | Yes (any age) |
| Parents | No |
| Other dependents | No |

---

## 7. MAXIMUM PER EMPLOYEE

| Attribute | Value |
|:----------|:------|
| **Individual Cap** | 24 × SBU = 24 × $482 = **$11,568** (2026) |
| **Excess Distribution** | Proportionally to other workers |

---

## 8. REGISTRATION REQUIREMENT

Employers must register payment in **Ministerio del Trabajo** portal following the cronogram based on RUC's 9th digit.

---

## 9. SYSTEM IMPLEMENTATION NOTES

For `l10n_ec_hr_payroll` module:

1. **Family Loads Field**: `hr.employee.family_loads` (Integer)
2. **Days Worked**: Track actual working days per fiscal year
3. **Two-Step Calculation**: Calculate 10% and 5% separately
4. **Cap Validation**: Enforce 24×SBU maximum
5. **Excess Redistribution**: Algorithm for redistributing excess
6. **Report Generation**: Ministry registration report
7. **Ex-Employee Handling**: Include terminated workers proportionally

---

## 10. PENALTIES

| Violation | Penalty |
|:----------|:--------|
| Late payment (>15 days) | Up to 2× amount owed |
| Failure to register | Administrative fine |
| False declaration | Criminal liability |

---

**Knowledge Base Entry ID**: KB-LABOR-003
**Verification Status**: VERIFIED
**Legal Authority**: CT Art. 97-100
**Next Review Date**: 2027-01-01
