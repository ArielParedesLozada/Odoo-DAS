# SENAE (CUSTOMS) - COMPLETE REFERENCE 2026
## ECUAPASS, DAU, Importaciones, Aranceles

**Last Verified**: 2026-01-22
**Source**: aduana.gob.ec, trade.gov

---

## 1. OVERVIEW

**SENAE** (Servicio Nacional de Aduana del Ecuador) regulates:
- Import/Export operations
- Customs duties
- ECUAPASS platform
- DAU (Declaración Aduanera Única)

---

## 2. IMPORT TAXES

### 2.1 Standard Duties
| Tax | Rate | Base | Description |
|:----|:-----|:-----|:------------|
| **AD VALOREM** | 0-40% | CIF | Arancel según producto |
| **FODINFA** | 0.5% | CIF | Fondo desarrollo infancia |
| **ISD** | 5% | Payment | Impuesto salida divisas |
| **IVA Import** | 15% | CIF + AD + FODINFA | Standard IVA |
| **ICE Import** | Variable | If applicable | Consumos especiales |
| **Salvaguardia** | 5-45% | CIF | Temporary measures |

### 2.2 CIF Calculation
```
CIF = FOB + Freight + Insurance
```

### 2.3 Total Import Duty Calculation
```
Import Duty = AD VALOREM + FODINFA + IVA Import
IVA Import Base = CIF + AD VALOREM + FODINFA
```

---

## 3. TARIFFS AND RATES

> **LEGAL PRINCIPLE**: Only tariffs published in the **Registro Oficial** are enforceable.
> All AD VALOREM rates are defined in the **Arancel Nacional** by HS code.
> Consult SENAE's official tariff portal: https://mesadeservicios.aduana.gob.ec/arancel/

---

## 4. ECUAPASS SYSTEM

### 4.1 Overview
| Attribute | Value |
|:----------|:------|
| Portal | ecuapass.aduana.gob.ec |
| Purpose | All customs declarations |
| Requirement | Electronic signature (token) |

### 4.2 Registration Requirements
- RUC (Registro Único Contribuyentes)
- Electronic signature from BCE or authorized provider
- Bank account for duty payments

### 4.3 System Status (Jan 2026)
- Operating normally since Jan 11, 2026
- After optimization and monitoring actions

---

## 5. DAU (DECLARACIÓN ADUANERA ÚNICA)

### 5.1 Types
| Type | Code | Purpose |
|:-----|:-----|:--------|
| **DAI** | 10 | Import to consumption |
| **DAE** | 40 | Export |
| **DAU-R** | Various | Regimes |

### 5.2 Required Documents (Import)
| Document | Required |
|:---------|:---------|
| Commercial Invoice | ✅ |
| Bill of Lading / Air Waybill | ✅ |
| Insurance Policy | ✅ |
| Certificate of Origin | If applicable |
| INEN-1 Certificate | If applicable |
| Phytosanitary Certificate | If applicable |

---

## 6. CUSTOMS REGIMES

| Code | Regime | Description |
|:-----|:-------|:------------|
| 10 | **Consumo** | Import for domestic use |
| 20 | Depósito | Temporary storage |
| 21 | Reembarque | Re-shipment |
| 40 | **Exportación** | Export |
| 41 | Exportación temporal | Temporary export |
| 50 | Tránsito | Transit |
| 70 | Zonas Francas | Free zones |
| 72 | ZEDE | Special economic zones |

---

## 7. EXPORT PROCESS

### 7.1 Documents
| Document | Required |
|:---------|:---------|
| Export Invoice | ✅ |
| DAE (Declaración Aduanera Exportación) | ✅ |
| Packing List | ✅ |
| Transport Document | ✅ |

### 7.2 IVA Treatment
- Exports are **0% IVA**
- Can claim IVA refund on purchases

---

## 8. ARANCEL NACIONAL

### 8.1 Structure
Based on Harmonized System (HS):
- 10 digits in Ecuador
- First 6 = International
- Last 4 = National

### 8.2 Common Categories
| HS Chapter | Products | Typical Rate |
|:-----------|:---------|:-------------|
| 01-05 | Animals | 15-25% |
| 06-14 | Plants | 10-20% |
| 15-24 | Food | 20-30% |
| 25-38 | Chemicals | 0-15% |
| 50-63 | Textiles | 20-30% |
| 84-85 | Machinery | 5-15% |
| 87 | Vehicles | 35-40% |

---

## 9. AUTHORIZED ECONOMIC OPERATOR (OEA)

### 9.1 Benefits
- Faster customs clearance
- Reduced inspections
- Priority processing

### 9.2 Requirements
- Clean customs history
- Financial solvency
- Security certifications

---

## 10. ODOO IMPLEMENTATION

### 10.1 Import Model (`l10n_ec.import.dau`)
| Field | Type | Description |
|:------|:-----|:------------|
| dau_number | Char | DAU/DAI Number |
| customs_district | Selection | GUAYAQUIL, QUITO, etc. |
| regime | Selection | 10, 20, 40, etc. |
| cif_value | Monetary | CIF Value USD |
| fob_value | Monetary | FOB Value |
| freight | Monetary | Freight Cost |
| insurance | Monetary | Insurance Cost |
| ad_valorem | Monetary | Computed Tariff |
| fodinfa | Monetary | Computed 0.5% |
| isd | Monetary | Computed 5% |
| iva_import | Monetary | Computed 15% |

---

## 11. AGENT CODE REFERENCE

```python
# SENAE Parameters 2026
FODINFA_RATE = 0.005   # 0.5%
ISD_RATE = 0.05        # 5%
IVA_IMPORT_RATE = 0.15 # 15%

# NOTE: Country-specific tariffs require Registro Oficial publication
# Do NOT hard-code tariffs - use configurable parameters

def calculate_import_duties(
    fob: float,
    freight: float,
    insurance: float,
    ad_valorem_rate: float = 0.15
) -> dict:
    """
    Calculate total import duties
    """
    cif = fob + freight + insurance
    ad_valorem = cif * ad_valorem_rate
    fodinfa = cif * FODINFA_RATE

    iva_base = cif + ad_valorem + fodinfa
    iva_import = iva_base * IVA_IMPORT_RATE

    return {
        'cif': round(cif, 2),
        'ad_valorem': round(ad_valorem, 2),
        'fodinfa': round(fodinfa, 2),
        'iva_base': round(iva_base, 2),
        'iva_import': round(iva_import, 2),
        'total_duties': round(ad_valorem + fodinfa + iva_import, 2),
        'total_cost': round(cif + ad_valorem + fodinfa + iva_import, 2)
    }
```

---

**Classification**: Agent Knowledge Base - SENAE
**Update**: On tariff changes
