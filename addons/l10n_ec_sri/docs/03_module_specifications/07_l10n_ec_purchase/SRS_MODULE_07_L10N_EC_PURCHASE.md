# SOFTWARE REQUIREMENTS SPECIFICATION
## Module: l10n_ec_purchase (Ecuador Purchase Compliance)

**Document Identifier**: SRS-L10N-EC-PURCHASE-001
**Version**: 1.0
**Date**: 2026-01-22
**Status**: APPROVED
**Standard**: ISO/IEC/IEEE 29148:2018

---

## 1. INTRODUCTION

### 1.1 Purpose
This SRS describes the requirements for the `l10n_ec_purchase` module, which implements Ecuador-specific purchasing compliance including Liquidación de Compra, Sustento Tributario, and Reembolso de Gastos.

### 1.2 Scope
The module SHALL:
1. Enable Liquidación de Compra for purchases from non-RUC suppliers.
2. Require Sustento Tributario selection on vendor bills.
3. Handle Reembolso de Gastos (expense reimbursement documents).
4. Validate document references per SRI requirements.

### 1.3 Definitions
| Term | Definition |
|:---|:---|
| **Liquidación de Compra** | Invoice issued by buyer when vendor has no RUC |
| **Sustento Tributario** | Tax support code determining deductibility |
| **Reembolso** | Expense reimbursement from intermediary |

### 1.4 Legal References
- Código Tributario Art. 96
- LORTI Art. 10 (Deductible Expenses)
- SRI Resolución NAC-DGERCGC16-00000092

---

## 2. EXPERT CREW PERSPECTIVES

### 2.1 CFO Perspective (María Finanzas)
> "Sustento Tributario directly affects our tax deductions. If we select the wrong code, we lose the tax credit. The system MUST guide users to select correctly."

### 2.2 Legal Counsel Perspective (Elena Derecho)
> "Liquidación de Compra has strict requirements. The buyer assumes full witholding responsibility (100% IVA, variable Renta). We need to document why we're using this document type."

### 2.3 Compliance Officer Perspective (Sofía Cumplimiento)
> "Every purchase document must have proper sustento. Without it, we fail ATS validation and face SRI penalties."

---

## 3. SPECIFIC REQUIREMENTS

### 3.1 Sustento Tributario Model (`l10n_ec.sustento`)
| Code | Name | IVA Credit | Renta Deductible | Use Case |
|:---|:---|:---|:---|:---|
| 01 | Crédito Tributario IVA | 100% | YES | Standard local purchase |
| 02 | Costo o Gasto | 0% | YES | Import, no IVA credit |
| 03 | Activo Fijo | 100% | Depreciated | Fixed asset purchase |
| 04 | Sin Derecho Crédito | 0% | NO | Personal expense |
| 05 | Proporcionalidad | Partial | YES | Mixed-use purchases |
| 06 | Reembolso | N/A | YES | Intermediary reimbursement |
| 07 | Partes Relacionadas | 100% | YES | Intercompany |
| 08 | Importación Servicios | Calculate | YES | Foreign service import |
| 09 | Retenciones Presuntivas | 100% | YES | Presumptive withholding |
| 10 | Extraterritorial | 0% | NO | Foreign purchase |

### 3.2 Vendor Bill Extensions (`account.move`)
| Field | Type | Required | Validation |
|:---|:---|:---|:---|
| `l10n_ec_sustento_id` | Many2one | Yes (purchases) | Must match document type |
| `l10n_ec_is_liquidacion` | Boolean | - | Triggers special workflow |
| `l10n_ec_is_reembolso` | Boolean | - | Triggers reimbursement lines |
| `l10n_ec_auth_number` | Char | Yes | 10, 37, or 49 digits |
| `l10n_ec_doc_type_vendor` | Selection | Yes | 01-07 validated |

### 3.3 Liquidación de Compra Workflow
**REQ-LIQ-001**: When `l10n_ec_is_liquidacion = True`:
1. Vendor must have `l10n_ec_identifier_type = 'cedula'` or `'pasaporte'`.
2. System auto-generates document as `account.move` with `l10n_latam_document_type = '03'`.
3. System applies 100% IVA withholding automatically.
4. System applies Renta withholding based on product category.
5. Buyer signs and transmits XML to SRI.

**REQ-LIQ-002**: Liquidación valid scenarios:
- Purchase from rural producer (agricultural products)
- Purchase from artisan without RUC
- Purchase from foreign resident without establishment

### 3.4 Reembolso de Gastos
**REQ-REEM-001**: Model `l10n_ec.reembolso.line`:
| Field | Type | Description |
|:---|:---|:---|
| `move_id` | Many2one | Parent vendor bill |
| `original_doc_type` | Selection | Type of original document |
| `original_doc_number` | Char | Original document number |
| `original_provider_vat` | Char | Original provider RUC |
| `original_provider_name` | Char | Original provider name |
| `original_date` | Date | Original document date |
| `subtotal_0` | Monetary | Subtotal IVA 0% |
| `subtotal_15` | Monetary | Subtotal IVA 15% |
| `iva` | Monetary | IVA amount |
| `total` | Monetary | Total reimbursed |

### 3.5 Document Authorization Validation
**REQ-AUTH-001**: The `l10n_ec_auth_number` field SHALL validate:
| Length | Type | Validation |
|:---|:---|:---|
| 10 | Physical Document | Numeric, valid date range |
| 37 | Online Authorization | Specific format |
| 49 | Offline Access Key | Mod11 check digit |

### 3.6 Sustento-Document Type Matrix
| Document Type | Valid Sustentos |
|:---|:---|
| 01 - Factura | 01, 02, 03, 04, 05, 07 |
| 03 - Liquidación | 01, 02, 03 |
| 04 - Nota Crédito | Same as original |
| 05 - Nota Débito | Same as original |
| 41 - Reembolso | 06 |

---

## 4. USE CASES

### 4.1 UC-001: Register Local Purchase with Tax Credit
**Actor**: Accounts Payable Clerk
**Flow**:
1. User creates Vendor Bill.
2. User enters vendor (with RUC).
3. User selects Sustento = "01 - Crédito Tributario".
4. System allows 100% IVA credit.
5. User validates and posts.

### 4.2 UC-002: Generate Liquidación de Compra
**Actor**: Accounts Payable Clerk
**Flow**:
1. User creates Vendor Bill.
2. User selects vendor (with Cédula, no RUC).
3. System auto-sets `l10n_ec_is_liquidacion = True`.
4. System auto-selects Sustento = "01".
5. System computes 100% IVA withholding.
6. User validates.
7. System generates XML, signs, transmits to SRI.
8. Vendor receives authorized Liquidación.

---

## 5. VALIDATION CRITERIA

| Test ID | Description | Expected |
|:---|:---|:---|
| **T-PUR-001** | Select Sustento 01 for Factura | IVA credit = 100% |
| **T-PUR-002** | Select Sustento 02 for Factura | IVA credit = 0% |
| **T-PUR-003** | Create Liquidación for Cédula vendor | Auto-withhold 100% IVA |
| **T-PUR-004** | Reembolso with multiple lines | All lines in XML |
| **T-PUR-005** | Invalid auth number length | Validation error |

---

**Document Control**:
| Version | Date | Author |
|:---|:---|:---|
| 1.0 | 2026-01-22 | Expert Crew (CFO, Legal, Compliance) |
