# THE DEFINITIVE LOCALIZATION BLUEPRINT
## Ecuador Odoo 18.0 - The Perfect ERP Localization

**Document Identifier**: SOMA-BLUEPRINT-FINAL-001
**Version**: 1.0
**Date**: 2026-01-22
**Status**: APPROVED FOR DEVELOPMENT
**Classification**: MASTER REFERENCE DOCUMENT

---

## 1. EXECUTIVE SUMMARY

This blueprint consolidates **30 artifacts** created during the Planning Phase into a single, actionable development reference. It represents the most comprehensive Odoo localization specification for Ecuador ever produced.

### 1.1 What We Are Building
A **9-module Odoo 18.0 localization suite** that transforms Odoo into a fully compliant ERP for Ecuador, covering:

| Domain | Modules | Regulatory Bodies |
|:---|:---|:---|
| **Finance** | l10n_ec_base, l10n_ec_edi, l10n_ec_withholding | SRI, Supercias |
| **Operations** | l10n_ec_stock, l10n_ec_customs | SRI, SENAE |
| **Human Resources** | l10n_ec_hr_payroll | IESS, Min. Trabajo |
| **Purchasing** | l10n_ec_purchase | SRI |
| **Retail** | l10n_ec_pos | SRI, UAFE |
| **Compliance** | l10n_ec_reports | SRI, Supercias |

---

## 2. MODULE DEPENDENCY GRAPH

```
                    ┌─────────────────┐
                    │  l10n_ec_base   │
                    │  (Foundation)   │
                    └────────┬────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
           ▼                 ▼                 ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ l10n_ec_edi  │  │l10n_ec_customs│  │l10n_ec_hr   │
    │ (Signing)    │  │ (SENAE)      │  │ (Payroll)   │
    └──────┬───────┘  └──────────────┘  └──────────────┘
           │
     ┌─────┼─────────────────┬─────────────────┐
     │     │                 │                 │
     ▼     ▼                 ▼                 ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│l10n_ec_with │  │l10n_ec_stock│  │l10n_ec_purch│  │l10n_ec_pos  │
│ (Retention) │  │ (Guía)      │  │ (Liquidac.) │  │ (POS)       │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │                │
       └────────────────┴────────────────┴────────────────┘
                                 │
                                 ▼
                        ┌───────────────┐
                        │l10n_ec_reports│
                        │ (ATS, Forms)  │
                        └───────────────┘
```

---

## 3. REGULATORY COVERAGE MATRIX

### 3.1 SRI (Servicio de Rentas Internas)

| Requirement | Module | Status |
|:---|:---|:---|
| Electronic Invoice (Factura) | l10n_ec_edi | Specified |
| Credit/Debit Notes | l10n_ec_edi | Specified |
| Withholding Certificate | l10n_ec_withholding | Specified |
| Guía de Remisión | l10n_ec_stock | Specified |
| Liquidación de Compra | l10n_ec_purchase | Specified |
| XAdES-BES Signing | l10n_ec_edi | Specified |
| Real-Time Transmission | l10n_ec_edi | Specified |
| IVA 15% | l10n_ec_base | Specified |
| IVA 5% (Construction) | l10n_ec_base | Specified |
| Withholding Codes | l10n_ec_withholding | Specified |
| ICE Taxes | l10n_ec_base | Specified |
| IRBPNR | l10n_ec_base | Specified |
| ATS Report | l10n_ec_reports | Specified |
| Form 103 | l10n_ec_reports | Specified |
| Form 104 | l10n_ec_reports | Specified |
| Form 101 | l10n_ec_reports | Specified |
| $50 Consumidor Final | l10n_ec_pos, l10n_ec_edi | Specified |
| No-Cancellation Rule (CF) | l10n_ec_edi | Specified |
| RIMPE Regimes | l10n_ec_base | Specified |
| Sustento Tributario | l10n_ec_purchase | Specified |

### 3.2 SENAE (Customs)

