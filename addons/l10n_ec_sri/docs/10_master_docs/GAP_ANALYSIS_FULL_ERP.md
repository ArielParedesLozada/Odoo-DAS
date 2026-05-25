# CRITICAL GAP ANALYSIS: FULL ERP SCOPE
## Odoo Ecuador Localization vs. ERP Requirements

**Document ID**: SOMA-GAP-ERP-001
**Date**: 2026-01-22
**Status**: **CRITICAL REMEDIATION**
**Auditor**: SomaTech Chief Architect (ERP Specialist)

---

## 1. EXECUTIVE APOLOGY & ASSESSMENT
The previous documentation (`SRS_ISO_DETAILED...`) was indeed **deficient** in the context of a full ERP. It focused heavily on *Outbound Invoicing* (Sales) but neglected the complexity of *Inbound Operations* (Purchasing, Logistics) and *Point of Sale*.

**Verdict**: The previous design covered ~40% of the ERP (Order-to-Cash). The remaining 60% (Procure-to-Pay, Inventory, POS) is missing.

---

## 2. IDENTIFIED GAPS (THE MISSING 60%)

### 2.1 The "Procure-to-Pay" Cycle (Purchasing)
*   **Missing: Liquidaciones de Compra (3.0)**
    *   **Reality**: When a company buys from someone *without* a RUC (e.g., rural producer), the Company MUST issue the invoice on their behalf.
    *   **Requirement**: A Wizard in Purchase Orders to "Generate Liquidación" -> Sign it -> Send it.
*   **Missing: Importations (Importaciones)**
    *   **Reality**: Imports have specific Tax Codes (Customs).
    *   **Requirement**: "Reembolso de Gastos" logic and specific ATS codes for Imports.
*   **Missing: Non-Deductible Expenses**
    *   **Reality**: Not all expenses are tax-deductible.
    *   **Requirement**: A toggle on Vendor Bills: "Gasto No Deducible" (affects Form 101/102).

### 2.2 The "Inventory & Logistics" Cycle
*   **Missing: Guía de Remisión (Delivery Note)**
    *   **Reality**: You cannot move goods in Ecuador without a Guía.
    *   **Requirement**: `stock.picking` must be signable.
    *   **Complexity**: Multi-destination routes, "Motivo de Traslado", Driver/Plate Details.
    *   **Integration**: Must link to the Invoice for the "Cruce" (Cross-check).

### 2.3 The "Point of Sale" (Retail)
*   **Missing: Offline/Online Hybrid**
    *   **Reality**: Retail shops cannot wait 5 seconds for SRI. They need "Facturación Offline" (Contingency) or "Fast Invoice".
    *   **Requirement**: Integration with `point_of_sale` module.
    *   **Logic**: "Cierre de Caja" (Session Closing) must reconcile SRI Documents.

### 2.4 The "Financial Compliance" (ATS)
*   **Missing: "Sustento Tributario"**
    *   **Reality**: Every Purchase must have a "Sustento" (e.g., Code 01: Tax Credit, Code 02: Cost/Expense).
    *   **Requirement**: The User MUST select the "Sustento" on every Vendor Bill.
*   **Missing: Reembolsos**
    *   **Reality**: Intermediaries must declare reimbursements.

---

## 3. REMEDIATION PLAN (THE NEW SRS)

I will immediately generate `SRS_FULL_ERP_INTEGRATED.md` that explicitly details:

1.  **Module: `l10n_ec_edi_stock`**:
    *   Extending `stock.picking` for Guías de Remisión.
    *   Driver/Vehicle Registry.

2.  **Module: `l10n_ec_edi_purchase`**:
    *   Liquidations of Purchase.
    *   Withholding on Purchases (Retención en la Fuente).
    *   "Sustento Tributario" selector.

3.  **Module: `l10n_ec_edi_pos`**:
    *   POS Receipt -> Electronic Invoice conversion.
    *   Offline Session Key management.

4.  **Module: `l10n_ec_accounting` (Expanded)**:
    *   Bank Reconciliation interfaces.
    *   "Caja Chica" (Petty Cash) liquidations.

**Process**: I will perform a Deep Research step on "Guía de Remisión 2026" and "Liquidación de Compra 2026" to ensure the new SRS is perfect.
