# TEST SPECIFICATION: INVENTORY
## TS_05 - Stock Management Ecuador

**Document ID**: TS-005 | **Version**: 1.0 | **Date**: 2026-01-22
**Owner**: QA Lead

---

## TEST CASES

| ID | Test Case | Input | Expected | Criteria |
|:---|:----------|:------|:---------|:---------|
| TS-05-01 | Goods Receipt | PO validated | Stock updated | Qty matches |
| TS-05-02 | Quality Reject | Reject items | Return created | Stock not added |
| TS-05-03 | Picking Order | SO confirmed | Pick list generated | Items listed |
| TS-05-04 | Partial Pick | Pick 5 of 10 | Backorder created | Both recorded |
| TS-05-05 | Guía Remisión | Delivery out | XML generated | SRI format |
| TS-05-06 | Guía Authorization | Send to SRI | Authorized | Status updated |
| TS-05-07 | Internal Transfer | Move between warehouses | Both stocks updated | Balanced |
| TS-05-08 | Inventory Count | Physical count | Adjustment proposed | Difference shown |
| TS-05-09 | Inventory Adjust | Confirm adjustment | Journal entry | GL balanced |
| TS-05-10 | Lot Tracking | Receive with lot | Lot recorded | Traceable |
| TS-05-11 | Serial Tracking | Receive with serial | Serial unique | No duplicates |
| TS-05-12 | Expiry Date | Set expiry | Alert before expiry | Warning shown |
| TS-05-13 | Negative Stock | Sell more than available | Blocked/Warning | Config dependent |
| TS-05-14 | Valuation FIFO | Multiple costs | FIFO applied | Cost correct |
| TS-05-15 | Stock Report | Generate report | Accurate quantities | Matches physical |

---

**Test Specification Classification**: ISO 9001:2015 Controlled
