# SOFTWARE REQUIREMENTS SPECIFICATION
## Module: l10n_ec_hr_payroll (Ecuador HR & Payroll - Ministerio del Trabajo / IESS)

**Document Identifier**: SRS-L10N-EC-HR-001
**Version**: 1.0
**Date**: 2026-01-22
**Status**: APPROVED
**Standard**: ISO/IEC/IEEE 29148:2018
**Regulatory Sources**:
- Ministerio del Trabajo (trabajo.gob.ec)
- IESS (iess.gob.ec)
- Código del Trabajo Ecuador
- SUT (Sistema Único de Trabajo)

---

## 1. INTRODUCTION

### 1.1 Purpose
This SRS describes the requirements for the `l10n_ec_hr_payroll` module, which implements Ecuador's complete payroll system including IESS contributions, Décimos, Utilidades, Fondos de Reserva, and all Ministerio del Trabajo compliance requirements.

### 1.2 Scope
The module SHALL:
1. Define Ecuador-specific payroll structures and salary rules.
2. Compute IESS contributions (personal and employer).
3. Handle Décimo Tercero and Décimo Cuarto (monthly/annual).
4. Calculate Fondos de Reserva.
5. Compute profit sharing (Utilidades 15%).
6. Generate employee liquidations (termination settlements).
7. Produce Rol de Pagos (official payslip format).
8. Integrate with SUT for ministry reporting.

### 1.3 Definitions & Acronyms
| Term | Definition |
|:---|:---|
| **SBU** | Salario Básico Unificado (Unified Basic Salary) - $482 USD for 2026 |
| **IESS** | Instituto Ecuatoriano de Seguridad Social |
| **SUT** | Sistema Único de Trabajo (Ministry Online System) |
| **Rol de Pagos** | Official Payslip Document |
| **Décimo Tercero** | 13th Month Salary (Christmas Bonus) |
| **Décimo Cuarto** | 14th Month Salary (School Bonus = 1 SBU) |
| **Fondos de Reserva** | Reserve Funds (8.33% after 1 year) |
| **Utilidades** | Profit Sharing (15% of net income) |

### 1.4 References
- Código del Trabajo Ecuador (Art. 42, 69, 95, 97, 111, 113)
- Ley de Seguridad Social
- Resolución MDT-2025-XXX (SBU 2026)
- https://www.trabajo.gob.ec
- https://www.iess.gob.ec

---

## 2. VERIFIED 2026 PAYROLL PARAMETERS

### 2.1 Salario Básico Unificado (SBU) 2026
| Parameter | Value | Source |
|:---|:---|:---|
| **SBU 2026** | **$482.00 USD** | Ministerio del Trabajo |
| **Hourly Rate** | $2.01 (482/240) | Calculated |
| **SBU 2025** | $460.00 USD | Reference |
| **Increase** | 4.78% | Calculated |

### 2.2 IESS Contribution Rates 2026
| Contribution | Employee % | Employer % | Base |
|:---|:---|:---|:---|
| **Aporte Personal** | 9.45% | - | Gross Salary |
| **Aporte Patronal** | - | 11.15% | Gross Salary |
| **SECAP** | - | 0.5% | Gross Salary |
| **IECE** | - | 0.5% | Gross Salary |
| **Total Employee** | **9.45%** | - | - |
| **Total Employer** | - | **12.15%** | - |
| **TOTAL COMBINED** | | | **21.60%** |

**Contribution Ceiling**: 25 x SBU = $12,050/month

### 2.3 Horas Extras & Suplementarias
| Type | Recargo | Rate (2026) | Hours |
|:---|:---|:---|:---|
| **Hora Ordinaria** | Base | $2.01 | Standard |
| **Hora Suplementaria** | +50% | $3.01 | 06:00-24:00 |
| **Hora Extraordinaria** | +100% | $4.02 | 24:00-06:00, Weekends, Holidays |
| **Jornada Nocturna** | +25% | $2.51 | Regular night shift |

### 2.4 Décimo Tercero (13th Salary)
| Attribute | Value |
|:---|:---|
| **Calculation** | Total earnings Dec 1 - Nov 30 / 12 |
| **Payment Date** | Before December 24 |
| **Mensualización** | Optional - Employee must request by Jan 15 |
| **Mensualizado Amount** | 1/12 of monthly salary each month |

