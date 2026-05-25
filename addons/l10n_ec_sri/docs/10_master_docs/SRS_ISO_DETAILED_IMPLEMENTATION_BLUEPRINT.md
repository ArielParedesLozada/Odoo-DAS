# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)
## SYSTEM: Odoo 18.0 Ecuador Full Localization Suite

**Document ID**: SOMA-SRS-EC-FULL-001
**Date**: 2026-01-22
**Version**: 2.0 (FINAL DETAILED)
**Standard**: ISO/IEC 29148:2018
**Classification**: CONFIDENTIAL / TECHNICAL BLUEPRINT

---

## 1. INTRODUCTION

### 1.1 Purpose
This document provides the atomic implementation details for the Odoo 18.0 Ecuadorian Localization. It dictates the exact **Models**, **Fields**, **Views**, and **Algorithms** required to satisfy the `SOMA-LEGAL-AUDIT-2026`.

### 1.2 Scope
The system is composed of three (3) distinct Odoo Modules:
1.  **`l10n_ec_sri`**: The Core Sovereign Module (Fiscal Engine).
2.  **`l10n_ec_reports`**: The Compliance Reporting Module (ATS/Tax Forms).
3.  **`l10n_ec_sri_saas`**: The Multi-Tenant Configuration Module.

---

## 2. MODULE 1: `l10n_ec_sri` (CORE IMPLEMENTATION)

### 2.1 Data Models (Structural Logic)

#### 2.1.1 Partner Extensions (`res.partner`)
**REQ-MOD-001**: Extend `res.partner` with the following columns:
| Technical Name | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `l10n_ec_identifier_type` | Selection | Yes | `cedula` | `['ruc', 'cedula', 'pasaporte']` |
| `l10n_ec_related_party` | Boolean | No | `False` | Used for ATS Reporting |
| `l10n_ec_legal_rep` | Boolean | No | `False` | Is Legal Representative? |
| `l10n_ec_rimpe_regime` | Selection | No | `None` | `['popular', 'emprendedor', 'general']` |
| `l10n_ec_forced_accounting`| Boolean | No | `False` | Obligado a llevar contabilidad |

#### 2.1.2 SRI Credentials (`l10n_ec.sri.credentials`)
**REQ-MOD-002**: Create new model `l10n_ec.sri.credentials` to store signing keys securely.
| Technical Name | Type | Description |
| :--- | :--- | :--- |
| `company_id` | Many2one | Link to `res.company` |
| `p12_certificate` | Binary | The `.p12` file (Stored Encrypted) |
| `p12_password` | Char | Password (Widget: `password`) |
| `environment` | Selection | `['test', 'prod']` |
| `sequence_emission` | Integer | Next Invoice Number (e.g. 1045) |

#### 2.1.3 Document Mixin (`l10n_ec.sri.mixin`)
**REQ-MOD-003**: Abstract Model to be inherited by `account.move`.
| Technical Name | Type | Description |
| :--- | :--- | :--- |
| `l10n_ec_authorization_state`| Selection | `['draft', 'signed', 'sent', 'authorized', 'rejected']` |
| `l10n_ec_access_key` | Char (49) | The SRI Access Key |
| `l10n_ec_authorization_date`| Datetime | Timestamp from SRI Response |
| `l10n_ec_xml_file` | Binary | The final Authorized XML |
| `l10n_ec_sri_error` | Text | Error Traceback from Middleware |

#### 2.1.4 Withholding Model (`account.retention`)
**REQ-MOD-004**: New Model for handling "Comprobantes de Retención".
| Technical Name | Type | Relations |
| :--- | :--- | :--- |
| `invoice_id` | Many2one | `account.move` (The Bill being withheld) |
| `tax_lines` | One2many | `account.retention.line` |
| `fiscal_year` | Char | Derived from Date |

### 2.2 Algorithms (Business Logic)

#### 2.2.1 Identity Validation (Mod 10/11)
**REQ-ALG-001**: Implement `validate_identifier(string)`:
1.  **Length Check**:
    *   RUC: 13 digits.
    *   Cedula: 10 digits.
