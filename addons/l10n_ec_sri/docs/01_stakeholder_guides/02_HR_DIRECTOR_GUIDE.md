# HR DIRECTOR DEFINITIVE REFERENCE GUIDE
## Lic. Carlos Talento Humano, MBA

**Document ID**: HR-DRG-001
**Version**: 2.0 (Enterprise Grade)
**Date**: 2026-01-22

---

## 1. REGULATORY FRAMEWORK

### 1.1 Governing Bodies
| Entity | Scope | System Integration |
|:-------|:------|:-------------------|
| **IESS** | Social Security | Planillas automáticas |
| **Min. Trabajo** | Contratos, SUT | Contract registration |
| **SRI** | Form 107, Utilidades | Payroll reports |

### 1.2 Primary Legal References
- **Código del Trabajo** (CT): Art. 42-185
- **Ley de Seguridad Social** (LSS): Art. 73-87
- **LORTI**: Art. 8-10 (Income Tax on employment)

---

## 2. IESS CONTRIBUTION RATES (2026)

### 2.1 Mandatory Contributions
| Concept | Employee | Employer | Total |
|:--------|:---------|:---------|:------|
| **Aporte Personal** | 9.45% | - | 9.45% |
| **Aporte Patronal** | - | 12.15% | 12.15% |
| **IECE** (Education) | - | 0.50% | 0.50% |
| **SECAP** (Training) | - | 0.50% | 0.50% |
| **Total** | **9.45%** | **13.15%** | **22.60%** |

> **Note**: Odoo payroll rule `hr.salary.rule` applies these via `amount_python_compute`.

### 2.2 Computation Formula
```python
# From hr.salary.rule (l10n_ec_hr_payroll)
def compute_iess_personal(payslip, inputs, worked_days, employee):
    base = payslip.contract_id.wage
    return -round(base * 0.0945, 2)  # Deduction (negative)

def compute_iess_patronal(payslip, inputs, worked_days, employee):
    base = payslip.contract_id.wage
    return round(base * 0.1315, 2)  # Company expense
```

### 2.3 Maximum Contributable Income
- **2026**: 25× SBU = $12,050/month
- Ceiling applies to both employee and employer

---

## 3. SALARIO BÁSICO UNIFICADO (SBU)

| Year | Amount | CT Reference |
|:-----|:-------|:-------------|
| 2024 | $460.00 | Acuerdo Min. |
| 2025 | $470.00 | Acuerdo Min. |
| 2026 | $482.00 | **Projected** |

### 3.1 Sectoral Minimum Wages
Define in `hr.contract.branch` model from legacy `l10n_ec_hr_contract`:
- Construcción: SBU + 15%
- Transporte: SBU + 12%
- Agricultura: SBU + 8%

---

## 4. DÉCIMOS (BONUS CALCULATIONS)

### 4.1 Décimo Tercero (Christmas Bonus)
| Attribute | Value |
|:----------|:------|
| **Legal Basis** | CT Art. 95-96 |
| **Formula** | (Σ Monthly Earnings Dec-Nov) ÷ 12 |
| **Payment Deadline** | December 24 |
| **Accrual Period** | December 1 (prior year) - November 30 |

```python
# Décimo 13 Calculation
def compute_decimo_13(employee, year):
    start = date(year-1, 12, 1)
    end = date(year, 11, 30)
    total_earnings = sum(payslip.gross for payslip in payslips(start, end))
    return round(total_earnings / 12, 2)
```

### 4.2 Décimo Cuarto (School Bonus)
| Attribute | Value |
|:----------|:------|
| **Legal Basis** | CT Art. 97 |
| **Amount** | 1 SBU ($482 in 2026) |
| **Costa/Insular Deadline** | March 15 |
| **Sierra/Oriente Deadline** | August 15 |
| **Accrual Period** | 12 months prior |

```python
# Décimo 14 Proration
def compute_decimo_14(employee, region, sbu):
    months_worked = count_months(employee.hire_date, cutoff_date(region))
    return round((sbu / 12) * min(months_worked, 12), 2)
```

### 4.3 Payment Options
- **Mensualizado**: Paid monthly (1/12 of annual amount)
- **Acumulado**: Paid in lump sum by deadline
- Employee signs election form (`hr.employee.decimo_mode`)

---

## 5. FONDOS DE RESERVA

| Attribute | Value |
|:----------|:------|
| **Legal Basis** | CT Art. 196-200 |
| **Rate** | 8.33% of monthly salary |
| **Eligibility** | After 13 months of service |
| **Payment** | IESS transfer or mensualizado |

### 5.1 Computation
```python
# Fondos de Reserva
def compute_fondos_reserva(employee, wage):
    if tenure_months(employee) >= 13:
        return round(wage * 0.0833, 2)
    return 0.0
```

---

## 6. UTILIDADES (PROFIT SHARING)

### 6.1 Legal Framework
| Attribute | Value |
|:----------|:------|
| **Legal Basis** | CT Art. 97-100 |
| **Total Amount** | 15% of Net Profit |
| **Distribution** | 10% by days worked, 5% by family loads |
| **Payment Deadline** | April 15 |

