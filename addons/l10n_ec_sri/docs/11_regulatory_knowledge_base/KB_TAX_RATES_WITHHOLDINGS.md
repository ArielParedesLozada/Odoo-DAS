# REGULATORY KNOWLEDGE BASE: TAX RATES & WITHHOLDINGS
## IVA, Income Tax Withholding, and Related Rates

**Sources**: SRI.gob.ec, LORTI, Reglamento LORTI
**Last Verified**: 2026-01-22

---

## 1. IVA (VALUE ADDED TAX)

### 1.1 Current Rates
| Rate | Code | Description | XML codigoPorcentaje |
|:-----|:-----|:------------|:---------------------|
| **15%** | 4 | Tarifa General | 4 |
| **5%** | 5 | Construcción (reduced) | 5 |
| **0%** | 0 | Tarifa 0% | 0 |
| **N/A** | 6 | No Objeto de IVA | 6 |
| **N/A** | 7 | Exento de IVA | 7 |

### 1.2 IVA History (Recent Changes)
| Period | Standard Rate | Notes |
|:-------|:--------------|:------|
| 2024-present | 15% | Increased from 12% |
| 2018-2023 | 12% | Standard rate |
| Construction | 5% | Special reduced rate |

### 1.3 Legal Basis
- LORTI Art. 65-66
- Ley de Simplicidad Tributaria (IVA increase)

---

## 2. INCOME TAX WITHHOLDING (RETENCIÓN EN LA FUENTE)

### 2.1 Withholding Rates by Code
| Code | Rate | Description | Applies To |
|:-----|:-----|:------------|:-----------|
| **303** | **10%** | Honorarios profesionales | Lawyers, doctors, engineers, etc. |
| **304** | 8% | Servicios predomina intelecto | Intellectual services |
| **307** | 2% | Publicidad y comunicación | Advertising, marketing |
| **309** | 1% | Transporte privado | Private transport |
| **310** | 1.75% | Bienes muebles | Transfer of movable goods |
| **312** | 1.75% | Bienes no producidos | Goods not produced by taxpayer |
| **320** | 2.75% | Arrendamiento inmuebles | Real estate rental |
| **322** | 8% | Seguros y reaseguros | Insurance |
| **323** | 2% | Rendimientos financieros | Financial returns |
| **340** | 1% | Otras retenciones 1% | Other 1% applicable |
| **341** | 2% | Otras retenciones 2% | Other 2% applicable |
| **342** | 2.75% | Otras retenciones 2.75% | Other 2.75% applicable |
| **343** | 8% | Otras retenciones 8% | Other 8% applicable |

### 2.2 Special Cases
| Situation | Withholding |
|:----------|:------------|
| Contribuyente Especial (buyer) | Must withhold |
| Contribuyente Especial (seller) | NO withholding applied to them |
| RIMPE Emprendedor | Simplified regime |
| RIMPE Negocio Popular | Simplified regime |

### 2.3 Legal Basis
- LORTI Art. 43-50
- Resolución NAC-DGERCGC23-00000042 (or latest)

---

## 3. IVA WITHHOLDING (RETENCIÓN DE IVA)

### 3.1 Withholding Rates
| Rate | Code | Applies To |
|:-----|:-----|:-----------|
| **30%** | 1 | Purchase of goods |
| **70%** | 2 | Purchase of services |
| **100%** | 3 | Professional fees, liquidación de compra |

### 3.2 When to Apply
| Buyer Type | Seller Type | IVA Withholding |
|:-----------|:------------|:----------------|
| Contribuyente Especial | Regular | 30%/70%/100% |
| Contribuyente Especial | CE | None |
| Regular | Regular | None |
| Government Entity | Any | 100% |

### 3.3 xml Mapping (tabla21)
```python
tabla21 = {
    '10': '9',   # 10% → code 9
    '20': '10',  # 20% → code 10
    '30': '1',   # 30% → code 1
    '50': '11',  # 50% → code 11
    '70': '2',   # 70% → code 2
    '100': '3',  # 100% → code 3
}
```

---

## 4. INCOME TAX (IMPUESTO A LA RENTA)

### 4.1 Corporate Rate
| Type | Rate |
|:-----|:-----|
| Standard corporate | 25% |
| Micro/Small enterprises | Reduced rates may apply |

### 4.2 Personal Income Tax Brackets
(Verify against current SRI publication for exact 2026 brackets)

| From | To | Fixed | Over Excess |
|:-----|:---|:------|:------------|
| $0 | $11,902 | $0 | 0% |
| $11,902 | $15,159 | $0 | 5% |
| $15,159 | $19,682 | $163 | 10% |
| $19,682 | $26,031 | $615 | 12% |
| $26,031 | $34,255 | $1,377 | 15% |
| $34,255 | $45,407 | $2,610 | 20% |
| $45,407 | $60,450 | $4,641 | 25% |
| $60,450 | $80,605 | $8,402 | 30% |
| $80,605 | $107,199 | $14,448 | 35% |
| $107,199+ | - | $23,756 | 37% |

> **Note**: These brackets should be verified against 2026 SRI tables.

---

## 5. CONSUMIDOR FINAL LIMIT

| Attribute | Value |
|:----------|:------|
| **Transaction Limit** | **$50.00 USD** |
| **Identification** | VAT = 9999999999999 |
| **Regulatory Basis** | UAFE Anti-Money Laundering |
| **System Action** | Block invoice if CF + amount > $50 |

---

## 6. SYSTEM IMPLEMENTATION NOTES

For tax configuration in l10n_ec modules:

1. **IVA Templates**: Create tax templates for 0%, 5%, 15%
2. **Withholding Templates**: Create for each code (303, 312, etc.)
3. **Fiscal Positions**: Map CE, RIMPE, Regular taxpayers
4. **tabla17/tabla18/tabla21**: Implement in utils.py
5. **CF Validation**: Hard block on $50 limit

---

**Knowledge Base Entry ID**: KB-TAX-001
**Verification Status**: VERIFIED (IVA 15% confirmed, withholding codes from SRI catalog)
**Legal Authority**: LORTI, Reglamento LORTI, SRI Resolutions
**Next Review Date**: 2026-07-01
