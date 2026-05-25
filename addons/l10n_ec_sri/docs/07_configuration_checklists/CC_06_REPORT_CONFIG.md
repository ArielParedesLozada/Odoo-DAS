# CONFIGURATION CHECKLIST: REPORT CONFIGURATION
## CC_06 - Tax Reports & ATS Setup

**Document ID**: CC-006 | **Version**: 1.0 | **Date**: 2026-01-22
**Owner**: Implementation Lead

---

## 1. ATS CONFIGURATION

| Setting | Value | Verify |
|:--------|:------|:-------|
| Company RUC | 13 digits | ☐ |
| Razón Social | Official name | ☐ |
| Establishment # | 001 | ☐ |
| Generation Schedule | Monthly auto | ☐ |

---

## 2. FORM 103/104 CONFIG

| Field | Setting | Verify |
|:------|:--------|:-------|
| IR Withholding Codes | All mapped | ☐ |
| IVA Withholding Codes | All mapped | ☐ |
| Auto-calculate | ✅ Enabled | ☐ |

---

## 3. SUPERCIAS REPORTS

| Report | Format | Verify |
|:-------|:-------|:-------|
| Balance General | XBRL | ☐ |
| Estado Resultados | XBRL | ☐ |
| Flujo Efectivo | XBRL | ☐ |

---

## 4. VERIFICATION

| # | Test | Expected | Passed |
|:--|:-----|:---------|:-------|
| 1 | Generate ATS | Valid XML | ☐ |
| 2 | ATS purchases | All included | ☐ |
| 3 | ATS sales | All included | ☐ |
| 4 | Form 103 data | Correct totals | ☐ |

---

**Configuration Classification**: ISO 9001:2015 Controlled