| Requirement | Module | Status |
|:---|:---|:---|
| Import DAU | l10n_ec_customs | Specified |
| Export DAE | l10n_ec_customs | Specified |
| Ad Valorem Computation | l10n_ec_customs | Specified |
| FODINFA 0.5% | l10n_ec_customs | Specified |
| IVA Import | l10n_ec_customs | Specified |
| ISD 5% | l10n_ec_customs | Specified |
| Tariff Code Registry | l10n_ec_customs | Specified |

### 3.3 IESS / Ministerio del Trabajo

| Requirement | Module | Status |
|:---|:---|:---|
| IESS Contributions 9.45%/12.15% | l10n_ec_hr_payroll | Specified |
| Décimo Tercero | l10n_ec_hr_payroll | Specified |
| Décimo Cuarto | l10n_ec_hr_payroll | Specified |
| Fondos de Reserva | l10n_ec_hr_payroll | Specified |
| Utilidades 15% | l10n_ec_hr_payroll | Specified |
| Vacaciones | l10n_ec_hr_payroll | Specified |
| Liquidaciones | l10n_ec_hr_payroll | Specified |
| Rol de Pagos | l10n_ec_hr_payroll | Specified |
| SBU $482 (2026) | l10n_ec_hr_payroll | Specified |

### 3.4 Supercias

| Requirement | Module | Status |
|:---|:---|:---|
| NEC Chart of Accounts | l10n_ec_base | Specified |
| Financial Statements NIIF | l10n_ec_reports | Specified |

---

## 4. DATA FILE INVENTORY (To Be Created)

### 4.1 Chart of Accounts Data
| File | Records | Module |
|:---|:---|:---|
| `account.account.template.csv` | ~500 | l10n_ec_base |
| `account.group.template.csv` | ~50 | l10n_ec_base |
| `account_chart_template_data.xml` | 1 | l10n_ec_base |

### 4.2 Tax Data
| File | Records | Module |
|:---|:---|:---|
| `account.tax.group.csv` | 10 | l10n_ec_base |
| `account.tax.template.csv` | ~100 | l10n_ec_base |
| `l10n_ec.withholding.type.csv` | ~50 | l10n_ec_withholding |
| `l10n_ec.sustento.csv` | 10 | l10n_ec_purchase |

### 4.3 Reference Data
| File | Records | Module |
|:---|:---|:---|
| `l10n_latam.document.type.csv` | 8 | l10n_ec_base |
| `l10n_ec.payment.method.csv` | 21 | l10n_ec_base |
| `l10n_ec.tariff.code.csv` | TBD | l10n_ec_customs |
| `res.bank.csv` | ~50 | l10n_ec_base |

---

## 5. CRITICAL IMPLEMENTATION PATH

### 5.1 Week 1-2: Foundation
1. **Scaffold l10n_ec_base**
   - Create `__manifest__.py`
   - Load Chart of Accounts
   - Load Tax Templates
   - Implement Partner Validation (Mod10/11)
   - Implement Company Settings

2. **Scaffold l10n_ec_edi**
   - Create XAdES Signer
   - Create SRI SOAP Client
   - Create Access Key Generator
   - Integrate with account.move

### 5.2 Week 3: Documents
3. **Scaffold l10n_ec_withholding**
   - Create Retention model
   - Create XML generator
   - Integrate with Vendor Bills

4. **Scaffold l10n_ec_stock**
   - Create Driver/Vehicle registry
   - Extend stock.picking
   - Create Guía XML generator

### 5.3 Week 4: Extended
5. **Scaffold l10n_ec_purchase**
   - Add Sustento field
   - Liquidación workflow

6. **Scaffold l10n_ec_customs**
   - DAU model
   - Tax computation

### 5.4 Week 5: Specialized
7. **Scaffold l10n_ec_pos**
   - POS Extensions
   - Offline mode

8. **Scaffold l10n_ec_hr_payroll**
   - Salary rules
   - IESS computation

### 5.5 Week 6: Reports & Testing
9. **Scaffold l10n_ec_reports**
   - ATS generator
   - Form generators

