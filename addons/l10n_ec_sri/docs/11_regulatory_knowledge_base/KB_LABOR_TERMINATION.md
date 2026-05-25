# REGULATORY KNOWLEDGE BASE: TERMINATION & LIQUIDATION
## Employment Termination Types and Calculations

**Source**: Código del Trabajo Art. 169-195
**Last Verified**: 2026-01-22

---

## 1. TERMINATION TYPES

### 1.1 Classification
| Type | Spanish | Description | Indemnification |
|:-----|:--------|:------------|:----------------|
| **Voluntary Resignation** | Renuncia voluntaria | Employee quits | Proportional décimos only |
| **Mutual Agreement** | Mutuo acuerdo | Both parties agree | Per agreement |
| **Desahucio (Employer)** | Desahucio empleador | 15-day notice by employer | 25% per year |
| **Desahucio (Employee)** | Desahucio trabajador | 15-day notice by employee | 25% per year (paid by employer) |
| **Unfair Dismissal** | Despido intempestivo | Immediate termination without cause | 3 months + 1/year |
| **Visto Bueno (Employer)** | Visto bueno empleador | Cause-based termination | None if approved |
| **Visto Bueno (Employee)** | Visto bueno trabajador | Employee quits with cause | 25% per year |
| **End of Contract** | Fin de contrato | Contract expires | Per contract type |

---

## 2. LIQUIDATION COMPONENTS

### 2.1 All Terminations Include
| Component | Calculation |
|:----------|:------------|
| **Pending Salary** | Days worked × daily rate |
| **Décimo 13 Proporcional** | (Earnings Dec-Termination) ÷ 12 |
| **Décimo 14 Proporcional** | (SBU ÷ 360) × days in period |
| **Unused Vacation** | (Salary ÷ 24) × unused days |
| **Fondos de Reserva** | If pending (8.33% of pending) |

### 2.2 Desahucio Bonus (Art. 185)
```
Bonificación = 25% × Monthly Salary × Years Worked
```

**Minimum**: 25% of one month's salary (even for <1 year)

### 2.3 Despido Intempestivo (Art. 188)
```
If tenure < 3 years:
    Indemnization = 3 × Monthly Salary

If tenure ≥ 3 years:
    Indemnization = (3 × Monthly Salary) + (1 × Monthly Salary × (Years - 3))
```

**Maximum**: 25 months' salary (for very long tenure)

---

## 3. DETAILED FORMULAS

### 3.1 Décimo 13 Proporcional
```
Period: December 1 (prior year) to Termination Date
D13 = Sum of Monthly Earnings in Period ÷ 12
```

### 3.2 Décimo 14 Proporcional
```
For Costa (period Mar-Feb):
D14 = (SBU ÷ 360) × Days Worked in Period

For Sierra (period Aug-Jul):
D14 = (SBU ÷ 360) × Days Worked in Period
```

### 3.3 Vacation Pay
```
Accrued Days = 15 × (Months Worked ÷ 12)
Plus: 1 extra day per year after 5 years (max 30 total)

Vacation Pay = (Monthly Salary ÷ 24) × Unused Days
```

---

## 4. VISTO BUENO CAUSES

### 4.1 Employer's Causes (Against Employee)
Per **Art. 172**:
1. Repeated tardiness/absences
2. Indiscipline or disobedience
3. Insults or violence against employer
4. Intoxication at work
5. Damage to company property
6. Disclosure of confidential information
7. Sexual harassment

### 4.2 Employee's Causes (Against Employer)
Per **Art. 173**:
1. Insults or mistreatment by employer
2. Salary reduction without consent
3. Non-payment of salary
4. Dangerous working conditions
5. Sexual harassment by employer

---

## 5. NOTICE PERIODS

| Type | Notice Required | Who Gives Notice |
|:-----|:----------------|:-----------------|
| Desahucio | 15 days (written) | Either party |
| Visto Bueno | N/A (process with Inspector) | Requesting party |
| Despido Intempestivo | None | Employer (pays indemnification) |
| Resignation | None (courtesy: 15 days) | Employee |

---

## 6. CALCULATION EXAMPLE

**Scenario**:
- Monthly Salary: $800
- Start Date: January 1, 2022
- Termination: July 15, 2026 (Despido Intempestivo)
- Tenure: 4 years, 6 months
- SBU 2026: $482
- Unused Vacation: 10 days

**Liquidation Calculation**:
```
1. Pending Salary (15 days):
   = ($800 / 30) × 15 = $400.00

2. Décimo 13 Proporcional (Dec 1, 2025 - Jul 15, 2026 = 7.5 months):
   = ($800 × 7.5) / 12 = $500.00

3. Décimo 14 Proporcional (Sierra: Aug 1, 2025 - Jul 15, 2026):
   = ($482 / 360) × 349 = $467.30

4. Unused Vacation (10 days):
   = ($800 / 24) × 10 = $333.33

5. Despido Intempestivo (4.5 years):
   = (3 × $800) + (1 × $800 × (4.5 - 3))
   = $2,400 + $1,200 = $3,600.00

TOTAL LIQUIDATION = $5,300.63
```

---

## 7. ACTA DE FINIQUITO

### 7.1 Requirements
- Must be signed before Ministerio del Trabajo inspector
- Lists all payment components
- Requires employee signature (or representative)
- Creates legal finality (no future claims)

### 7.2 Timeline
- Payment due within 15 days of termination
- Registration within 30 days

---

## 8. SYSTEM IMPLEMENTATION NOTES

For `l10n_ec_hr_payroll` module:

1. **Termination Wizard**: Guide through termination type selection
2. **Automatic Calculation**: Compute all liquidation components
3. **Region Logic**: Costa vs Sierra for Décimo 14
4. **Tenure Calculator**: Precise years/months/days
5. **Vacation Tracker**: Accrued vs used days
6. **Indemnification Formula**: Per termination type
7. **Acta Generation**: Print-ready document for Ministry
8. **Cap Enforcement**: 25-month limit for despido

---

**Knowledge Base Entry ID**: KB-LABOR-004
**Verification Status**: VERIFIED
**Legal Authority**: CT Art. 169-195, especially Art. 172, 173, 185, 188
**Next Review Date**: 2027-01-01
