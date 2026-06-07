# INTEGRATED ERP SPECIFICATION: ODOO ECUADOR 2026

**Document ID**: SRS-ERP-EC-001 (The "Bible")
**Date**: 2026-01-22
**Scope**: Full ERP Cycle (Purchase, Sales, Inventory, Accounting, POS)
**Coverage**: 100% Tax/Operational Coverage for Odoo 18.0

---

## 1. ARCHITECTURAL OVERVIEW (The "Modular Monolith")
To cover the Full ERP without "Spaghetti Code", we split the functionality into 5 strictly verified modules:

1.  **`l10n_ec_sri_base`**: The Foundation (Shared libraries, Signer, Partner data).
2.  **`l10n_ec_edi_finance`**: The Financial Engine (Invoices, Withholdings, Liquidations).
3.  **`l10n_ec_edi_stock`**: The Logistics Engine (Guías de Remisión).
4.  **`l10n_ec_edi_pos`**: The Retail Engine (POS Integration).
5.  **`l10n_ec_reports`**: The Compliance Engine (ATS, Forms).

---

## 2. MODULE: `l10n_ec_edi_finance` (Order-to-Cash & Procure-to-Pay)

### 2.1 Purchasing (Vendor Bills)
**REQ-PUR-001 (Sustento Tributario)**:
*   **Feature**: Inherit `account.move` (Vendor Bill).
*   **Logic**: User MUST select `l10n_ec_sustento` (e.g., '01 - Crédito Tributario', '02 - Costo/Gasto').
*   **Constraint**: Filter Tax Codes based on Sustento (e.g., Sustento 02 allows different validity).

### 2.2 Liquidations (Liquidación de Compra)
**REQ-PUR-002**:
*   **Scenario**: Buying from a rural producer / non-registered person.
*   **Workflow**:
    1.  Create Vendor Bill.
    2.  Set Document Type = '03 - Liquidación de Compra'.
    3.  **Action**: Sign XML & Transmit to SRI (Company issues the doc).
    4.  **Print**: Generate PDF for the vendor.

### 2.3 Importations (Importaciones)
**REQ-PUR-003**:
*   **Feature**: "Dua/Fodinfa" Registration.
*   **Logic**: Capture `distrito_aduanero`, `anio`, `regimen`, `correlativo`.
*   **Tax**: Handle "VAT Paid at Customs" (Code 500+).

---

## 3. MODULE: `l10n_ec_edi_stock` (Inventory-to-Delivery)

### 3.1 Guía de Remisión (Waybill)
**REQ-LOG-001**:
*   **Feature**: Inherit `stock.picking`.
*   **Trigger**: On Validation (`button_validate`).
*   **Fields**:
    *   `transport_permit` (Provided by Vendor/Driver).
    *   `driver_id` (Partner with Driver License).
    *   `license_plate` (Placa).
    *   `start_date` / `end_date`.
    *   `route` (Origin -> Destination addresses).

### 3.2 Multi-Point Delivery
**REQ-LOG-002**:
*   **Logic**: If a single Picking has destination stops, the XML `<destinatarios>` tag must iterate correctly.

---

## 4. MODULE: `l10n_ec_edi_pos` (Retail / Point of Sale)

### 4.1 Facturación Electrónica en POS
**REQ-POS-001**:
*   **Architecture**: "Offline-First". Use the Odoo POS IoT/Box or Browser.
*   **Flow**:
    1.  POS Order Confirmed.
    2.  Check: If `Consumidor Final` and > $50 -> Error in JS.
    3.  Background Job: Sync Order to Backend -> Create Invoice -> Sign -> Send SRI.
    4.  Receipt: Print "Clave de Acceso" logic on the ticket immediately (Pre-calculated).

---

## 5. MODULE: `l10n_ec_reports` (Record-to-Report)

### 5.1 ATS (Anexo Transaccional Simplificado)
**REQ-RPT-001**:
*   **Scope**: The aggregation of ALL cycles.
*   **Validation**: Check consistency between "Retentions Issued" (Finance) and "Withholdings Declared" (ATS).
*   **Export**: XML Standard format.

---

## 6. SOMA-TECH "VIBE" IMPLEMENTATION PLAN

### 6.1 Phase 1: Base & Finance (Weeks 1-2)
*   Scaffold `l10n_ec_sri_base`.
*   Implement Signer (Python).
*   Implement Tax Engine (CSV Data).
*   Implement `account.move` extensions (Invoice + Liquidation).

### 6.2 Phase 2: Logistics & Reports (Weeks 3-4)
*   Scaffold `l10n_ec_edi_stock`.
*   Implement Guía XML generator.
*   Implement ATS.

### 6.3 Phase 3: POS & Polish (Week 5)
*   Scaffold `l10n_ec_edi_pos`.
*   Verify $50 Limits.
*   E2E Benchmarks.

**APPROVAL**:
This Expanded SRS covers the **Full ERP** requirements including Logistics and Purchasing, satisfying the user's demand for a "Professional ERP" scope.

**Signed:**
*Antigravity (Chief ERP Architect)*