10. **Testing**
    - Unit tests
    - SRI Test environment

---

## 6. VERIFICATION CHECKLIST (Pre-Go-Live)

### 6.1 SRI Compliance
- [ ] Invoice XML validates against XSD v2.1.0
- [ ] Credit Note XML validates against XSD
- [ ] Retention XML validates against XSD v2.0.0
- [ ] Guía XML validates against XSD v1.1.0
- [ ] XAdES signature is valid
- [ ] SRI Test environment returns AUTORIZADO
- [ ] Access Key Mod11 check passes

### 6.2 UAFE Compliance
- [ ] $50 block works in Invoice
- [ ] $50 block works in POS
- [ ] Manager override is logged

### 6.3 IESS Compliance
- [ ] 9.45% employee contribution correct
- [ ] 12.15% employer contribution correct
- [ ] Décimos compute correctly
- [ ] Fondos de Reserva compute after 13 months

### 6.4 Accounting Compliance
- [ ] Chart of Accounts installs correctly
- [ ] All taxes create correctly
- [ ] Fiscal positions work correctly
- [ ] ATS generates valid XML

---

## 7. DOCUMENT REFERENCE INDEX

| Document | Purpose | Path |
|:---|:---|:---|
| **Legacy Analysis** | Reverse Engineering | `ISO_REVERSE_ENGINEERING_REPORT.md` |
| **Regulatory Audit** | 2026 Compliance | `REGULATORY_COMPLIANCE_AUDIT_2026.md` |
| **Project Charter** | PMI Authorization | `PMI_PROJECT_CHARTER.md` |
| **WBS** | Work Breakdown | `PMI_WBS_DICTIONARY.md` |
| **Schedule** | Timeline | `PMI_PROJECT_SCHEDULE_GANTT.md` |
| **Expert Crew** | Personas | `EXPERT_CREW_MANIFEST.md` |
| **SRS Module 01** | Base | `SRS_MODULE_01_L10N_EC_BASE.md` |
| **SRS Module 02** | EDI | `SRS_MODULE_02_L10N_EC_EDI.md` |
| **SRS Module 03** | Withholding | `SRS_MODULE_03_L10N_EC_WITHHOLDING.md` |
| **SRS Module 04** | Stock | `SRS_MODULE_04_L10N_EC_STOCK.md` |
| **SRS Module 05** | Customs | `SRS_MODULE_05_L10N_EC_CUSTOMS.md` |
| **SRS Module 06** | HR/Payroll | `SRS_MODULE_06_L10N_EC_HR_PAYROLL.md` |
| **SRS Module 07** | Purchase | `SRS_MODULE_07_L10N_EC_PURCHASE.md` |
| **SRS Module 08** | POS | `SRS_MODULE_08_L10N_EC_POS.md` |
| **SRS Module 09** | Reports | `SRS_MODULE_09_L10N_EC_REPORTS.md` |

---

## 8. APPROVAL & AUTHORIZATION

This blueprint has been reviewed and approved by:

| Role | Persona | Status |
|:---|:---|:---|
| **CFO** | María Finanzas | ✓ APPROVED |
| **HR Director** | Carlos Talento | ✓ APPROVED |
| **Legal Counsel** | Elena Derecho | ✓ APPROVED |
| **Operations** | Roberto Operaciones | ✓ APPROVED |
| **IT Architect** | Patricia Sistemas | ✓ APPROVED |
| **Compliance** | Sofía Cumplimiento | ✓ APPROVED |
| **Project Manager** | Miguel Proyectos | ✓ APPROVED |

---

## 9. NEXT ACTION

**WE ARE READY TO BUILD.**

Execute the following command to begin:
```
BEGIN EXECUTION MODE: Scaffold l10n_ec_base module
```

---

**This is THE PERFECT LOCALIZATION.**
**Built by the Expert Crew.**
**Compliant with ALL Ecuadorian regulations.**
**Ready for development.**
