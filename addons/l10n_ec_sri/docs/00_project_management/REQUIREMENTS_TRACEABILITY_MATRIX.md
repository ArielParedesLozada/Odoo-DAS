# REQUIREMENTS TRACEABILITY MATRIX
## ISO 29148:2018 Compliance

**Document ID**: RTM-001
**Version**: 1.0
**Effective Date**: 2026-01-22
**Owner**: Business Analyst

---

## 1. PURPOSE

This matrix traces all business requirements through design specifications, implementation, and test cases to ensure complete coverage and verification.

---

## 2. TRACEABILITY OVERVIEW

```mermaid
flowchart LR
    A[Business Requirement] --> B[SRS Specification]
    B --> C[Design/Data Mapping]
    C --> D[Implementation]
    D --> E[Test Case]
    E --> F[Acceptance]
```

---

## 3. CORE REQUIREMENTS TRACE

### 3.1 Electronic Invoicing (SRI)

| Req ID | Requirement | SRS | Data Mapping | Test Case | Status |
|:-------|:------------|:----|:-------------|:----------|:-------|
| REQ-001 | Generate electronic invoice XML per SRI v2.32 | SRS-002 §3.1 | DM-001 | TS-001-01 to 08 | ✅ |
| REQ-002 | Apply XAdES-BES digital signature | SRS-002 §3.2 | DM-001 §4 | TS-001-06 | ✅ |
| REQ-003 | Transmit to SRI via SOAP | SRS-002 §3.3 | DM-001 §5 | TS-001-10 to 14 | ✅ |
| REQ-004 | Handle SRI authorization responses | SRS-002 §3.4 | DM-001 §6 | TS-001-15 to 19 | ✅ |
| REQ-005 | Generate/send RIDE PDF | SRS-002 §3.5 | - | TS-001-20 to 23 | ✅ |
| REQ-006 | Validate RUC/Cédula with Módulo 11 | SRS-001 §4.2 | - | TS-001-02 | ✅ |
| REQ-007 | Enforce Consumidor Final $50 limit | SRS-002 §3.1.4 | DM-001 §3.3 | TS-001-04 | ✅ |
| REQ-008 | Apply 15% IVA calculation | SRS-001 §5.1 | DM-001 §3.5 | TS-001-03 | ✅ |

### 3.2 Withholding (Retención)

| Req ID | Requirement | SRS | Data Mapping | Test Case | Status |
|:-------|:------------|:----|:-------------|:----------|:-------|
| REQ-010 | Generate 5% IR withholding (303) | SRS-003 §3.1 | DM-002 | TS-002-01 | ✅ |
| REQ-011 | Generate 10% IR withholding (312) | SRS-003 §3.1 | DM-002 | TS-002-02 | ✅ |
| REQ-012 | Generate 30% IVA withholding | SRS-003 §3.2 | DM-002 | TS-002-03 | ✅ |
| REQ-013 | Generate 70% IVA withholding | SRS-003 §3.2 | DM-002 | TS-002-04 | ✅ |
| REQ-014 | Generate 100% IVA withholding | SRS-003 §3.2 | DM-002 | TS-002-05 | ✅ |
| REQ-015 | Enforce 5-day emission rule | SRS-003 §3.3 | DM-002 §4 | TS-002-06 | ✅ |
| REQ-016 | Link withholding to source invoice | SRS-003 §3.4 | DM-002 §3.2 | TS-002-07 | ✅ |
| REQ-017 | Transmit retención XML to SRI | SRS-003 §3.5 | DM-002 §5 | TS-002-08 | ✅ |

### 3.3 Payroll (HR/Nómina)

