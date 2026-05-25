# CONFIGURATION CHECKLIST: PAYROLL SETUP
## CC_02 - Ecuador HR/Payroll Configuration

**Document ID**: CC-002 | **Version**: 1.0 | **Date**: 2026-01-22
**Owner**: Implementation Lead (Expert Crew)
**Regulatory Refs**: All KB_LABOR_* and KB_IESS_* documents

---

## 1. PRE-REQUISITES

| # | Item | Status |
|:--|:-----|:-------|
| 1 | Chart of Accounts configured | ☐ |
| 2 | Company address (region) set | ☐ |
| 3 | SBU 2026 ($482) configured | ☐ |
| 4 | IESS employer code obtained | ☐ |

---

## 2. SYSTEM PARAMETERS

### 2.1 Labor Parameters

| Path | Setting | Value 2026 | Verify |
|:-----|:--------|:-----------|:-------|
| Settings > HR > Ecuador | SBU | $482.00 | ☐ |
| Settings > HR > Ecuador | IESS Personal Rate | 9.45% | ☐ |
| Settings > HR > Ecuador | IESS Patronal Rate | 12.15% | ☐ |
| Settings > HR > Ecuador | Fondos Reserva Rate | 8.33% | ☐ |
| Settings > HR > Ecuador | Contribution Ceiling | 25 × SBU | ☐ |
| Settings > HR > Ecuador | D14 Sierra Date | April 15 | ☐ |
| Settings > HR > Ecuador | D14 Costa Date | August 15 | ☐ |

### 2.2 Income Tax Brackets

| Bracket | From | To | Rate | Base | Verify |
|:--------|:-----|:---|:-----|:-----|:-------|
| 1 | $0 | $11,722 | 0% | $0 | ☐ |
| 2 | $11,722 | $14,930 | 5% | $0 | ☐ |
| 3 | $14,930 | $19,385 | 10% | $160 | ☐ |
| 4 | $19,385 | $25,638 | 12% | $606 | ☐ |
| 5 | $25,638 | $33,738 | 15% | $1,356 | ☐ |
| 6 | $33,738 | $44,721 | 20% | $2,571 | ☐ |
| 7 | $44,721 | $59,537 | 25% | $4,768 | ☐ |
| 8 | $59,537 | $79,388 | 30% | $8,472 | ☐ |
| 9 | $79,388 | $105,580 | 35% | $14,427 | ☐ |
| 10 | $105,580 | + | 37% | $23,594 | ☐ |

---

## 3. SALARY RULES CONFIGURATION

### 3.1 Earnings

| Rule Code | Name | Category | Formula |
|:----------|:-----|:---------|:--------|
| BASIC | Sueldo Básico | GROSS | `contract.wage` |
| HE50 | Horas Extras 50% | GROSS | `hours * hourly_rate * 1.5` |
| HE100 | Horas Extras 100% | GROSS | `hours * hourly_rate * 2.0` |
| COMIS | Comisiones | GROSS | `inputs.COMIS.amount` |
| D13_MENS | Décimo 13 Mensualizado | GROSS | `wage / 12` |
| D14_MENS | Décimo 14 Mensualizado | GROSS | `482 / 12` |

### 3.2 Deductions

| Rule Code | Name | Category | Formula |
|:----------|:-----|:---------|:--------|
| IESS_PER | IESS Personal | DED | `min(GROSS, ceiling) * 0.0945` |
| IR | Impuesto Renta | DED | `calculate_ir(annual_income)` |
| ADELANTO | Anticipo | DED | `inputs.ADELANTO.amount` |
| PRESTAMO | Préstamo Quirografario | DED | `inputs.PRESTAMO.amount` |

### 3.3 Employer Contributions

| Rule Code | Name | Category | Formula |
|:----------|:-----|:---------|:--------|
| IESS_PAT | IESS Patronal | EMP | `min(GROSS, ceiling) * 0.1215` |
| FR | Fondos Reserva | EMP | `wage * 0.0833 if months > 13` |
| D13_PROV | Décimo 13 Provisión | EMP | `wage * 0.0833` |
| D14_PROV | Décimo 14 Provisión | EMP | `482 / 12` |
| VAC_PROV | Vacaciones Provisión | EMP | `wage * 0.0416` |

---

## 4. ACCOUNTING CONFIGURATION

### 4.1 Salary Journal Entries

| Concept | Debit Account | Credit Account |
|:--------|:--------------|:---------------|
| Gross Wages | 5.1.1.01 Sueldos | 2.1.3.01 Sueldos por Pagar |
| IESS Personal | 2.1.3.01 Sueldos | 2.1.5.01 IESS por Pagar |
| IESS Patronal | 5.1.2.01 Aporte Patronal | 2.1.5.01 IESS por Pagar |
| Décimo 13 Prov | 5.1.2.02 Décimo Tercero | 2.1.3.02 D13 por Pagar |
| Décimo 14 Prov | 5.1.2.03 Décimo Cuarto | 2.1.3.03 D14 por Pagar |
| Fondos Reserva | 5.1.2.04 Fondos Reserva | 2.1.5.02 FR por Pagar |
| Income Tax | 2.1.3.01 Sueldos | 2.1.4.01 IR por Pagar |

---

## 5. EMPLOYEE MASTER DATA

| Field | Required | Source | Verify |
|:------|:---------|:-------|:-------|
| Cédula / Pasaporte | ✓ | Employee | ☐ |
| IESS Affiliation # | ✓ | IESS Portal | ☐ |
| Contract Start Date | ✓ | Contract | ☐ |
| Contract Type | ✓ | Contract | ☐ |
| Region (Costa/Sierra) | ✓ | Work Location | ☐ |
| Bank Account | ✓ | Employee | ☐ |
| Family Loads | ✓ | Employee | ☐ |

---

## 6. PAYROLL STRUCTURES

| Structure | Applies To | Rules Included |
|:----------|:-----------|:---------------|
| EC_STANDARD | Permanent employees | All rules |
| EC_TEMPORARY | Temporary contracts | Exclude FR, D13/14 prov |
| EC_DOMESTIC | Domestic workers | Different IESS rate |
| EC_EXECUTIVE | Executives | Higher IR brackets |

---

## 7. PERIOD CONFIGURATION

| Period | Frequency | Run Date |
|:-------|:----------|:---------|
| Monthly Payroll | Monthly | Last day |
| IESS Planilla | Monthly | 15th next month |
| Décimo 13 | Annual | December 24 |
| Décimo 14 | Annual | April 15 / Aug 15 |
| Utilidades | Annual | April 15 |

---

## 8. VERIFICATION STEPS

| # | Test | Expected | Passed |
|:--|:-----|:---------|:-------|
| 1 | Create test employee $1000 | - | ☐ |
| 2 | Run payslip | IESS = $94.50 | ☐ |
| 3 | Check IESS Patronal | $121.50 | ☐ |
| 4 | Check D13 provision | $83.33 | ☐ |
| 5 | Export IESS planilla | Valid file | ☐ |
| 6 | Post payroll entries | Balanced | ☐ |

---

## 9. SIGN-OFF

| Role | Name | Date | Signature |
|:-----|:-----|:-----|:----------|
| HR Manager | | | |
| Finance Manager | | | |
| IT Lead | | | |
| Project Manager | | | |

---

**Configuration Checklist Classification**: ISO 9001:2015 Controlled
