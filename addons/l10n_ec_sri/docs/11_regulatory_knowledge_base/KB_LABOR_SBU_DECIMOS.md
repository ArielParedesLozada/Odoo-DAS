# REGULATORY KNOWLEDGE BASE: LABOR LAW - SBU & DÉCIMOS
## Verified from ecuadorlegalonline.com - January 2026

**Sources**:
- https://www.ecuadorlegalonline.com/laboral/salario-basico-unificado/
- https://www.ecuadorlegalonline.com/laboral/decimo-tercer-sueldo/
- https://www.ecuadorlegalonline.com/laboral/decimo-cuarto-sueldo/

**Last Verified**: 2026-01-22

---

## 1. SALARIO BÁSICO UNIFICADO (SBU) 2026

| Year | Amount | Effective Date | Legal Basis |
|:-----|:-------|:---------------|:------------|
| 2026 | **$482.00 USD** | January 1, 2026 | Acuerdo Ministerial |
| 2025 | $460.00 USD | January 1, 2025 | Acuerdo Ministerial |
| 2024 | $450.00 USD | January 1, 2024 | Acuerdo Ministerial |

### 1.1 Sectors Covered by SBU
- Pequeña industria
- Agricultura
- Maquila
- Empleados del hogar (domestic workers)
- Operarios de artesanía
- Colaboradores de microempresas

### 1.2 SBU Implications for 2026
- **Décimo Cuarto Sueldo**: $482.00
- **Multas laborales**: Calculated based on SBU
- **Pensiones alimenticias**: Reference table updated
- **IESS contributions**: Calculated on SBU floor
- **Partial-time workers**: Proportional to hours worked

---

## 2. DÉCIMO TERCER SUELDO (CHRISTMAS BONUS)

### 2.1 Key Information
| Attribute | Value |
|:----------|:------|
| **Legal Basis** | Código del Trabajo |
| **Calculation Period** | December 1 (prior year) to November 30 (current year) |
| **Payment Deadline** | **December 24** |
| **Formula** | (Sum of all earnings in period) ÷ 12 |

### 2.2 Earnings Included in Calculation
- Remuneración básica (base salary)
- Horas extras (overtime)
- Comisiones (commissions)
- Otras retribuciones accesorias permanentes (other permanent payments)

### 2.3 Payment Options
1. **Acumulado**: Full amount paid in December
2. **Mensualizado**: 1/12 paid monthly throughout the year

### 2.4 Option Change Deadline
- **January 15** of each year to submit preference change

---

## 3. DÉCIMO CUARTO SUELDO (SCHOOL BONUS)

### 3.1 Key Information
| Attribute | Value |
|:----------|:------|
| **Legal Basis** | Código del Trabajo, Art. 113, 114, 115 |
| **Amount** | 1 SBU = **$482.00 (2026)** |
| **Costa/Galápagos Deadline** | **March 15** |
| **Sierra/Amazonía Deadline** | **August 15** |

### 3.2 Calculation Periods
| Region | Period Start | Period End |
|:-------|:-------------|:-----------|
| **Costa & Galápagos** | March 1 (prior year) | February 29/28 (payment year) |
| **Sierra & Amazonía** | August 1 (prior year) | July 31 (payment year) |

### 3.3 Payment Options
1. **Acumulado**: Full SBU paid on deadline date
2. **Mensualizado**: $482 ÷ 12 = **$40.17/month** (2026)

### 3.4 Calculation Formula
For partial periods:
```
Décimo 14 = (SBU ÷ 360) × Days Worked
```

### 3.5 Partial Time Workers
For workers with less than 8 hours daily:
```
= (Days in period × SBU × (Weekly Hours × 4)) ÷ 360
```

### 3.6 Exclusions
Per **Art. 115 Código del Trabajo**:
- Operarios de artesanos (artisan workers)
- Aprendices de artesanos (artisan apprentices)

---

## 4. COMPUTATION EXAMPLES

### 4.1 Décimo 13 - Full Year Worker
```
Monthly earnings Jan-Nov: $800/month
Total = $800 × 12 = $9,600
Décimo 13 = $9,600 ÷ 12 = $800.00
```

### 4.2 Décimo 13 - Partial Year (5 months)
```
Earnings for 5 months = $4,000
Décimo 13 = $4,000 ÷ 12 = $333.33
```

### 4.3 Décimo 14 - Full Year Worker
```
Décimo 14 = 1 SBU = $482.00
```

### 4.4 Décimo 14 - Partial Year (150 days worked)
```
Décimo 14 = ($482 ÷ 360) × 150 = $200.83
```

---

## 5. SYSTEM IMPLEMENTATION NOTES

For `l10n_ec_hr_payroll` module:

1. **SBU Constant**: Store as system parameter, update annually
2. **Décimo 13 Period**: December 1 to November 30
3. **Décimo 14 Period**: Regional logic required (Costa vs Sierra)
4. **Acumulado/Mensualizado**: Employee preference field required
5. **Deadline Validation**: Alert before payment deadlines
6. **Proportional Calculation**: For partial-year workers

---

**Knowledge Base Entry ID**: KB-LABOR-001
**Verification Status**: VERIFIED from legal reference source
**Legal Authority**: Código del Trabajo Art. 95-97, 113-115
**Next Review Date**: 2027-01-01 (after SBU announced)
