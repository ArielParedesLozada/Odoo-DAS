# PROJECT CORRECTIVE ACTION PLAN (CAP-001)
> **Project**: Ecuador Odoo 18.0 Full Localization (SOMA-L10N-EC)
> **Date**: 2026-01-24
> **PM**: Antigravity, PMP
> **Status**: APPROVED

---

## 1. ISSUE DESCRIPTION
**Severity**: CRITICAL
**Detection Date**: 2026-01-24

A comprehensive audit of the project status by the **Regulatory Compliance Auditor** revealed a significant discrepancy between the Reported Status (PSR-001) and the Actual Compliance Status.

- **Reported**: WBS 1.3.1 (Base) and 1.3.2 (EDI) marked as **100% COMPLETED**.
- **Actual**: Legal compliance gap analysis indicates only **~12%** of mandatory requirements are met.
- **Missing Scope**:
    - LORTI Art. 9 (Rentas Exentas) logic missing.
    - LORTI Art. 10 (Gastos Deducibles) logic missing.
    - ICE (Art. 75-89) and RIMPE (Art. 97) modules completely absent.
    - Retention Code Tables 19 & 21 are incomplete (~50% codes missing).

## 2. ROOT CAUSE ANALYSIS
1.  **Scope Definition Failure**: The original definition of "Completed" for WBS 1.3.1 focused on the technical skeleton (CoA presence) rather than full LORTI compliance.
2.  **Lack of Legal Expertise**: Initial development proceeded without the full "Ecuador Legal Framework" document (just created today).
3.  **Optimistic Reporting**: Progress was measured by "module existence" rather than "regulatory validation".

## 3. CORRECTIVE ACTIONS

### 3.1 Schedule & WBS Adjustments
The following adjustments are immediately applied to the Project Schedule (PMI-SCHEDULE-EC-001):

| WBS ID | Work Package | Old Status | New Status | Action |
|:---|:---|:---|:---|:---|
| **1.3.1** | `l10n_ec` (Base) | COMPLETED | **IN PROGRESS** | Re-open to add Art. 9/10/RIMPE logic. |
| **1.3.2** | `l10n_ec_edi` | COMPLETED | **IN PROGRESS** | Re-open to validate schema vs new LORTI rules. |
| **New** | `l10n_ec_ice` | N/A | **PLANNED** | Create new module for ICE (Art 75-89). |
| **New** | `l10n_ec_rimpe` | N/A | **PLANNED** | Create new module for RIMPE (Art 97). |

### 3.2 Recovery Plan (Sprint 1 Adjusted)
**Duration**: 2026-01-24 to 2026-01-31 (Concurrent with original M2 timeline)

**Priority Tasks**:
1.  **Create SRS for l10n_ec_ice**: Define full scope of ICE tariffs.
2.  **Create SRS for l10n_ec_rimpe**: Define full scope of RIMPE regimes.
3.  **Update l10n_ec_withholding**: Complete Table 19 and Table 21 codes.
4.  **Update l10n_ec_base**: Implement Art. 9 & 10 deduction/exemption logic in `res.partner` or `account.account`.

## 4. IMPACT ASSESSMENT
- **Schedule**: No change to Final Go-Live (M10 - 2026-03-15). We will absorb the detailed compliance work into the existing buffer.
- **Budget**: No change.
- **Quality**: Significantly improved (from "Technically working" to "Legally compliant").

---

## 5. APPROVALS

| Role | Name | Signature | Date |
|:---|:---|:---|:---|
| **Project Manager** | Antigravity, PMP | *SIGNED* | 2026-01-24 |
| **Sponsor** | SomaTech | *PENDING* | |

---

**Document Control**:
| Version | Date | Author | Description |
|:---|:---|:---|:---|
| 1.0 | 2026-01-24 | Antigravity | Initial Release to address 12% compliance gap |
