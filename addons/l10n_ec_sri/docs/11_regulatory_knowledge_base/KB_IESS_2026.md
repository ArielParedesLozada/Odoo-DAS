# IESS (SEGURIDAD SOCIAL) - COMPLETE REFERENCE 2026
## Aportes, Fondos de Reserva, Planillas

**Last Verified**: 2026-01-22
**Source**: iess.gob.ec, ecuadorlegalonline.com

---

## 1. CONTRIBUTION RATES 2026

### 1.1 Private Sector
| Contribution | Employee | Employer | Total |
|:-------------|:---------|:---------|:------|
| **Aporte Personal** | **9.45%** | - | 9.45% |
| **Aporte Patronal** | - | **11.15%** | 11.15% |
| **SECAP** | - | 0.5% | 0.5% |
| **IECE** | - | 0.5% | 0.5% |
| **TOTAL** | **9.45%** | **12.15%** | **21.60%** |

### 1.2 Public Sector
| Contribution | Employee | Employer |
|:-------------|:---------|:---------|
| **Aporte Personal** | **11.45%** | - |
| **Aporte Patronal** | - | **9.15%** |

### 1.3 Example Calculation (SBU $482)
| Concept | Amount |
|:--------|:-------|
| Employee contribution | $45.55 (9.45%) |
| Employer IESS | $53.74 (11.15%) |
| SECAP | $2.41 (0.5%) |
| IECE | $2.41 (0.5%) |
| **Total Employer** | **$58.56** |

---

## 2. CONTRIBUTION CEILING

| Year | SBU | Ceiling (25×SBU) |
|:-----|:----|:-----------------|
| 2025 | $470 | $11,750 |
| **2026** | **$482** | **$12,050** |

> Contributions are calculated on salary up to the ceiling. Any amount above $12,050/month is NOT subject to IESS.

---

## 3. FONDOS DE RESERVA

### 3.1 Parameters
| Attribute | Value |
|:----------|:------|
| Rate | **8.33%** of monthly salary |
| Eligibility | After **13 months** continuous service |
| Base | Same as IESS contributions |

### 3.2 Payment Options
| Option | Description |
|:-------|:------------|
| **Mensualizado (IESS)** | Paid monthly through IESS (default) |
| **Acumulado (Retenido)** | Retained by employer, paid at termination |

### 3.3 Employee Choice
- Default: Monthly via IESS
- Can request accumulation in writing

---

## 4. PLANILLA IESS (MONTHLY CONTRIBUTION FILE)

### 4.1 File Format
The employer generates a monthly file with:
| Field | Description |
|:------|:------------|
| RUC | Employer RUC |
| Cédula | Employee ID |
| Apellidos | Last names |
| Nombres | First names |
| Sueldo | Monthly salary |
| Días trabajados | Days worked |
| Aporte personal | 9.45% calculation |
| Aporte patronal | 11.15% calculation |

### 4.2 Submission Deadline
- By the **15th of the following month**
- Payment via banking system

### 4.3 Portal
- URL: empleadores.iess.gob.ec
- Requires: RUC and credentials

---

## 5. AVISO DE ENTRADA/SALIDA

### 5.1 Aviso de Entrada (New Hire)
| Attribute | Value |
|:----------|:------|
| Deadline | **15 days** after hire |
| Portal | empleadores.iess.gob.ec |
| Required | Cédula, hire date, salary |

### 5.2 Aviso de Salida (Termination)
| Attribute | Value |
|:----------|:------|
| Deadline | **3 days** after termination |
| Portal | empleadores.iess.gob.ec |
| Required | Termination date, reason |

---

## 6. PRÉSTAMOS IESS

### 6.1 Types
| Type | Description |
|:-----|:------------|
| **Quirografario** | Personal loan, up to 80 SBU |
| **Hipotecario** | Home loan |
| **Prendario** | Vehicle loan |

### 6.2 Deduction
- Employer deducts from payroll
- Remits to IESS with monthly contributions

---

## 7. JUBILACIÓN (RETIREMENT)

### 7.1 Requirements
| Type | Contributions | Age |
|:-----|:--------------|:----|
| Vejez | 480 months | 60+ years |
| Vejez anticipada | 480 months | 55+ years (reduced) |
| Invalidez | Variable | Any |

### 7.2 Calculation
Based on average of last 5 years of contributions.

---

## 8. AGENT CODE REFERENCE

```python
# IESS Parameters 2026
SBU_2026 = 482.00
IESS_CEILING = SBU_2026 * 25  # $12,050

# Private Sector Rates
IESS_PERSONAL_RATE = 0.0945  # 9.45%
IESS_PATRONAL_RATE = 0.1115  # 11.15%
SECAP_RATE = 0.005           # 0.5%
IECE_RATE = 0.005            # 0.5%
FONDOS_RESERVA_RATE = 0.0833 # 8.33%

# Eligibility
FONDOS_RESERVA_MONTHS = 13   # After 13 months

# Deadlines
AVISO_ENTRADA_DAYS = 15
AVISO_SALIDA_DAYS = 3

def calculate_iess_contributions(gross_salary: float) -> dict:
    """
    Calculate IESS contributions for a given gross salary.
    """
    base = min(gross_salary, IESS_CEILING)

    return {
        'base': base,
        'personal': round(base * IESS_PERSONAL_RATE, 2),
        'patronal': round(base * IESS_PATRONAL_RATE, 2),
        'secap': round(base * SECAP_RATE, 2),
        'iece': round(base * IECE_RATE, 2),
        'total_employer': round(base * (IESS_PATRONAL_RATE + SECAP_RATE + IECE_RATE), 2)
    }
```

---

**Classification**: Agent Knowledge Base - IESS
**Update**: On rate changes or SBU update