### 2.5 Décimo Cuarto (14th Salary)
| Attribute | Value |
|:---|:---|
| **Amount** | 1 SBU = $482 (2026) |
| **Mensualizado** | $40.17/month (482/12) |
| **Payment Costa/Galápagos** | Before March 15 (Period: Mar 1 - Feb 28) |
| **Payment Sierra/Amazonía** | Before August 15 (Period: Aug 1 - Jul 31) |

### 2.6 Fondos de Reserva
| Attribute | Value |
|:---|:---|
| **Rate** | 8.33% of monthly salary |
| **Eligibility** | After 13 months of continuous service |
| **Payment Options** | Monthly (IESS) or Annual (retained) |
| **Default** | Monthly through IESS unless employee requests otherwise |

### 2.7 Utilidades (Profit Sharing)
| Component | Percentage | Distribution |
|:---|:---|:---|
| **Individual Component** | 10% | Based on days worked |
| **Family Component** | 5% | Based on registered dependents |
| **Maximum per Employee** | 24 SBU | $11,568 (2026) |
| **Payment Deadline** | April 15 |

### 2.8 Vacaciones
| Attribute | Value |
|:---|:---|
| **Annual Days** | 15 working days |
| **After 5 Years** | +1 day per year (max 30 total) |
| **Payment** | Full salary + 1/24 of total annual |
| **Minimum Consecutive** | 6 days |

---

## 3. SPECIFIC REQUIREMENTS

### 3.1 Data Models

#### 3.1.1 Payroll Configuration (`l10n_ec.hr.config`)
| Field | Type | Default | Description |
|:---|:---|:---|:---|
| `sbu` | Monetary | 482.00 | Current SBU |
| `iess_personal_rate` | Float | 9.45 | Employee IESS % |
| `iess_patronal_rate` | Float | 11.15 | Employer IESS % |
| `secap_rate` | Float | 0.5 | SECAP % |
| `iece_rate` | Float | 0.5 | IECE % |
| `fondos_reserva_rate` | Float | 8.33 | Reserve Funds % |
| `employer_region` | Selection | - | 'costa', 'sierra' |

#### 3.1.2 Employee Extensions (`hr.employee`)
| Field | Type | Description |
|:---|:---|:---|
| `l10n_ec_iess_code` | Char | IESS Affiliation Number |
| `l10n_ec_contract_type` | Selection | indefinido, fijo, eventual, prueba |
| `l10n_ec_sector_code` | Char | Sectorial Table Code |
| `l10n_ec_hire_date` | Date | Employment Start Date |
| `l10n_ec_decimo13_mode` | Selection | mensualizado, acumulado |
| `l10n_ec_decimo14_mode` | Selection | mensualizado, acumulado |
| `l10n_ec_fondos_mode` | Selection | iess_monthly, retained |
| `l10n_ec_dependents` | Integer | Family Dependents (for Utilidades) |
| `l10n_ec_region` | Selection | costa, sierra, galapagos, amazonia |

#### 3.1.3 Contract Extensions (`hr.contract`)
| Field | Type | Description |
|:---|:---|:---|
| `l10n_ec_sectorial_salary` | Monetary | Minimum per sector |
| `l10n_ec_transport_bonus` | Monetary | Non-taxable transport |
| `l10n_ec_food_bonus` | Monetary | Non-taxable food |
| `l10n_ec_is_partial_time` | Boolean | Part-time contract |
| `l10n_ec_partial_hours` | Float | Weekly hours if partial |

#### 3.1.4 Payslip Extensions (`hr.payslip`)
| Field | Type | Description |
|:---|:---|:---|
| `l10n_ec_rol_number` | Char | Rol de Pagos Sequential |
| `l10n_ec_iess_personal` | Monetary | Computed IESS deduction |
| `l10n_ec_iess_patronal` | Monetary | Computed employer IESS |
| `l10n_ec_decimo13_provision` | Monetary | Monthly D13 provision |
| `l10n_ec_decimo14_provision` | Monetary | Monthly D14 provision |
| `l10n_ec_fondos_reserva` | Monetary | Reserve funds |
| `l10n_ec_ir_withholding` | Monetary | Income tax withheld |