| Req ID | Requirement | SRS | Data Mapping | Test Case | Status |
|:-------|:------------|:----|:-------------|:----------|:-------|
| REQ-020 | Calculate IESS personal (9.45%) | SRS-006 §3.1 | DM-006 | TS-003-01 | 📝 Pending |
| REQ-021 | Calculate IESS patronal (12.15%) | SRS-006 §3.1 | DM-006 | TS-003-02 | 📝 Pending |
| REQ-022 | Generate IESS monthly planilla | SRS-006 §3.2 | DM-006 | TS-003-03 | 📝 Pending |
| REQ-023 | Calculate Décimo Tercero | SRS-006 §3.3 | KB-004 | TS-003-04 | 📝 Pending |
| REQ-024 | Calculate Décimo Cuarto | SRS-006 §3.4 | KB-004 | TS-003-05 | 📝 Pending |
| REQ-025 | Calculate Fondos de Reserva (8.33%) | SRS-006 §3.5 | KB-005 | TS-003-06 | 📝 Pending |
| REQ-026 | Calculate Utilidades (15%) | SRS-006 §3.6 | KB-006 | TS-003-07 | 📝 Pending |
| REQ-027 | Generate liquidation (finiquito) | SRS-006 §3.7 | KB-007 | TS-003-08 | 📝 Pending |
| REQ-028 | Withhold income tax per brackets | SRS-006 §3.8 | KB-003 | TS-003-09 | 📝 Pending |

### 3.4 Inventory & Stock

| Req ID | Requirement | SRS | Data Mapping | Test Case | Status |
|:-------|:------------|:----|:-------------|:----------|:-------|
| REQ-030 | Generate Guía de Remisión XML | SRS-004 §3.1 | DM-004 | TS-005-01 | 📝 Pending |
| REQ-031 | Track lot/serial with SRI | SRS-004 §3.2 | DM-004 | TS-005-02 | 📝 Pending |
| REQ-032 | Link to invoice movements | SRS-004 §3.3 | - | TS-005-03 | 📝 Pending |

### 3.5 Customs (Importación)

| Req ID | Requirement | SRS | Data Mapping | Test Case | Status |
|:-------|:------------|:----|:-------------|:----------|:-------|
| REQ-040 | Calculate Ad-Valorem duties | SRS-005 §3.1 | KB-009 | TS-006-01 | 📝 Pending |
| REQ-041 | Calculate FODINFA (0.5%) | SRS-005 §3.2 | KB-009 | TS-006-02 | 📝 Pending |
| REQ-042 | Calculate ICE on imports | SRS-005 §3.3 | KB-009 | TS-006-03 | 📝 Pending |
| REQ-043 | Calculate IVA on CIF+duties | SRS-005 §3.4 | KB-009 | TS-006-04 | 📝 Pending |
| REQ-044 | Track DAI declaration | SRS-005 §3.5 | - | TS-006-05 | 📝 Pending |

### 3.6 Point of Sale (POS)

| Req ID | Requirement | SRS | Data Mapping | Test Case | Status |
|:-------|:------------|:----|:-------------|:----------|:-------|
| REQ-050 | Issue POS invoice in <2 seconds | SRS-008 §3.1 | DM-001 | TS-004-01 | 📝 Pending |
| REQ-051 | Offline mode with sync | SRS-008 §3.2 | - | TS-004-02 | 📝 Pending |
| REQ-052 | Apply Consumidor Final auto-lock | SRS-008 §3.3 | - | TS-004-03 | 📝 Pending |
| REQ-053 | Print receipt with RIDE | SRS-008 §3.4 | - | TS-004-04 | 📝 Pending |

### 3.7 Reporting (ATS, 103, 104)

| Req ID | Requirement | SRS | Data Mapping | Test Case | Status |
|:-------|:------------|:----|:-------------|:----------|:-------|
| REQ-060 | Generate ATS XML | SRS-009 §3.1 | DM-007 | TS-007-01 | 📝 Pending |
| REQ-061 | Generate Form 103 | SRS-009 §3.2 | - | TS-007-02 | 📝 Pending |
| REQ-062 | Generate Form 104 | SRS-009 §3.3 | - | TS-007-03 | 📝 Pending |
| REQ-063 | Generate balance for Supercias | SRS-009 §3.4 | KB-008 | TS-007-04 | 📝 Pending |

