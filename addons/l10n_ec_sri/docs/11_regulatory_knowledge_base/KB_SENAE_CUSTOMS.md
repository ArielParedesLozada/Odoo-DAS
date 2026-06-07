# REGULATORY KNOWLEDGE BASE: SENAE (CUSTOMS)
## Servicio Nacional de Aduana del Ecuador

**Source**: https://www.aduana.gob.ec
**Official Name**: Servicio Nacional de Aduana del Ecuador
**Last Verified**: 2026-01-22

---

## 1. AGENCY OVERVIEW

| Attribute | Value |
|:----------|:------|
| **Name** | Servicio Nacional de Aduana del Ecuador |
| **Acronym** | SENAE |
| **Role** | Customs control and trade facilitation |
| **Portal** | https://www.aduana.gob.ec |
| **Ecuapass** | https://ecuapass.aduana.gob.ec |

---

## 2. KEY SYSTEMS

### 2.1 ECUAPASS
Main customs declaration and processing system.

| Function | Description |
|:---------|:------------|
| Import declarations (DAI) | Declaración Aduanera de Importación |
| Export declarations (DAE) | Declaración Aduanera de Exportación |
| Transit permits | Régimen de tránsito |
| Temporary imports | Admisión temporal |

### 2.2 Ventanilla Única Ecuatoriana (VUE)
Single window for all import/export permits:
- ARCSA (health products)
- AGROCALIDAD (agricultural)
- INEN (technical standards)
- Other permits

### 2.3 Arancel Nacional (Customs Tariff)
| Resource | URL |
|:---------|:----|
| Tariff Query | https://mesadeservicios.aduana.gob.ec/arancel/ |
| HS Code Lookup | Available online |

---

## 3. IMPORT PROCESS

### 3.1 Import Taxes
| Tax | Calculation |
|:----|:------------|
| **Ad-Valorem** | CIF value × Tariff rate |
| **FODINFA** | CIF × 0.5% (child development fund) |
| **ICE** | Specific products (alcohol, tobacco, vehicles) |
| **IVA** | (CIF + Ad-valorem + FODINFA + ICE) × 15% |
| **ISD** | 5% on foreign payments >$5,000 |

### 3.2 CIF Value
```
CIF = Cost (FOB) + Insurance + Freight
```

### 3.3 Import Tax Formula
```python
def calculate_import_taxes(cif, tariff_rate, has_ice=False, ice_amount=0):
    ad_valorem = cif * tariff_rate
    fodinfa = cif * 0.005  # 0.5%
    ice = ice_amount if has_ice else 0
    taxable_base = cif + ad_valorem + fodinfa + ice
    iva = taxable_base * 0.15  # 15%
    return {
        'ad_valorem': ad_valorem,
        'fodinfa': fodinfa,
        'ice': ice,
        'iva': iva,
        'total': ad_valorem + fodinfa + ice + iva
    }
```

---

## 4. EXPORT PROCESS

### 4.1 Export Requirements
- DAE (Declaración Aduanera de Exportación)
- Commercial invoice
- Packing list
- Transport document (B/L, AWB)
- Phytosanitary certificate (if applicable)
- Certificate of origin (for trade agreements)

### 4.2 Export Incentives
| Incentive | Description |
|:----------|:------------|
| **Drawback** | Return of import duties on exported goods |
| **Temporary admission** | Duty-free import for export manufacturing |

---

## 5. AUTHORIZED ECONOMIC OPERATOR (OEA)

### 5.1 Benefits
- Expedited clearance
- Reduced inspections
- Priority treatment
- International recognition

### 5.2 Requirements
- Good compliance history
- Internal control systems
- Security measures
- Financial solvency

---

## 6. CUSTOMS REGIMES

| Regime | Description |
|:-------|:------------|
| **Importación a consumo** | Direct import for domestic use |
| **Admisión temporal** | Temporary import (manufacturing) |
| **Tránsito aduanero** | Transit through Ecuador |
| **Depósito aduanero** | Customs warehouse |
| **Reimportación** | Return of exported goods |
| **Exportación definitiva** | Final export |

---

## 7. DOCUMENTATION

### 7.1 Import Documents
| Document | Spanish Name |
|:---------|:-------------|
| DAI | Declaración Aduanera de Importación |
| Commercial Invoice | Factura Comercial |
| Packing List | Lista de Empaque |
| Bill of Lading | Conocimiento de Embarque |
| Air Waybill | Guía Aérea |
| Insurance Certificate | Certificado de Seguro |

### 7.2 Export Documents
| Document | Spanish Name |
|:---------|:-------------|
| DAE | Declaración Aduanera de Exportación |
| Certificado de Origen | Certificate of Origin |
| Fitosanitario | Phytosanitary Certificate |

---

## 8. PENALTIES

| Violation | Penalty |
|:----------|:--------|
| Undervaluation | 100% of evaded duties + fines |
| False documentation | Criminal prosecution |
| Contraband | Seizure + criminal charges |
| Late declaration | Fines per day |

---

## 9. SYSTEM IMPLEMENTATION NOTES

For `l10n_ec_customs` module:

1. **DAU Model**: Store import declaration data
2. **Tax Calculation**: Implement formula with all components
3. **HS Code Integration**: Link to arancel nacional
4. **Vendor Bill Integration**: Auto-create from DAU
5. **Landed Cost**: Include all import taxes in cost
6. **VUE Permits**: Track required permits per product

---

## 10. KEY RESOURCES

| Resource | URL |
|:---------|:----|
| **Main Portal** | https://www.aduana.gob.ec |
| **Ecuapass** | https://ecuapass.aduana.gob.ec |
| **Tariff Query** | https://mesadeservicios.aduana.gob.ec/arancel/ |
| **VUE** | Via Ecuapass |
| **SENAE Browser** | https://www.aduana.gob.ec/senae-browser-descargas/ |

---

**Knowledge Base Entry ID**: KB-SENAE-001
**Verification Status**: VERIFIED from official website
**Legal Authority**: Código Orgánico de la Producción (COPCI)
**Next Review Date**: 2026-07-01
