# ODOO 18.0 GAP ANALYSIS FOR ECUADOR LOCALIZATION
## What Odoo Provides vs What We Must Build

**Document ID**: SOMA-GAP-ODOO-001
**Date**: 2026-01-22

---

## 1. GAP MATRIX

### ACCOUNTING & FINANCE
| Requirement | Odoo Has? | Gap | Customization Level |
|:---|:---|:---|:---|
| NEC Chart of Accounts | Template System | Data Only | **LOW** |
| IVA 15%/5%/0% | Tax Framework | Data Only | **LOW** |
| ICE Taxes | Formula Taxes | Config | **LOW** |
| **Access Key 49-digit** | **NO** | **FULL** | **HIGH - NEW CODE** |
| **XAdES-BES Signing** | **NO** | **FULL** | **HIGH - NEW CODE** |
| **SRI SOAP Client** | **NO** | **FULL** | **HIGH - NEW CODE** |
| **Mod10/11 Validation** | **NO** | **FULL** | **MEDIUM - EXTENSION** |

### PURCHASING
| Requirement | Odoo Has? | Gap | Customization Level |
|:---|:---|:---|:---|
| Vendor Bills | Full | None | **NONE** |
| **Sustento Tributario** | **NO** | **FULL** | **MEDIUM - EXTENSION** |
| **Liquidación de Compra** | **NO** | **FULL** | **HIGH - NEW WORKFLOW** |
| **Withholding Document** | **NO** | **FULL** | **HIGH - NEW MODEL** |

### INVENTORY
| Requirement | Odoo Has? | Gap | Customization Level |
|:---|:---|:---|:---|
| Warehouse Mgmt | Full | None | **NONE** |
| Lot Tracking | Full | None | **NONE** |
| **Guía de Remisión** | **NO** | **FULL** | **HIGH - EXTENSION** |
| **Driver/Vehicle** | **NO** | **FULL** | **MEDIUM - NEW MODELS** |

### POINT OF SALE
| Requirement | Odoo Has? | Gap | Customization Level |
|:---|:---|:---|:---|
| POS Interface | Full | None | **NONE** |
| **Electronic Invoice** | **NO** | **FULL** | **HIGH - EXTENSION** |
| **$50 CF Limit** | **NO** | **FULL** | **MEDIUM - VALIDATION** |
| **Offline Queue** | **NO** | **FULL** | **HIGH - NEW MODEL** |

### PAYROLL (HR)
| Requirement | Odoo Has? | Gap | Customization Level |
|:---|:---|:---|:---|
| Payroll Engine | Full | None | **NONE** |
| Salary Rules | Full | None | **NONE** |
| **IESS 9.45%/12.15%** | **NO** | **FULL** | **MEDIUM - RULES** |
| **Décimo 13/14** | **NO** | **FULL** | **MEDIUM - RULES** |
| **Fondos Reserva** | **NO** | **FULL** | **MEDIUM - RULES** |
| **Liquidaciones** | **NO** | **FULL** | **HIGH - NEW MODEL** |

### CUSTOMS (SENAE)
| Requirement | Odoo Has? | Gap | Customization Level |
|:---|:---|:---|:---|
| **DAU Document** | **NO** | **FULL** | **HIGH - NEW MODEL** |
| **Tariff Codes** | **NO** | **FULL** | **MEDIUM - NEW MODEL** |
| **ISD 5%** | **NO** | **FULL** | **MEDIUM - LOGIC** |

### REPORTING
| Requirement | Odoo Has? | Gap | Customization Level |
|:---|:---|:---|:---|
| Financial Reports | Full | None | **NONE** |
| **ATS XML** | **NO** | **FULL** | **HIGH - NEW WIZARD** |
| **Form 103/104** | **NO** | **FULL** | **MEDIUM - REPORTS** |

---

## 2. EFFORT SUMMARY

| Level | Count | Description |
|:---|:---|:---|
| **NONE** | 8 | Use standard Odoo |
| **LOW** | 5 | Data files only |
| **MEDIUM** | 12 | Field extensions, rules |
| **HIGH** | 14 | New models, complex code |

**Total Custom Development Items**: 31
