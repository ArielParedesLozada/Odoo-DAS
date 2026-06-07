# CONFIGURATION CHECKLIST: POS SETUP
## CC_04 - Point of Sale Ecuador

**Document ID**: CC-004 | **Version**: 1.0 | **Date**: 2026-01-22
**Owner**: Implementation Lead

---

## 1. PRE-REQUISITES

| # | Item | Status |
|:--|:-----|:-------|
| 1 | SRI setup complete | ☐ |
| 2 | Products configured | ☐ |
| 3 | Payment methods defined | ☐ |
| 4 | Receipt printer configured | ☐ |

---

## 2. POS CONFIGURATION

| Setting | Value | Verify |
|:--------|:------|:-------|
| POS Name | Store location | ☐ |
| Warehouse | Linked warehouse | ☐ |
| Pricelist | Default price list | ☐ |
| Invoice Journal | Facturas POS | ☐ |
| Emission Point | 002 (or dedicated) | ☐ |

---

## 3. CONSUMIDOR FINAL SETTINGS

| Setting | Value | Verify |
|:--------|:------|:-------|
| Enable CF Limit | ✅ Yes | ☐ |
| CF Limit Amount | $50.00 | ☐ |
| CF Identification | 9999999999999 | ☐ |
| Block if > $50 no ID | ✅ Yes | ☐ |

---

## 4. PAYMENT METHODS

| Method | Account | Verify |
|:-------|:--------|:-------|
| Cash | 1.1.1.01 Caja | ☐ |
| Credit Card | 1.1.1.04 Tarjetas | ☐ |
| Debit Card | 1.1.1.04 Tarjetas | ☐ |
| Bank Transfer | 1.1.1.02 Bancos | ☐ |

---

## 5. RECEIPT/INVOICE

| Setting | Value | Verify |
|:--------|:------|:-------|
| Auto-Invoice | ✅ Yes | ☐ |
| Print RIDE | ✅ Yes | ☐ |
| Paper Format | Thermal 80mm | ☐ |
| Include Logo | ✅ Yes | ☐ |

---

## 6. VERIFICATION

| # | Test | Expected | Passed |
|:--|:-----|:---------|:-------|
| 1 | Open POS session | Cash prompt | ☐ |
| 2 | Sale $45 no ID | CF accepted | ☐ |
| 3 | Sale $60 no ID | Blocked | ☐ |
| 4 | Sale $60 with ID | Accepted | ☐ |
| 5 | Print receipt | RIDE OK | ☐ |
| 6 | Close session | Z Report | ☐ |

---

**Configuration Classification**: ISO 9001:2015 Controlled
