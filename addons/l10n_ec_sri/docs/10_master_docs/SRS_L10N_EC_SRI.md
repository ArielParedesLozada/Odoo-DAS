# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)
## Module: `l10n_ec_sri` (Ecuadorian Core Localization)

**Document ID**: SRS-L10N-EC-SRI-001
**Date**: 2026-01-22
**Version**: 1.0 (Odoo 18.0)
**Compliance**: ISO/IEC 29148:2018
**Author**: Antigravity (SomaTech Architect Persona)

---

## 1. INTRODUCTION

### 1.1 Purpose
This document specifies the software requirements for the `l10n_ec_sri` module, designed to provide full fiscal compliance for companies operating in Ecuador using Odoo 18.0. It supersedes all legacy documentation/logic found in `odoo-ecuador` v10.

### 1.2 Scope
The module encapsulates:
1.  **Identity Management**: Validation of RUC, Cedula, Pasaporte.
2.  **Fiscal Configuration**: Chart of Accounts, Taxes (15% etc), Fiscal Positions.
3.  **Electronic Invoicing (Facturación Electrónica)**: Generation, Signing, Transmission (SRI).
4.  **Withholding Taxes (Retenciones)**: Issuance and Reception.
5.  **Legal Protections**: UAFE limits ($50), RIMPE regimes.

---

## 2. FUNCTIONAL REQUIREMENTS

### 2.1 Component: Identity & Partner (`res.partner`)
**REQ-ID-01**: The system MUST validate the `vat` (RUC/CI) field using the Modulo 10 and Modulo 11 algorithms defined in `SOMA-REV-ENG-001`.
**REQ-ID-02**: The `res.partner` model MUST include a field `l10n_ec_sri_regime` (Selection) to support "RIMPE - Negocio Popular", "RIMPE - Emprendedor", and "General".
**REQ-ID-03**: The system MUST prevent proper invoicing to "Consumidor Final" (9999999999999) if the total amount exceeds $50.00 USD (UAFE Mandate).

### 2.2 Component: Fiscal Structure (`account.tax`, `account.account`)
**REQ-FIS-01**: The module MUST install a Chart of Accounts compliant with the **NEC** (Normas Ecuatorianas de Contabilidad).
**REQ-FIS-02**: The module MUST provision Tax Groups and Taxes for:
    *   **IVA 15%** (Code 4).
    *   **IVA 5%** (Construction Materials).
    *   **IVA 0%**.
    *   **IVA Exento**.
    *   **ICE** (Consumo Especial).
    *   **IRBPNR** (Plastic Bottles).
**REQ-FIS-03**: Tax Codes for ATS (Formulario 104) MUST be mapped to these taxes.

### 2.3 Component: Electronic Documents (`account.move`)
**REQ-DOC-01**: `account.move` MUST be extended to include Mixin `l10n_ec.sri.mixin`.
**REQ-DOC-02**: The Mixin MUST provide fields:
    *   `l10n_ec_access_key` (Char 49, Compute/Stored).
    *   `l10n_ec_auth_number` (Char).
    *   `l10n_ec_auth_date` (Datetime).
    *   `l10n_ec_xml_content` (Binary - Attachment).
**REQ-DOC-03**: The Access Key MUST be generated using the algorithm defined in `SOMA-REV-ENG-001` (Section 3.2).
**REQ-DOC-04**: The system MUST support the following SRI Document Types:
    *   01: Factura
    *   03: Liquidación de Compra
    *   04: Nota de Crédito
    *   05: Nota de Débito
    *   06: Guía de Remisión
    *   07: Comprobante de Retención

### 2.4 Component: Withholding (`account.retention`)
**REQ-RET-01**: The system MUST allow issuing Withholdings against Supplier Invoices (`in_invoice`).
**REQ-RET-02**: The system MUST validate that the Withholding Date is within **5 days** of the Invoice Date.
**REQ-RET-03**: The Withholding sequence MUST be 15 digits (001-001-000000001).
**REQ-RET-04**: Calculated amounts MUST follow the `sri.retention.concept` percentages (1%, 1.75%, 2.75%, 8%, 10% etc).

### 2.5 Component: EDI Engine (Signing & Transport)
**REQ-EDI-01**: The system MUST sign XML documents using **XAdES-BES** standard (Level 3 or 4).
**REQ-EDI-02**: Signing MUST be performed natively in Python using `lxml` and `cryptography` (No Java).
**REQ-EDI-03**: Certification File (.p12) MUST be stored partially encrypted or secured via Odoo's keychain.
**REQ-EDI-04**: Transmission MUST use the `zeep` library to communicate with `cel.sri.gob.ec` (Online) and `celcer.sri.gob.ec` (Test).
**REQ-EDI-05**: The system MUST implement a "Retry" mechanism for SRI timeouts (Offline mode fallback).

---

## 3. NON-FUNCTIONAL REQUIREMENTS

### 3.1 Performance
**REQ-PERF-01**: XML Generation and Signing MUST take less than 500ms per document on standard hardware.
**REQ-PERF-02**: Batch Reference checking (Unique Invoice Number) must be indexed in PostgreSQL.

### 3.2 Security
**REQ-SEC-01**: P12 Passwords MUST NOT be visible in the UI (Use `password=True` widget).
**REQ-SEC-02**: XML Logs MUST be sanitized of P12 passwords before storage.

---

## 4. DATA DICTIONARY (Legacy Mapping)
*   Legacy Table 17 (Tax Codes) -> Mapped to `account.tax.group`.
*   Legacy Table 18 (IVA Rates) -> Mapped to `account.tax` (Code 2, 0, 6, 7).
*   **NEW**: Table 20 (Retention Codes) -> Mapped to `l10n_ec.retention.concept`.

---

## 5. MIGRATION STRATEGY
*   **Data**: No data migration from Odoo 10 (Greenfield implementation assumed).
*   **Logic**: Port Python logic from `odoo-ecuador-legacy` manually, refactoring for Odoo 18 API (`write` vs `create`, `depends` vs `onchange`).

**APPROVAL**:
*   Legal: [APPROVED]
*   Technical: [APPROVED]