### 6.2 Calculation Algorithm
```python
def distribute_utilidades(company, year):
    net_profit = company.annual_net_profit(year)
    if net_profit <= 0:
        return []

    total_15 = net_profit * 0.15
    pool_10 = total_15 * (10/15)  # Direct distribution
    pool_5 = total_15 * (5/15)    # Family loads

    total_days = sum(emp.worked_days(year) for emp in employees)
    total_loads = sum(emp.family_loads for emp in employees)

    distribution = []
    for emp in employees:
        share_10 = pool_10 * (emp.worked_days(year) / total_days)
        share_5 = pool_5 * (emp.family_loads / total_loads) if total_loads > 0 else 0
        distribution.append({
            'employee': emp,
            'amount': round(share_10 + share_5, 2)
        })
    return distribution
```

### 6.3 Maximum Per Employee
- Individual cap: 24× SBU ($11,568 in 2026)
- Excess distributed proportionally to others

---

## 7. VACACIONES

| Attribute | Value |
|:----------|:------|
| **Legal Basis** | CT Art. 69-72 |
| **First 5 Years** | 15 calendar days |
| **After 5 Years** | +1 day per year (max 30) |
| **Divisor** | (Monthly Salary ÷ 24) × Days |

### 7.1 Vacation Pay Formula
```python
def vacation_pay(employee, days_requested):
    monthly_salary = employee.contract_id.wage
    daily_rate = monthly_salary / 24  # CT Art. 71
    return round(daily_rate * days_requested, 2)
```

---

## 8. TERMINACIÓN DE CONTRATO (LIQUIDACIÓN)

### 8.1 Termination Types
| Type | Additional Benefits |
|:-----|:--------------------|
| Renuncia voluntaria | Proportional décimos only |
| Desahucio | +25% per year (CT Art. 185) |
| Despido intempestivo | +3 months (1yr), +1 month per year after |
| Visto bueno empleador | No indemnization |
| Visto bueno trabajador | +25% per year |

### 8.2 Liquidation Components
```python
def calculate_liquidation(employee, termination_type, date):
    components = {
        'salario_pendiente': pending_salary(employee, date),
        'decimo_13_proporcional': prorata_decimo_13(employee, date),
        'decimo_14_proporcional': prorata_decimo_14(employee, date),
        'vacaciones_no_gozadas': unused_vacation_pay(employee, date),
        'fondos_reserva': fondos_reserva_pending(employee, date),
    }

    if termination_type == 'desahucio':
        components['bonificacion_desahucio'] = desahucio_bonus(employee)
    elif termination_type == 'despido_intempestivo':
        components['indemnizacion'] = despido_indemnization(employee)

    return components

def despido_indemnization(employee):
    years = tenure_years(employee)
    wage = employee.contract_id.wage
    if years < 1:
        return wage * 3  # 3 months first year
    else:
        return (wage * 3) + (wage * (years - 1))  # +1 month per additional year
```

---

## 9. SUT COMPLIANCE

### 9.1 Sistema Único de Trabajo
| Action | Deadline | Penalty |
|:-------|:---------|:--------|
| Contract registration | 15 days after start | Fine |
| Termination notification | 15 days after end | Fine |
| Aviso de entrada (IESS) | 15 days after start | Back payment |
| Aviso de salida (IESS) | 3 days after end | Fine |

---

## 10. ODOO FIELD REFERENCE

### 10.1 Contract Model (hr.contract)
| Field | Type | Purpose |
|:------|:-----|:--------|
| `wage` | Float | Monthly salary |
| `struct_id` | Many2one | Salary structure |
| `l10n_ec_decimo_mode` | Selection | mensualizado/acumulado |
| `l10n_ec_fondos_mode` | Selection | iess/mensualizado |

### 10.2 Payslip Model (hr.payslip)
| Field | Type | Purpose |
|:------|:-----|:--------|
| `line_ids` | One2many | Salary rule results |
| `l10n_ec_net_receivable` | Float | Net to pay |
| `l10n_ec_iess_personal` | Float | Employee contribution |
| `l10n_ec_iess_patronal` | Float | Employer contribution |

---

## 11. AI AGENT COMMANDS

### 11.1 Payroll Queries
```
"Calculate pending décimo 13 for all employees"
"Show IESS liabilities for January 2026"
"Who is eligible for fondos de reserva?"
"What is total utilidades distribution for 2025?"
```

### 11.2 Contract Management
```
"List contracts expiring this month"
"Show employees not registered in SUT"
"Calculate liquidation for employee Juan Pérez"
```

### 11.3 Compliance Alerts
```
"Are all décimo 14 payments processed for Costa?"
"Show employees missing family load documentation"
"What is our utilidades liability for 2025?"
```

---

**Document Classification**: HR Executive Reference
**Legal Authority**: Código del Trabajo, Ley de Seguridad Social
**Last Verified**: 2026-01-22
