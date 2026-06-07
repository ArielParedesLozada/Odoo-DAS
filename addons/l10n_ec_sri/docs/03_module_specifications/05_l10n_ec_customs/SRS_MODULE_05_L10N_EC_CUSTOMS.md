# SOFTWARE REQUIREMENTS SPECIFICATION
## Module: l10n_ec_customs (Ecuador SENAE Customs Integration)

**Document Identifier**: SRS-L10N-EC-CUSTOMS-001
**Version**: 1.0
**Date**: 2026-01-22
**Status**: APPROVED
**Standard**: ISO/IEC/IEEE 29148:2018

---

## 1. INTRODUCTION

### 1.1 Purpose
This SRS describes the requirements for the `l10n_ec_customs` module, which implements customs clearance workflows, import tax computation (Ad Valorem, FODINFA, ISD), and SENAE document management.

### 1.2 Scope
The module SHALL:
1. Define customs document model (DAU/DAI).
2. Compute import taxes automatically.
3. Track export documents and IVA recovery.
4. Integrate with vendor bills for landed cost.

### 1.3 Definitions
| Term | Definition |
|:---|:---|
| **SENAE** | Servicio Nacional de Aduana del Ecuador |
| **DAU** | Declaración Aduanera Única (Import) |
| **DAE** | Declaración Aduanera de Exportación |
| **CIF** | Cost + Insurance + Freight (Customs Value) |
| **FOB** | Free On Board (Product Value) |
| **Ad Valorem** | Percentage tariff on CIF value |
| **FODINFA** | 0.5% development fund tax |
| **ISD** | Impuesto a la Salida de Divisas (5%) |

### 1.4 References
- SENAE Resolución SENAE-DGN-2020-0001-RE
- Código Orgánico de la Producción, Comercio e Inversiones
- Arancel Nacional de Importaciones (Tariff Book)

---

## 2. OVERALL DESCRIPTION

### 2.1 Product Perspective
This module bridges Odoo's Purchase and Inventory modules with Ecuador's customs requirements. It ensures all import costs are correctly capitalized and taxes documented.

### 2.2 Product Functions
1. **F-CUS-001**: Import Declaration (DAU) Management
2. **F-CUS-002**: Tariff Code Assignment to Products
3. **F-CUS-003**: Import Tax Computation
4. **F-CUS-004**: Export Documentation
5. **F-CUS-005**: ISD Tax on Foreign Payments

### 2.3 Constraints
- All imports MUST have a valid DAU number.
- Tariff codes MUST match SENAE's official schedule.
- ISD is applied on ALL foreign payments (not just imports).

---

## 3. EXTERNAL INTERFACE REQUIREMENTS

### 3.1 User Interfaces
| Screen | Location |
|:---|:---|
| **Tariff Code Configuration** | Inventory > Configuration > Tariff Codes |
| **DAU Form** | Purchase > Customs > Import Declarations |
| **Product Form** | Extended with tariff_code field |

---

## 4. SPECIFIC REQUIREMENTS

### 4.1 Functional Requirements

#### 4.1.1 Import Declaration Model (F-CUS-001)
**REQ-F-001.1**: Model `l10n_ec.customs.declaration`:
| Field | Type | Description |
|:---|:---|:---|
| `name` | Char | DAU Number (e.g., 055-2026-10-000123-4) |
| `declaration_type` | Selection | `import`, `export` |
| `date` | Date | Customs clearance date |
| `customs_district` | Selection | GUAYAQUIL, QUITO, MANTA, etc. |
| `regime` | Selection | 10 (Consumption), 20 (Warehouse), 70 (Re-export) |
| `fob_value` | Monetary | FOB value (USD) |
| `freight` | Monetary | Freight cost |
| `insurance` | Monetary | Insurance cost |
| `cif_value` | Monetary | Computed: FOB + Freight + Insurance |
| `ad_valorem_rate` | Float | Tariff percentage |
| `ad_valorem_amount` | Monetary | Computed: CIF * rate |
| `fodinfa_amount` | Monetary | Computed: CIF * 0.5% |
| `iva_import` | Monetary | Computed: (CIF + AdValorem + Fodinfa) * 15% |
| `isd_amount` | Monetary | Computed from payment |
| `total_taxes` | Monetary | Sum of all taxes |
| `purchase_order_id` | Many2one | Link to PO |
| `invoice_ids` | Many2many | Customs broker invoices |

