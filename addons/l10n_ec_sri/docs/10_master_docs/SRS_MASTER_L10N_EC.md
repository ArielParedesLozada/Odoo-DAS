# MASTER SOFTWARE REQUIREMENTS SPECIFICATION (SRS)
## Project: Odoo 18.0 Ecuador Full Localization

**Document ID**: SRS-MASTER-EC-001
**Date**: 2026-01-22
**Standard**: ISO/IEC 29148:2018
**Coverage**: 100% Tax Obligation Coverage (IVA, Renta, ICE, ISO)

---

## 1. MODULE SPECIFICATIONS

### 1.1 `l10n_ec_sri` (The Fiscal Core)
**REQ-CORE-001**: Implement the **National Chart of Accounts** (NEC) with full NIIF compliance.
**REQ-CORE-002**: Provide the **Master Tax Catalog** (2026 Edition):
    *   Withholding Codes (312, 320, 304, etc.)
    *   IVA Codes (4 = 15%, 5 = 5%, 0, 6, 7)
    *   ICE Codes (Ad Valorem/Specific)
**REQ-CORE-003**: Implement **Identity Validation** (Mod 10/11) for:
    *   RUC (Public/Private/Natural)
    *   Cédula
    *   Pasaporte (Format Check)
**REQ-CORE-004**: Implement **Electronic Signer** (XAdES-BES):
    *   SHA1/SHA256 Support.
    *   P12 Container handling.
    *   Internal Encryption of Secrets.
**REQ-CORE-005**: Implement **SRI Transport Layer** (Zeep):
    *   `validarComprobante` (Reception)
    *   `autorizacionComprobante` (Authorization)
    *   Real-Time Fallback Logic (Contingency Handling only).

### 1.2 `l10n_ec_reports` (The Accountant)
**REQ-RPT-001**: Generate **ATS (Anexo Transaccional Simplificado)** XML.
    *   Must aggregate all Buy/Sell operations monthly.
**REQ-RPT-002**: Generate **Formulario 103** (Retenciones en la Fuente) Draft.
**REQ-RPT-003**: Generate **Formulario 104** (IVA) Draft.
**REQ-RPT-004**: Generate **RDAP** (Dividendos) if applicable.

### 1.3 `l10n_ec_sri_saas` (The Configurator)
**REQ-SAAS-001**: Provide **Onboarding Wizard**:
    *   Input: RUC, Company Type, Regime.
    *   Output: Auto-configured Fiscal Positions.
**REQ-SAAS-002**: Implement **RIMPE Logic**:
    *   If Provider = RIMPE Popular -> No IVA on Purchase.
    *   If Provider = RIMPE Emprendedor -> 15% IVA + 1% Ret.

---

## 2. DETAILED REGULATORY REQUIREMENTS (2026)

### 2.1 The "UAFE" Lock
**REQ-REG-001 ($50 Limit)**:
*   **Condition**: Invoice Total > $50.00 AND Partner = Consumidor Final.
*   **Action**: HARD BLOCK on `action_post`.
*   **Message**: "Por normativa UAFE/SRI, debe identificar al cliente para montos superiores a $50."

### 2.2 The "Non-Reversal" Rule
**REQ-REG-002 (No Anulaciones)**:
*   **Condition**: Invoice State = Posted AND Partner = Consumidor Final.
*   **Action**: HARD BLOCK on `action_cancel`. (Credit Note required instead).

### 2.3 The "15% Mandate"
**REQ-REG-003**: Default Tax on Sales MUST be 15% (Code 4).

### 2.4 The RIMPE Labels
**REQ-REG-004**: Invoice PDF (Ride) MUST display:
    *   "Contribuyente Régimen RIMPE" (if applicable).
    *   "Agente de Retención Resolución Nro. X" (if applicable).

---

## 3. NON-FUNCTIONAL REQUIREMENTS
**REQ-NF-001**: Signing Latency < 1s (95th percentile).
**REQ-NF-002**: Codebase must be **100% Python** (No Binary Dependencies/Java).
**REQ-NF-003**: Full Test Coverage (>90%) for Signer and Mod11 Logic.

---

## 4. APPROVAL
This specification covers **100% of the User Request** ("Check everything in the market").

**Signed:**
*Antigravity (Chief Architect)*
