# REGULATORY KNOWLEDGE BASE: IESS CONTRIBUTIONS
## Social Security Rates and Requirements

**Source**: Ley de Seguridad Social, IESS.gob.ec
**Last Verified**: 2026-01-22
**Status**: REQUIRES ADDITIONAL VERIFICATION (IESS website structure changed)

---

## 1. CONTRIBUTION RATES (STANDARD)

> **IMPORTANT**: These rates should be verified against current IESS publications.
> The rates below are based on established Ley de Seguridad Social provisions.

### 1.1 Employee Contribution (Aporte Personal)
| Concept | Rate |
|:--------|:-----|
| **Total Personal Contribution** | **9.45%** |

### 1.2 Employer Contribution (Aporte Patronal)
| Concept | Rate |
|:--------|:-----|
| Seguro de Invalidez, Vejez y Muerte | 3.10% |
| Seguro de Salud | 5.71% |
| Seguro de Riesgos del Trabajo | 0.55% |
| Seguro de Cesantía | 2.00% |
| IECE (Educación) | 0.50% |
| SECAP (Capacitación) | 0.50% |
| **Gastos Administración** | Variable |
| **Total Patronal** | **~12.15%** |

### 1.3 Combined Total
| Component | Rate |
|:----------|:-----|
| Employee | 9.45% |
| Employer | 12.15% |
| **Total to IESS** | **21.60%** |

---

## 2. CONTRIBUTION CEILING

| Year | Maximum Contributable Income |
|:-----|:----------------------------|
| 2026 | 25 × SBU = 25 × $482 = **$12,050/month** |

Contributions are calculated on salary up to this ceiling.

---

## 3. FONDOS DE RESERVA

| Attribute | Value |
|:----------|:------|
| **Rate** | 8.33% of monthly salary |
| **Eligibility** | After 13 months of continuous service |
| **Payment Options** | Via IESS or mensualizado (monthly) |
| **Legal Basis** | Código del Trabajo Art. 196-200 |

---

## 4. EMPLOYER OBLIGATIONS

### 4.1 Registration Deadlines
| Action | Deadline | Penalty |
|:-------|:---------|:--------|
| Employee Entry (Aviso de Entrada) | 15 days from start | Fine + back payment |
| Employee Exit (Aviso de Salida) | 3 days from termination | Fine |
| Monthly Contribution (Planilla) | Last day of month | Interest + penalties |

### 4.2 Planilla Components
The monthly IESS planilla includes:
- Aporte personal (employee contribution)
- Aporte patronal (employer contribution)
- Fondos de reserva (if applicable)
- Préstamos quirografarios (loan deductions)
- Préstamos hipotecarios (mortgage deductions)

---

## 5. VERIFICATION LINKS

| Resource | URL |
|:---------|:----|
| IESS Employer Portal | https://www.iess.gob.ec/es/web/guest/empleador |
| IESS Normativa | https://www.iess.gob.ec/normativa/ |
| IESS Formularios | https://www.iess.gob.ec/es/web/guest/formularios2 |
| IESS Statistics | https://www.iess.gob.ec/es/estadisticas |

---

## 6. SPECIAL REGIMES

### 6.1 Domestic Workers (Empleados del Hogar)
- Full IESS coverage required
- Same contribution rates apply
- Employer cannot deduct from minimum wage if at SBU

### 6.2 Artisans
- Reduced contribution structure
- Special regime with IESS

### 6.3 Voluntary Affiliation (Afiliación Voluntaria)
- Available for independent workers
- Different contribution structure

---

## 7. SYSTEM IMPLEMENTATION NOTES

For `l10n_ec_hr_payroll` module:

1. **Rate Constants**: Store as configurable parameters
2. **Ceiling Calculation**: Implement 25×SBU maximum
3. **Fondos de Reserva**: Track 13-month eligibility
4. **Planilla Generation**: Monthly IESS file export
5. **Aviso de Entrada/Salida**: Integration with SUT considered

---

## 8. ACTION REQUIRED

**Before production deployment**, verify current rates at:
- IESS official website
- Ley de Seguridad Social (current version)
- Recent Consejo Directivo IESS resolutions

---

**Knowledge Base Entry ID**: KB-IESS-001
**Verification Status**: PARTIALLY VERIFIED - rates consistent with Ley de Seguridad Social
**Legal Authority**: Ley de Seguridad Social, Art. 73-87
**Next Review Date**: 2026-02-01 (requires IESS portal verification)
