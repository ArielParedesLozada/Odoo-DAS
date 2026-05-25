# CONFIGURATION CHECKLIST: INVENTORY SETUP
## CC_03 - Stock Management Ecuador

**Document ID**: CC-003 | **Version**: 1.0 | **Date**: 2026-01-22
**Owner**: Implementation Lead

---

## 1. PRE-REQUISITES

| # | Item | Status |
|:--|:-----|:-------|
| 1 | Chart of Accounts configured | ☐ |
| 2 | SRI setup complete | ☐ |
| 3 | Warehouses defined | ☐ |

---

## 2. WAREHOUSE CONFIGURATION

| Setting | Value | Verify |
|:--------|:------|:-------|
| Warehouse Name | Per location | ☐ |
| Short Code | 3 letters (e.g., GYE) | ☐ |
| Address | Full address | ☐ |
| Routes | Buy/Manufacture/Pick | ☐ |

---

## 3. PRODUCT CONFIGURATION

| Field | Setting | Verify |
|:------|:--------|:-------|
| Can be Sold | ☐ Yes/No | ☐ |
| Can be Purchased | ☐ Yes/No | ☐ |
| Product Type | Storable/Consumable/Service | ☐ |
| Tracking | None/Lot/Serial | ☐ |
| Costing Method | FIFO/Average | ☐ |
| IVA Tax | 15% / 0% / Exempt | ☐ |

---

## 4. VALUATION

| Setting | Value | Verify |
|:--------|:------|:-------|
| Costing Method | FIFO (recommended) | ☐ |
| Inventory Valuation | Automated | ☐ |
| Stock Input Account | 1.1.5.01 | ☐ |
| Stock Output Account | 1.1.5.02 | ☐ |
| Stock Valuation Account | 1.1.3.01 | ☐ |
| Expense Account | 5.1.1.01 | ☐ |

---

## 5. GUÍA DE REMISIÓN

| Setting | Value | Verify |
|:--------|:------|:-------|
| Sequence | 001-001-XXXXXXXXX | ☐ |
| Emission Point | 001 | ☐ |
| Auto-generate on delivery | ☐ Yes | ☐ |
| Require signature | ☐ Yes | ☐ |

---

## 6. VERIFICATION

| # | Test | Expected | Passed |
|:--|:-----|:---------|:-------|
| 1 | Create product | Saved | ☐ |
| 2 | Receive goods | Stock + | ☐ |
| 3 | Deliver goods | Stock - | ☐ |
| 4 | Generate Guía | XML valid | ☐ |
| 5 | Check valuation | Cost correct | ☐ |

---

**Configuration Classification**: ISO 9001:2015 Controlled
