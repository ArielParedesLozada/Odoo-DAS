# CONFIGURATION CHECKLIST: CUSTOMS SETUP
## CC_05 - Import/Export Ecuador (SENAE)

**Document ID**: CC-005 | **Version**: 1.0 | **Date**: 2026-01-22
**Owner**: Implementation Lead

---

## 1. PRE-REQUISITES

| # | Item | Status |
|:--|:-----|:-------|
| 1 | Multi-currency enabled | ☐ |
| 2 | Landed cost module installed | ☐ |
| 3 | Import supplier accounts | ☐ |

---

## 2. TAX CONFIGURATION

| Tax | Rate | Account | Verify |
|:----|:-----|:--------|:-------|
| Ad-Valorem | Variable (5-40%) | 1.1.5.01 | ☐ |
| FODINFA | 0.5% | 1.1.5.02 | ☐ |
| ICE Import | Variable | 1.1.5.03 | ☐ |
| IVA Import | 15% | 1.1.2.01 (credit) | ☐ |

---

## 3. LANDED COST TYPES

| Type | Allocation | Account | Verify |
|:-----|:-----------|:--------|:-------|
| Freight | By Weight | 1.1.5.10 | ☐ |
| Insurance | By Value | 1.1.5.11 | ☐ |
| Customs Duties | By Value | 1.1.5.12 | ☐ |
| Broker Fee | Equal | 1.1.5.13 | ☐ |

---

## 4. INCOTERMS

| Incoterm | Use Case | Verify |
|:---------|:---------|:-------|
| FOB | Supplier delivers to port | ☐ |
| CIF | Supplier includes freight+ins | ☐ |
| EXW | Pick up at supplier | ☐ |
| DDP | Delivered duty paid | ☐ |

---

## 5. VERIFICATION

| # | Test | Expected | Passed |
|:--|:-----|:---------|:-------|
| 1 | Create import PO (USD) | Converted | ☐ |
| 2 | Receive goods | Stock updated | ☐ |
| 3 | Create landed cost | Duties allocated | ☐ |
| 4 | Check product cost | Includes duties | ☐ |
| 5 | IVA credit recorded | 1.1.2.01 debit | ☐ |

---

**Configuration Classification**: ISO 9001:2015 Controlled
