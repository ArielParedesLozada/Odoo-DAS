# REGULATORY KNOWLEDGE BASE: SUPERINTENDENCIA DE COMPAÑÍAS
## Corporate Compliance and Financial Reporting Requirements

**Source**: https://www.supercias.gob.ec/portalscvs/
**Official Name**: Superintendencia de Compañías, Valores y Seguros (SCVS)
**Last Verified**: 2026-01-22

---

## 1. AGENCY OVERVIEW

| Attribute | Value |
|:----------|:------|
| **Name** | Superintendencia de Compañías, Valores y Seguros |
| **Acronym** | SCVS (Supercias) |
| **Role** | Supervision and control of companies and securities |
| **Scope** | All corporations (S.A., S.A.S., Cia. Ltda.) |
| **Portal** | https://www.supercias.gob.ec |

---

## 2. STATUTORY OBLIGATIONS

### 2.1 Company Types Supervised
| Type | Description |
|:-----|:------------|
| **S.A.** | Sociedad Anónima (Corporation) |
| **S.A.S.** | Sociedad por Acciones Simplificada (Simplified Corp) |
| **Cia. Ltda.** | Compañía de Responsabilidad Limitada (LLC) |
| **Holding** | Tenedoras de acciones |
| **Foreign** | Sucursales de compañías extranjeras |

### 2.2 Recent News (2025-2026)
- **125,000+ companies** submitted 2024 financial statements
- **S.A.S.** showing exponential growth
- **6,000+ companies** dissolved/cancelled in 2025
- **87,000+ companies** exonerated from 2025 contribution

---

## 3. ANNUAL FINANCIAL STATEMENT OBLIGATIONS

### 3.1 Submission Deadline
| Attribute | Value |
|:----------|:------|
| **Deadline** | **April 30** (extended in some provinces) |
| **Format** | XBRL / Portal submission |
| **Portal** | https://portal.supercias.gob.ec |

### 3.2 Required Financial Statements
1. **Estado de Situación Financiera** (Balance Sheet)
2. **Estado de Resultados Integral** (Income Statement)
3. **Estado de Flujos de Efectivo** (Cash Flow Statement)
4. **Estado de Cambios en el Patrimonio** (Equity Changes)
5. **Notas a los Estados Financieros** (Notes)

### 3.3 Accounting Standards
| Standard | Application |
|:---------|:------------|
| **NIIF Completas** | Large companies |
| **NIIF para PYMES** | Small/Medium companies |
| **NEC** | Historical (replaced by NIIF) |

---

## 4. CONTRIBUCIÓN SOCIETARIA (ANNUAL CONTRIBUTION)

### 4.1 Calculation Basis
- Based on **total assets** reported in financial statements
- Progressive scale by company size
- Exonerations for small companies (87K+ exonerated in 2025)

### 4.2 Payment Timeline
| Event | Deadline |
|:------|:---------|
| Financial statement submission | April 30 |
| Contribution calculation | Post-submission |
| Payment | Per RUC 9th digit cronogram |

---

## 5. AUDIT REQUIREMENTS

### 5.1 Mandatory External Audit
Required if company exceeds ANY of the following thresholds:

| Criterion | Threshold (2026) |
|:----------|:-----------------|
| **Total Assets** | > $4,000,000 |
| **Annual Revenue** | > $5,000,000 |
| **Number of Employees** | > 200 |

### 5.2 Audit Report Submission
- Due with financial statements (April 30)
- Must be certified by authorized auditor
- Include auditor's opinion

---

## 6. COMPANY REGISTRATION

### 6.1 Required for New Companies
1. Company constitution (escritura pública)
2. Appointment of legal representative
3. RUC registration (via SRI)
4. IESS employer registration

### 6.2 Company Modifications
- Capital increases/decreases
- Statute reforms
- Merger/spinoffs
- Dissolution

---

## 7. KEY SERVICES

| Service | Portal |
|:--------|:-------|
| Financial Statement Portal | https://portal.supercias.gob.ec |
| Company Existence Verification | https://appscvs1.supercias.gob.ec/portalinformacion |
| Legal Representative Query | Online portal |
| Document Certification | Physical offices |

---

## 8. PENALTIES

| Violation | Penalty |
|:----------|:--------|
| Late financial statements | Fines, disqualification |
| Failure to report | Dissolution proceedings |
| False information | Criminal liability |
| Late contribution payment | Interest + administrative fine |

---

## 9. SYSTEM IMPLEMENTATION NOTES

For `l10n_ec` ERP module:

1. **Chart of Accounts**: Must align with Supercias structure
2. **Financial Reports**: Generate NIIF-compliant statements
3. **XBRL Export**: Consider future integration
4. **Audit Trail**: Full traceability for auditors
5. **Thresholds**: Track asset/revenue/employees for audit requirement

---

## 10. ERP INTEGRATION CONSIDERATIONS

| Area | System Requirement |
|:-----|:-------------------|
| **COA** | NIIF-compliant account structure |
| **Trial Balance** | Export for Supercias portal |
| **Financial Statements** | Balance Sheet, Income Statement, etc. |
| **Audit Preparation** | Document retention, access log |

---

**Knowledge Base Entry ID**: KB-SUPERCIAS-001
**Verification Status**: VERIFIED from official website
**Legal Authority**: Ley de Compañías, Resoluciones SCVS
**Next Review Date**: 2027-04-01
