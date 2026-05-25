# PROCESS FLOW: POS DAILY OPERATIONS
## PF_05 - Point of Sale Ecuador Compliance

**Document ID**: PF-005 | **Version**: 1.0 | **Date**: 2026-01-22
**Owner**: Retail Operations Manager (Expert Crew)

---

## 1. SWIMLANE DIAGRAM

```mermaid
flowchart TB
    subgraph Opening["Store Opening"]
        A[Open POS Session] --> B[Count Cash Drawer]
        B --> C[Confirm Opening Balance]
    end

    subgraph Sales["Sales Transactions"]
        C --> D[Customer Arrives]
        D --> E{ID Provided?}
        E -->|Yes| F[Enter RUC/Cédula]
        E -->|No| G{Total > $50?}
        G -->|No| H[Consumidor Final]
        G -->|Yes| I[Request ID Required]
        F --> J[Add Products]
        H --> J
        J --> K[Apply Discounts]
        K --> L{Payment Method}
        L -->|Cash| M[Receive Cash]
        L -->|Card| N[Process Card]
        L -->|Transfer| O[Verify Transfer]
        M --> P[Generate Electronic Invoice]
        N --> P
        O --> P
        P --> Q[Print RIDE]
        Q --> D
    end

    subgraph Closing["Store Closing"]
        D --> R[End Session]
        R --> S[Count Cash Drawer]
        S --> T{Match Expected?}
        T -->|Yes| U[Close Session]
        T -->|No| V[Report Discrepancy]
        V --> W[Manager Approval]
        W --> U
        U --> X[Generate Z Report]
    end
```

---

## 2. CONSUMIDOR FINAL RULES

| Total Venta | Requirement | Invoice Type |
|:------------|:------------|:-------------|
| ≤ $50.00 | No ID needed | Consumidor Final |
| > $50.00 | ID Required | Named invoice |

> [!WARNING]
> Sistema bloquea ventas > $50 sin identificación.

---

## 3. KPIs

| Metric | Target |
|:-------|:-------|
| Transaction Time | < 2 min |
| SRI Sync | < 30 sec |
| Daily Closure | 100% reconciled |

---

**Process Classification**: ISO 9001:2015 Controlled
