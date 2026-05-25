# REGULATORY KNOWLEDGE BASE - INDEX
## Ecuador ERP Implementation - Official Sources 2026

**Last Updated**: 2026-01-22
**Total Files**: 19
**For Use By**: AI Agents and Development Teams

---

## MASTER DOCUMENTS

| File | Description | Verified |
|:-----|:------------|:---------|
| [KB_MASTER_REGULATORY_2026.md](./KB_MASTER_REGULATORY_2026.md) | **COMPLETE 2026 regulatory overview - ALL AGENCIES** | ✅ Jan 2026 |

---

## BY REGULATORY AGENCY

### SRI (Servicio de Rentas Internas)
| File | Description |
|:-----|:------------|
| [KB_SRI_EINVOICING_2026.md](./KB_SRI_EINVOICING_2026.md) | Electronic invoicing 2026 changes, XML, endpoints |
| [KB_SRI_ELECTRONIC_INVOICING.md](./KB_SRI_ELECTRONIC_INVOICING.md) | Base e-invoicing reference |
| [KB_TAX_RATES_WITHHOLDINGS.md](./KB_TAX_RATES_WITHHOLDINGS.md) | IVA, IR rates, withholding codes |

### IESS (Seguridad Social)
| File | Description |
|:-----|:------------|
| [KB_IESS_2026.md](./KB_IESS_2026.md) | **Complete 2026 contribution rates** |
| [KB_IESS_CONTRIBUTIONS.md](./KB_IESS_CONTRIBUTIONS.md) | Base contribution reference |

### MINISTERIO DEL TRABAJO
| File | Description |
|:-----|:------------|
| [KB_MINISTERIO_TRABAJO_2026.md](./KB_MINISTERIO_TRABAJO_2026.md) | **Complete 2026 labor regulations** |
| [KB_MINTRABAJO_SUT.md](./KB_MINTRABAJO_SUT.md) | SUT system reference |
| [KB_LABOR_SBU_DECIMOS.md](./KB_LABOR_SBU_DECIMOS.md) | SBU, Décimo 13/14 |
| [KB_LABOR_FONDOS_RESERVA.md](./KB_LABOR_FONDOS_RESERVA.md) | Fondos de Reserva |
| [KB_LABOR_UTILIDADES.md](./KB_LABOR_UTILIDADES.md) | Profit sharing 15% |
| [KB_LABOR_TERMINATION.md](./KB_LABOR_TERMINATION.md) | Liquidation calculations |

### SUPERCIAS (Superintendencia de Compañías)
| File | Description |
|:-----|:------------|
| [KB_SUPERCIAS_2026.md](./KB_SUPERCIAS_2026.md) | **Complete 2026 financial statement requirements** |
| [KB_SUPERCIAS.md](./KB_SUPERCIAS.md) | Base reference |

### SENAE (Aduana)
| File | Description |
|:-----|:------------|
| [KB_SENAE_2026.md](./KB_SENAE_2026.md) | **Complete 2026 customs with new tariffs** |
| [KB_SENAE_CUSTOMS.md](./KB_SENAE_CUSTOMS.md) | Base customs reference |

### COMPETITIVE ANALYSIS
| File | Description |
|:-----|:------------|
| [KB_COMPETITIVE_BENCHMARK.md](./KB_COMPETITIVE_BENCHMARK.md) | Ecuador ERP market analysis |
| [FEATURE_REQUIREMENTS_COMPETITIVE.md](./FEATURE_REQUIREMENTS_COMPETITIVE.md) | Feature requirements |

---

## KEY 2026 VALUES (QUICK REFERENCE)

```python
# === CRITICAL 2026 VALUES ===

# SBU (Ministerio del Trabajo)
SBU_2026 = 482.00  # USD

# IVA (SRI)
IVA_RATE = 0.15  # 15%

# IESS Contributions
IESS_PERSONAL = 0.0945  # 9.45%
IESS_PATRONAL = 0.1115  # 11.15%
IESS_CEILING = SBU_2026 * 25  # $12,050

# Fondos de Reserva
FONDOS_RESERVA = 0.0833  # 8.33%

# Décimos
DECIMO_13_DEADLINE = "2026-12-24"
DECIMO_14_COSTA = "2026-03-15"
DECIMO_14_SIERRA = "2026-08-15"

# Utilidades
UTILIDADES_RATE = 0.15  # 15%
UTILIDADES_DEADLINE = "2026-04-15"

# SRI E-Invoicing
CONSUMIDOR_FINAL_LIMIT = 50.00  # USD
SRI_TRANSMISSION = "REAL-TIME"  # 2026 mandate

# SENAE Standard Rates (Official Law)
FODINFA = 0.005  # 0.5%
ISD = 0.05  # 5%
# NOTE: Other tariffs vary by HS code - check Arancel Nacional
```

---

## VERIFICATION STATUS

| Agency | Status | Last Verified | Next Review |
|:-------|:-------|:--------------|:------------|
| **SRI** | ✅ Current | 2026-01-22 | 2026-06-01 |
| **IESS** | ✅ Current | 2026-01-22 | 2026-06-01 |
| **Min. Trabajo** | ✅ Current | 2026-01-22 | 2027-01-01 |
| **Supercias** | ✅ Current | 2026-01-22 | 2026-04-30 |
| **SENAE** | ✅ Current | 2026-01-22 | 2026-03-01 |

---

## AGENT USAGE INSTRUCTIONS

1. **Start with KB_MASTER_REGULATORY_2026.md** for overview
2. Reference specific agency files for detailed rules
3. Use code snippets directly in Odoo modules
4. Update this index when regulations change

---

**Classification**: Agent Knowledge Base Index
**Maintainer**: Development Team