2.  **Province Check**: First 2 digits must be `01-24` or `30`.
3.  **Third Digit Check**:
    *   `< 6`: Natural Person (Modulo 10).
    *   `= 6`: Public Entity (Modulo 11).
    *   `= 9`: Private Juridical (Modulo 11).
4.  **Checksum**: Calculate last digit based on weighted sum.

#### 2.2.2 Access Key Generation
**REQ-ALG-002**: Implement `generate_access_key(values)`:
*   **Format**: `[Date(8)][Type(2)][RUC(13)][Env(1)][Estab(3)][Emission(3)][Seq(9)][Code(8)][Type(1)][Check(1)]`
*   **Check Digit**: Use Modulo 11 (Weighted 2-7).
*   **Constraint**: Must be exactly 49 digits numeric.

#### 2.2.3 Electronic Signing (XAdES-BES)
**REQ-ALG-003**: Implement `sign_xml(xml_content, p12, password)`:
1.  **Library**: Use `xmlsec` (Python bindings) or `cryptography`.
2.  **Canonicalization**: `C14N`.
3.  **Digest**: SHA-1 or SHA-256 (SRI Configurable).
4.  **Structure**:
    *   `<ds:Signature>`
    *   `<ds:SignedInfo>`
    *   `<ds:KeyInfo>` (Include X509 Certificate)
    *   `<ds:Object>` (Qualifying Properties - "Firmado por Odoo")

### 2.3 User Interface (Views)

#### 2.3.1 Invoice Form (`account_move_form_inherit`)
**REQ-UI-001**: Inject Notebook Page "SRI Ecuador":
*   Display `Access Key` (Readonly).
*   Display `Authorization Status` (Badge Widget).
*   Button `Send to SRI` (Visible if Not Authorized).
*   Button `Download XML`.

#### 2.3.2 Consumidor Final Blocking
**REQ-UI-002**: On `action_post()`:
```python
if partner.vat == '9999999999999' and amount_total > 50.00:
    raise UserError("UAFE LIMIT EXCEEDED: Please identify client.")
```

---

## 3. MODULE 2: `l10n_ec_reports` (COMPLIANCE)

### 3.1 ATS Reporting (`ats_wizard`)
**REQ-RPT-001**: Generate `ATS.xml` following `ficha_tecnica_ats_v2.xsd`.
*   **Iterate**: All `account.move` where `state='posted'`.
*   **Group By**: Partner (Compras / Ventas).
*   **Aggregate**: Base Imponible 0%, Base 15%, Monto IVA, Retenciones.

### 3.2 Formulario 103 (Retenciones)
**REQ-RPT-002**: Pivot View of `account.retention.line`.
*   **Rows**: Tax Code (312, 320, etc.).
*   **Columns**: Month.
*   **Values**: Sum of Base, Sum of Tax.

---

## 4. MODULE 3: `l10n_ec_sri_saas` (MULTI-TENANT CONFIG)

### 4.1 Onboarding Wizard (`l10n_ec.onboarding`)
**REQ-SAAS-001**: Wizard Steps:
1.  **Upload Logo/RUC**: Auto-fill Company Data.
2.  **Select Regime**: "RIMPE" / "General" / "Special".
3.  **Load Certificate**: Upload P12.

### 4.2 Auto-Configurator
**REQ-SAAS-002**: On Wizard Finish:
1.  Set `account.fiscal.position` defaults based on Regime.
2.  Generate `ir.sequence` for Invoices (001-001).
3.  Install Chart of Accounts (NEC).

---

## 5. TECHNICAL CONSTRAINTS
**REQ-TEC-001**: No Java Dependencies.
**REQ-TEC-002**: No Binary Executables.
**REQ-TEC-003**: 100% Odoo 18.0 API Compliance.

---

## 6. VALIDATION CRITERIA
1.  **XML Validation**: All XMLs must pass `xmllint --schema` against SRI XSDs.
2.  **UAFE Test**: Try to invoice $51 to Consumidor Final -> MUST FAIL.
3.  **RIMPE Test**: Validate Invoice from RIMPE Popular -> MUST HAVE 0% IVA.

**Authorized By:**
*Antigravity (System Architect)*
