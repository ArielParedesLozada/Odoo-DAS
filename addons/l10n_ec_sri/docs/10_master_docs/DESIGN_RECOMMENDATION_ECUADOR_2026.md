# SOMA TECH ECUADOR: Odoo 18.0 Architecture Recommendation (2026)

**Authored By**:
*   **Dr. Legal (LORTI/UAFE Specialist)**
*   **Ing. Odoo Architect (Vibe Coding Certified)**
*   **Lic. CPA (NIIF/SRI Expert)**

**Date**: January 22, 2026
**Document ID**: SOMA-ARCH-EC-2026
**Status**: **PROPOSAL FOR APPROVAL**

---

## 1. EXECUTIVE SUMMARY & "PERFECT" ARCHITECTURE
After analyzing the legacy codebase (v10) and current 2026 Law (Ley Orgánica de Simplificación y Progresividad Tributaria + RIMPE + 15% IVA), we recommend a **Unified "Sovereign" Module Approach**.

### The Recommendation: `l10n_ec_sri` (The Core Monolith)
Instead of adhering to the legacy fragmentation (14 modules), we strongly recommend a single, robust module `l10n_ec_sri` that encapsulates the entire "Fiscal Integrity" of the company.

**Why?**
1.  **Vibe Rule #3 (No Unnecessary Files)**: Managing dependencies between `partner`, `tax`, `einvoice`, `withholding` is fragile. In Ecuador, you cannot issue an Invoice without understanding Withholdings (Agents of Retention). They are inseparable.
2.  **Transactional Integrity**: The "Cross-Reference" (Cruce de Cuentas) between ATS, Form 104, and Electronic Invoices requires real-time consistency. A monolith ensures atomic updates.

### Secondary Module: `l10n_ec_reports` (Compliance)
A separate module strictly for **SRI Reporting** (ATS, RDEP, Form 103/104). This separates "Daily Operations" (Invoicing) from "Monthly Compliance" (Reporting), which allows for report updates without risking operational code.

---

## 2. LEGAL & FISCAL MANDATES (The "Lawyer & CPA" Input)

### 2.1 The "RIMPE" Imperative (Mandatory)
*   **Regulation**: Regimen Simplificado para Emprendedores y Negocios Populares.
*   **Impact**: We MUST distinguish between `RIMPE - Negocio Popular` (0% rate, text legend) and `RIMPE - Emprendedor`. The legacy code has ZERO support for this.
*   **Requirement**: `res.partner` must have a field `x_sri_regime` and dynamic tax mapping.

### 2.2 UAFE & "Consumidor Final" ($50 Rule)
*   **Regulation**: Anti-Money Laundering (UAFE) limits "Consumidor Final" to $50.00.
*   **Technical Lock**: The POS and Invoice form MUST physically block validation if:
    *   Partner = Consumidor Final (9999999999999) AND
    *   Amount > $50.
*   **Exception**: Unless an explicit "Manager Override" (generic ID) is used, but legally, we must demand RUC/Cedula.

### 2.3 The 15% IVA Reality
*   **Regulation**: Standard VAT rate is 15% (as of 2024/2025).
*   **Technical**: Hardcoded tables in legacy (Task Step 62) are obsolete. We need a `account.tax.group` with metadata ID `2` (IVA) and Code `4` (15%).

### 2.4 Electronic Signatures (Firma Electrónica)
*   **Regulation**: Messages are legally binding.
*   **Security**: The P12/PFX file must be encrypted at rest (Vibe "Secret Sovereignty"). The password should NOT be stored in plain text if possible, or minimally scoped.

---

## 3. PROPOSED MODULE STRUCTURE

### Module 1: `l10n_ec_sri` (The Engine)
*   **Manifest**: `depends: ['account', 'base', 'web']`
*   **Scope**:
    *   **Identity**: RUC/Cedula/Pasaporte validators (Algorithm Modulo 10 & 11).
    *   **Fiscal**: Chart of Accounts (NEC/NIIF), Tax Groups (IVA 15%, 5%, 0%, Exento).
    *   **Document**: `account.move` extensions for `clave_acceso`, `tipo_emision`.
    *   **Withholding**: `account.retention` (or `account.payment` override) for Retentions *received* and *issued*.
    *   **EDI**: Python-native Signing (`cryptography` + `lxml`) & Zeep SOAP client.
    *   **Email**: Customized Templates for "Ride" (PDF + XML).

### Module 2: `l10n_ec_reports` (The Accountant)
*   **Manifest**: `depends: ['l10n_ec_sri']`
*   **Scope**:
    *   **ATS**: XML Generation for Anexo Transaccional.
    *   **Financial Reports**: Balance Sheet (Supercias Format), P&L (Supercias Format).

---

## 4. NEXT STEPS
I have prepared the **ISO-Compliant SRS** for the Core Module below.

**Recommendation**: Accept this architecture. It is cleaner, legally safer, and easier to maintain than the legacy spaghetti.
