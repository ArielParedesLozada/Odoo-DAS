# PROCESS FLOW: INVENTORY CYCLE
## PF_06 - Stock Management Ecuador

**Document ID**: PF-006 | **Version**: 1.0 | **Date**: 2026-01-22
**Owner**: Warehouse Manager (Expert Crew)

---

## 1. SWIMLANE DIAGRAM

```mermaid
flowchart TB
    subgraph Receiving["Goods Receipt"]
        A[PO Confirmed] --> B[Goods Arrive]
        B --> C[Quality Check]
        C --> D{OK?}
        D -->|No| E[Return/Claim]
        D -->|Yes| F[Validate Receipt]
        F --> G[Update Stock]
    end

    subgraph Picking["Order Fulfillment"]
        G --> H[Sales Order Confirmed]
        H --> I[Generate Picking]
        I --> J[Pick Products]
        J --> K[Validate Picking]
        K --> L{Guía Remisión Required?}
        L -->|Yes| M[Generate Guía Remisión]
        L -->|No| N[Direct Delivery]
        M --> O[Print/Sign Guía]
        O --> P[Ship to Customer]
        N --> P
    end

    subgraph Inventory["Inventory Control"]
        G --> Q[Schedule Count]
        Q --> R[Physical Count]
        R --> S{Discrepancy?}
        S -->|No| T[Confirm Count]
        S -->|Yes| U[Investigate]
        U --> V[Adjust Inventory]
        V --> W[Journal Entry]
    end
```

---

## 2. GUÍA DE REMISIÓN RULES

| Scenario | Required? |
|:---------|:----------|
| Sale with delivery | ✅ Always |
| Internal transfer | ✅ If different locations |
| Customer returns | ✅ Document required |

---

## 3. ACCOUNTING ENTRIES

```
Goods Receipt:
  Debit:  1.1.3.01 Inventario
  Credit: 2.1.1.01 Cuentas x Pagar

Inventory Adjustment (Shortage):
  Debit:  5.1.9.01 Pérdida Inventario
  Credit: 1.1.3.01 Inventario
```

---

**Process Classification**: ISO 9001:2015 Controlled