#### 4.1.2 Tariff Code Model (F-CUS-002)
**REQ-F-002.1**: Model `l10n_ec.tariff.code`:
| Field | Type | Description |
|:---|:---|:---|
| `code` | Char | 10-digit HS Code |
| `name` | Char | Description |
| `ad_valorem` | Float | Standard tariff % |
| `unit` | Char | Unit of measure |
| `ice_applicable` | Boolean | Subject to ICE? |
| `antidumping` | Float | Additional duty (if any) |

**REQ-F-002.2**: Extend `product.template`:
| Field | Type |
|:---|:---|
| `l10n_ec_tariff_code_id` | Many2one |

#### 4.1.3 Import Tax Computation (F-CUS-003)
**REQ-F-003.1**: On DAU save, compute:
```python
@api.depends('cif_value', 'ad_valorem_rate')
def _compute_taxes(self):
    for rec in self:
        rec.ad_valorem_amount = rec.cif_value * rec.ad_valorem_rate / 100
        rec.fodinfa_amount = rec.cif_value * 0.005  # 0.5%
        taxable_base = rec.cif_value + rec.ad_valorem_amount + rec.fodinfa_amount
        rec.iva_import = taxable_base * 0.15  # 15% IVA
        rec.total_taxes = (rec.ad_valorem_amount + rec.fodinfa_amount +
                          rec.iva_import + rec.isd_amount)
```

#### 4.1.4 ISD Tax on Payments (F-CUS-005)
**REQ-F-005.1**: Extend `account.payment`:
| Field | Type | Description |
|:---|:---|:---|
| `l10n_ec_is_foreign` | Boolean | Payment to foreign entity? |
| `l10n_ec_isd_amount` | Monetary | Computed: amount * 5% |

**REQ-F-005.2**: ISD Computation:
```python
@api.depends('amount', 'partner_id.country_id')
def _compute_isd(self):
    for payment in self:
        if payment.partner_id.country_id.code != 'EC':
            payment.l10n_ec_isd_amount = payment.amount * 0.05
        else:
            payment.l10n_ec_isd_amount = 0
```

#### 4.1.5 Export Documentation (F-CUS-004)
**REQ-F-004.1**: Export invoices SHALL:
- Have `l10n_ec_is_export = True`
- Apply Fiscal Position "Exportación" (IVA 0%)
- Store DAE number in `l10n_ec_dae_number`

**REQ-F-004.2**: Link export invoice to DAE for IVA recovery:
| Field | Type |
|:---|:---|
| `l10n_ec_dae_number` | Char |
| `l10n_ec_dae_date` | Date |

---

## 5. USE CASES

### 5.1 UC-001: Register Import with Taxes
**Actor**: Accountant
**Flow**:
1. User receives goods from international supplier.
2. User creates DAU record with CIF values.
3. System auto-computes Ad Valorem, FODINFA, IVA Import.
4. User links DAU to Vendor Bill.
5. System posts journal entries for customs taxes.
**Postcondition**: Landed cost correctly capitalized.

### 5.2 UC-002: ISD on Foreign Payment
**Actor**: Accountant
**Flow**:
1. User creates payment to foreign supplier.
2. System detects foreign country.
3. System computes 5% ISD.
4. User confirms payment.
5. System creates ISD tax liability entry.
**Postcondition**: ISD recorded for monthly declaration.

---

## 6. VALIDATION CRITERIA

| Test ID | Description | Expected |
|:---|:---|:---|
| **T-CUS-001** | Create DAU with CIF = $10,000, tariff 20% | AdValorem = $2,000 |
| **T-CUS-002** | Compute FODINFA | $50 (0.5%) |
| **T-CUS-003** | Compute IVA Import | $1,807.50 |
| **T-CUS-004** | Payment $1,000 to USA | ISD = $50 |

---

**Document Control**:
| Version | Date | Author |
|:---|:---|:---|
| 1.0 | 2026-01-22 | Antigravity (World's #1 Odoo Expert + SENAE Specialist) |