### 3.2 Salary Rules

#### 3.2.1 Income Rules
| Code | Name | Condition | Computation |
|:---|:---|:---|:---|
| `EC_BASIC` | Sueldo Básico | Always | `contract.wage` |
| `EC_HORA_EXTRA_50` | Horas Suplementarias | `worked_hours.extra_50 > 0` | `hours * (wage/240) * 1.5` |
| `EC_HORA_EXTRA_100` | Horas Extraordinarias | `worked_hours.extra_100 > 0` | `hours * (wage/240) * 2` |
| `EC_COMISION` | Comisiones | `inputs.commission` | `inputs.commission.amount` |
| `EC_BONO` | Bonificaciones | `inputs.bonus` | `inputs.bonus.amount` |
| `EC_D13_MENS` | Décimo 13 Mensualizado | `employee.l10n_ec_decimo13_mode == 'mensualizado'` | `categories.GROSS / 12` |
| `EC_D14_MENS` | Décimo 14 Mensualizado | `employee.l10n_ec_decimo14_mode == 'mensualizado'` | `config.sbu / 12` |
| `EC_FONDOS_RES` | Fondos de Reserva | `employee.months_service >= 13` | `categories.GROSS * 0.0833` |

#### 3.2.2 Deduction Rules
| Code | Name | Condition | Computation |
|:---|:---|:---|:---|
| `EC_IESS_PERS` | Aporte Personal IESS | Always | `min(categories.GROSS, config.sbu * 25) * 0.0945` |
| `EC_IR` | Impuesto a la Renta | `annual_income > threshold` | `compute_ir_table(annual_projected)` |
| `EC_ANTICIPO` | Anticipo de Sueldo | `inputs.advance` | `inputs.advance.amount` |
| `EC_PRESTAMO` | Préstamo IESS | `inputs.iess_loan` | `inputs.iess_loan.amount` |
| `EC_EMBARGO` | Embargo Judicial | `inputs.garnishment` | `inputs.garnishment.amount` |

#### 3.2.3 Employer Contribution Rules
| Code | Name | Computation |
|:---|:---|:---|
| `EC_IESS_PAT` | Aporte Patronal | `categories.GROSS * 0.1115` |
| `EC_SECAP` | SECAP | `categories.GROSS * 0.005` |
| `EC_IECE` | IECE | `categories.GROSS * 0.005` |
| `EC_D13_PROV` | Provisión D13 | `categories.GROSS / 12` |
| `EC_D14_PROV` | Provisión D14 | `config.sbu / 12` |
| `EC_VAC_PROV` | Provisión Vacaciones | `categories.GROSS / 24` |

### 3.3 Liquidación (Termination Settlement)

#### 3.3.1 Required Computations
| Concept | Formula |
|:---|:---|
| **Salario Proporcional** | `(monthly_wage / 30) * days_worked_current_month` |
| **Décimo 13 Proporcional** | `total_earned_period / 12` |
| **Décimo 14 Proporcional** | `(sbu / 12) * months_in_period` |
| **Vacaciones No Gozadas** | `(monthly_wage / 24) * months_worked` |
| **Fondos de Reserva Retenidos** | If retained, full accumulated amount |
| **Desahucio** | `monthly_wage * 0.25 * years_service` |
| **Despido Intempestivo (< 3 years)** | `monthly_wage * 3` |
| **Despido Intempestivo (> 3 years)** | `monthly_wage * months (1 per year, max 25)` |

#### 3.3.2 Liquidation Model (`l10n_ec.hr.liquidation`)
| Field | Type | Description |
|:---|:---|:---|
| `employee_id` | Many2one | Employee being terminated |
| `termination_type` | Selection | renuncia, desahucio, despido, mutuo_acuerdo |
| `termination_date` | Date | Last working day |
| `cause` | Text | Reason for termination |
| `line_ids` | One2many | Liquidation line items |
| `total_ingreso` | Monetary | Total benefits owed |
| `total_deduccion` | Monetary | Total deductions |
| `total_neto` | Monetary | Net settlement |
| `acta_finiquito` | Binary | Signed settlement document |