### 3.8 AI Agent Capabilities

| Req ID | Requirement | SRS | Data Mapping | Test Case | Status |
|:-------|:------------|:----|:-------------|:----------|:-------|
| REQ-070 | Voice-to-Invoice via MCP | AI-001, AI-002 | - | TS-001-AI-01 | 📝 Pending |
| REQ-071 | AI Collection Agent (WhatsApp) | AI-001 §4.3 | AI-005 | TS-AI-01 | 📝 Pending |
| REQ-072 | AI Purchase Order from photos | AI-001 §4.1 | AI-002 | TS-AI-02 | 📝 Pending |
| REQ-073 | AI Liquidation Calculator | AI-001 §4.4 | AI-002 | TS-AI-03 | 📝 Pending |
| REQ-074 | AI Compliance Monitor | AI-001 §5 | - | TS-AI-04 | 📝 Pending |

---

## 4. COVERAGE SUMMARY

| Category | Requirements | With SRS | With Test | Coverage |
|:---------|:-------------|:---------|:----------|:---------|
| Electronic Invoicing | 8 | 8 | 8 | 100% |
| Withholding | 8 | 8 | 8 | 100% |
| Payroll | 9 | 9 | 0 | 0% (pending) |
| Inventory | 3 | 3 | 0 | 0% (pending) |
| Customs | 5 | 5 | 0 | 0% (pending) |
| POS | 4 | 4 | 0 | 0% (pending) |
| Reporting | 4 | 4 | 0 | 0% (pending) |
| AI Agent | 5 | 5 | 0 | 0% (pending) |
| **TOTAL** | **46** | **46** | **16** | **35%** |

---

## 5. REGULATORY TRACEABILITY

| Regulation | KB Entry | Affected Requirements |
|:-----------|:---------|:----------------------|
| SRI Ficha Técnica v2.32 | KB-001 | REQ-001 to 008, 010-017 |
| Código del Trabajo (SBU) | KB-004 | REQ-023, 024 |
| IESS Contributions | KB-003 | REQ-020, 021, 022, 025 |
| Income Tax Brackets | KB-003 | REQ-028 |
| Fondos de Reserva | KB-005 | REQ-025 |
| Utilidades | KB-006 | REQ-026 |
| Termination Law | KB-007 | REQ-027 |
| Supercias Reporting | KB-008 | REQ-063 |
| SENAE Customs | KB-009 | REQ-040 to 044 |

---

## 6. FORWARD/BACKWARD TRACE

### 6.1 Forward Trace (Requirement → Test)
Every requirement MUST have at least one test case.

### 6.2 Backward Trace (Test → Requirement)
Every test case MUST link to at least one requirement.

---

## 7. GAP IDENTIFICATION

| Gap ID | Description | Action Required | Owner | Due Date |
|:-------|:------------|:----------------|:------|:---------|
| RTM-GAP-001 | Payroll tests not created | Create TS-003 | QA Lead | 2026-02-01 |
| RTM-GAP-002 | Inventory tests not created | Create TS-005 | QA Lead | 2026-02-01 |
| RTM-GAP-003 | Customs tests not created | Create TS-006 | QA Lead | 2026-02-01 |
| RTM-GAP-004 | POS tests not created | Create TS-004 | QA Lead | 2026-02-01 |
| RTM-GAP-005 | Reports tests not created | Create TS-007 | QA Lead | 2026-02-01 |
| RTM-GAP-006 | AI Agent tests not created | Create TS-AI | QA Lead | 2026-02-15 |

---

## 8. REFERENCES

- ISO/IEC/IEEE 29148:2018 - Requirements Engineering
- PMI PMBOK® Guide, 7th Edition - Requirements Traceability
- [Business Requirements Document](./BUSINESS_REQUIREMENTS_DOCUMENT.md)
- [Document Control Matrix](./DOC_CONTROL_MATRIX.md)

---

**Traceability Classification**: ISO 29148:2018 Controlled Matrix
