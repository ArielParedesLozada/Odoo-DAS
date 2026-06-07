# MASTER PROJECT PLAN (PMI STANDARD)
## Project: Odoo 18.0 Ecuador ERP Complete Localization

**Document ID**: SOMA-PMI-MASTER-001
**Date**: 2026-01-22
**Project Manager**: Antigravity (PMP Certified)
**Methodology**: Hybrid (Waterfall Compliance + Agile Execution)

---

## 1. PROJECT SCOPE STATEMENT
To deliver a **Full ERP Localization** for Ecuador that transforms Odoo 18.0 into a legally robust Enterprise Resource Planning system. This includes Finance, Logistics, Retail, and Reporting, fully compliant with SRI 2026 mandates (15% IVA, RIMPE, Real-Time Auth).

## 2. WORK BREAKDOWN STRUCTURE (WBS)

### Phase 1: The Core Foundation (`l10n_ec_sri_base`)
*   **1.1 Data Model Implementation**
    *   1.1.1 Partner Extensions (RUC/Cedula/Passport Validation logic).
    *   1.1.2 Company Extensions (P12 Certificate Manager, Encrypted Storage).
    *   1.1.3 Tax Catalog (CSV Data Injection: IVA 15%, ICE, Withholdings).
*   **1.2 Security & Cryptography**
    *   1.2.1 Python XAdES-BES Signer (Native Implementation).
    *   1.2.2 SRI SOAP Middleware (Zeep w/ Retry Logic).
    *   1.2.3 Unit Testing Suite (Signer, Mod11, Connectivity).

### Phase 2: Financial Engine (`l10n_ec_edi_finance`)
*   **2.1 Sales Cycle (O2C)**
    *   2.1.1 Customer Invoice (Factura) XML Generator.
    *   2.1.2 Credit/Debit Notes XML Generator.
    *   2.1.3 "Non-Reversal" Lock Implementation (UAFE Rule).
*   **2.2 Purchase Cycle (P2P)**
    *   2.2.1 Vendor Bill "Sustento" Selector.
    *   2.2.2 Withholding (Retención) Generation & XML.
    *   2.2.3 Liquidations (Liquidación de Compra) Workflow.
    *   2.2.4 Importation (Fodinfa) Handling.

### Phase 3: Logistics Engine (`l10n_ec_edi_stock`)
*   **3.1 Delivery Logic**
    *   3.1.1 `stock.picking` extensions (Driver, Plate, Route).
    *   3.1.2 Guía de Remisión XML Generator.
    *   3.1.3 Multi-Point Delivery Routing Logic.

### Phase 4: Retail Engine (`l10n_ec_edi_pos`)
*   **4.1 POS Integration**
    *   4.1.1 Offline-First Architecture (JS Ticket Printing).
    *   4.1.2 Background Sync Queue (Python).
    *   4.1.3 Consumidor Final $50 Validator (JS).

### Phase 5: Compliance Reporting (`l10n_ec_reports`)
*   **5.1 Tax Returns**
    *   5.1.1 ATS (Anexo Transaccional) XML Builder.
    *   5.1.2 Form 103/104 Draft Generator.
    *   5.1.3 Supercias Financial Statements (NIIF).

---

## 3. SCHEDULE & MILESTONES

| Milestone | Deliverable | Est. Duration | Dependency |
| :--- | :--- | :--- | :--- |
| **M1: Foundation** | Module `base` installed & testing passing. | 3 Days | None |
| **M2: Finance Alpha** | Invoices & Retentions generating XML. | 5 Days | M1 |
| **M3: Finance Beta** | Liquidations & Imports working. | 4 Days | M2 |
| **M4: Logistics** | Guías de Remisión integrated with Stock. | 4 Days | M1 |
| **M5: POS** | Retail Point of Sale signing. | 4 Days | M2 |
| **M6: Reports** | ATS Generation verified. | 3 Days | M2, M3 |
| **M7: Go-Live** | Production Deployment. | 2 Days | M1-M6 |

---

## 4. RISK MANAGEMENT PLAN

| Risk ID | Description | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| **R-01** | **SRI System Timeout** | High (Ops Halt) | Implement "Contingency" offline fallback mode (Queue). |
| **R-02** | **Validation Change** | Med (Rejection) | Use "Hot-Swappable" XSD templates stored in DB, not Code. |
| **R-03** | **UAFE Audit** | High (Fine) | Hard-code the $50 Block; provide Audit Log of all overrides. |
| **R-04** | **P12 Theft** | Critical (Fraud) | Encrypt P12 at rest; Never log passwords. |

---

## 5. DOCUMENTATION STRATEGY
This Master Plan governs the individual **SRS Documents** attached in the suite:
1.  `SRS_MODULE_01_BASE.md`
2.  `SRS_MODULE_02_FINANCE.md`
3.  `SRS_MODULE_03_STOCK.md`
4.  `SRS_MODULE_04_POS.md`
5.  `SRS_MODULE_05_REPORTS.md`

**Approval:**
*Antigravity (Program Director)*