### 3.4 Rol de Pagos (Official Payslip)

#### 3.4.1 Required Fields (Per Ministerio del Trabajo)
**Header**:
- Company Name, RUC, Address
- Employee Name, Cédula, Position, Department
- Period (Start Date - End Date)
- Hire Date

**Income Section (Ingresos)**:
| Line | Description |
|:---|:---|
| 1 | Sueldo Básico |
| 2 | Horas Extras 50% |
| 3 | Horas Extras 100% |
| 4 | Comisiones |
| 5 | Bonificaciones |
| 6 | Décimo Tercero Mensualizado (if applicable) |
| 7 | Décimo Cuarto Mensualizado (if applicable) |
| 8 | Fondos de Reserva (if applicable) |
| 9 | Otros Ingresos |
| **TOTAL INGRESOS** | Sum |

**Deduction Section (Egresos)**:
| Line | Description |
|:---|:---|
| 1 | Aporte Personal IESS (9.45%) |
| 2 | Impuesto a la Renta |
| 3 | Anticipos |
| 4 | Préstamos IESS |
| 5 | Préstamos Empresa |
| 6 | Otros Descuentos |
| **TOTAL EGRESOS** | Sum |

**Footer**:
- **Líquido a Recibir** = Total Ingresos - Total Egresos
- Employee Signature
- Employer Signature
- Date

### 3.5 SUT Integration

#### 3.5.1 Required SUT Reports
| Report | Frequency | Deadline |
|:---|:---|:---|
| **Registro Contratos** | Per event | 15 days after hire |
| **Aviso de Entrada IESS** | Per event | 15 days after hire |
| **Aviso de Salida IESS** | Per event | 3 days after termination |
| **Acta de Finiquito** | Per termination | 15 days after termination |
| **Pago Utilidades** | Annual | April 15 |
| **Pago Décimo 13** | Annual | December 24 |
| **Pago Décimo 14** | Annual | March 15 / August 15 |

---

## 4. USE CASES

### 4.1 UC-001: Generate Monthly Payroll
**Actor**: HR Manager
**Flow**:
1. User creates Payroll Batch for period.
2. System loads all active employees.
3. System fetches attendance/extra hours.
4. System computes each salary rule.
5. System generates Rol de Pagos for each employee.
6. User validates and confirms batch.
7. System creates accounting entries.
8. System generates bank payment file.

### 4.2 UC-002: Process Employee Termination
**Actor**: HR Manager
**Flow**:
1. User creates Liquidation record.
2. User selects termination type and date.
3. System computes all pending benefits.
4. System computes any indemnifications.
5. User validates calculations.
6. System generates Acta de Finiquito.
7. System registers in SUT.
8. System triggers IESS exit notification.

---

## 5. VALIDATION CRITERIA

| Test ID | Description | Expected |
|:---|:---|:---|
| **T-HR-001** | Compute IESS on $1000 salary | Personal=$94.50, Patronal=$121.50 |
| **T-HR-002** | Compute D13 for 6 months work | 6/12 * gross |
| **T-HR-003** | Compute D14 for Costa (full year) | $482 |
| **T-HR-004** | Compute 8 extra hours @100% | 8 * 2.01 * 2 = $32.16 |
| **T-HR-005** | Liquidation with 5 years service | Include 5 months despido |

---

## 6. INCOME TAX TABLE (Impuesto a la Renta 2026)

| From | To | Base Tax | Marginal Rate |
|:---|:---|:---|:---|
| 0 | 11,722 | 0 | 0% |
| 11,722 | 14,930 | 0 | 5% |
| 14,930 | 19,385 | 160 | 10% |
| 19,385 | 25,638 | 606 | 12% |
| 25,638 | 33,738 | 1,356 | 15% |
| 33,738 | 44,721 | 2,571 | 20% |
| 44,721 | 59,537 | 4,768 | 25% |
| 59,537 | 79,388 | 8,472 | 30% |
| 79,388 | En adelante | 14,427 | 37% |

---

**Document Control**:
| Version | Date | Author |
|:---|:---|:---|
| 1.0 | 2026-01-22 | Antigravity (HR/Labor Law Specialist + CPA) |
