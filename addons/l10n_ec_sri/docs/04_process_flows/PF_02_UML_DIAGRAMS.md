# UML DIAGRAMS: PROCURE-TO-PAY
## Appendix to PF_02 - Professional UML Suite

**Document ID**: PF-02-UML | **Version**: 1.0 | **Date**: 2026-01-22

---

## 1. SEQUENCE DIAGRAM: Withholding Flow

```mermaid
sequenceDiagram
    autonumber
    participant AP as Accounts Payable
    participant Odoo as Odoo ERP
    participant Validator as 5-Day Validator
    participant SRI as SRI Web Service
    participant Vendor as Vendor

    AP->>Odoo: Register Vendor Invoice
    activate Odoo
    Odoo->>Odoo: Post Invoice
    Odoo->>Odoo: Identify Withholding Taxes

    AP->>Odoo: Create Retention
    Odoo->>Validator: Check 5-Day Rule
    activate Validator

    alt Within 5 Days
        Validator-->>Odoo: ✅ Valid
        deactivate Validator
        Odoo->>Odoo: Calculate IR Amount
        Odoo->>Odoo: Calculate IVA Retention
        Odoo->>Odoo: Generate Retention XML
        Odoo->>Odoo: Apply XAdES Signature
        Odoo->>SRI: validarComprobante(retention_xml)
        activate SRI
        SRI-->>Odoo: RECIBIDA
        Odoo->>SRI: autorizacionComprobante
        SRI-->>Odoo: AUTORIZADO + Auth#
        deactivate SRI
        Odoo->>Odoo: Create Journal Entry
        Odoo->>Odoo: Generate RIDE
        Odoo->>Vendor: Send Retention PDF+XML
        Odoo-->>AP: ✅ Retention Complete
    else > 5 Days
        Validator-->>Odoo: ❌ Rule Violated
        Odoo-->>AP: ⚠️ BLOCKED - 5-Day Rule
    end
    deactivate Odoo
```

---

## 2. STATE MACHINE: Vendor Bill + Retention Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Draft: Create Bill

    Draft --> Posted: action_post()
    Draft --> Cancelled: Cancel

    Posted --> RetentionPending: Withholding Required
    Posted --> ReadyToPay: No Withholding

    state RetentionProcess {
        RetentionPending --> RetentionDraft: Create Retention
        RetentionDraft --> RetentionSent: Send to SRI
        RetentionSent --> RetentionAuthorized: AUTORIZADO
        RetentionSent --> RetentionRejected: DEVUELTA
        RetentionRejected --> RetentionDraft: Correct
    }

    RetentionAuthorized --> ReadyToPay: Retention Complete

    ReadyToPay --> PartialPaid: Partial Payment
    ReadyToPay --> Paid: Full Payment

    PartialPaid --> Paid: Complete Payment

    Paid --> [*]: Closed

    note right of RetentionPending: Must complete within 5 days
    note right of RetentionAuthorized: Journal entry created
```

---

## 3. ER DIAGRAM: Retention Data Model

```mermaid
erDiagram
    ACCOUNT_RETENTION ||--|| ACCOUNT_MOVE : "source_invoice"
    ACCOUNT_RETENTION ||--o{ ACCOUNT_RETENTION_LINE : "retention_lines"
    ACCOUNT_RETENTION ||--|| RES_PARTNER : "vendor"
    ACCOUNT_RETENTION_LINE ||--|| ACCOUNT_TAX : "tax"
    ACCOUNT_RETENTION ||--o| SRI_AUTHORIZATION : "sri_auth"

    ACCOUNT_RETENTION {
        int id PK
        int invoice_id FK
        int partner_id FK
        string name "Retention Number"
        date date
        date invoice_date "Source Invoice Date"
        string state "draft/sent/authorized/cancelled"
        string l10n_ec_clave_acceso
        string l10n_ec_numero_autorizacion
        float amount_total
        boolean within_5_days "Computed"
    }

    ACCOUNT_RETENTION_LINE {
        int id PK
        int retention_id FK
        int tax_id FK
        string tax_type "ir/iva"
        string code "303/312/etc"
        float base
        float percentage
        float amount
    }

    ACCOUNT_TAX {
        int id PK
        string name
        string l10n_ec_code "303-340"
        float amount "Percentage"
        string type_tax_use "purchase"
        string l10n_ec_type "ir_ret/iva_ret"
    }

    ACCOUNT_MOVE {
        int id PK
        string name
        date invoice_date
        float amount_total
        float amount_untaxed
        int partner_id FK
    }
```

---

## 4. ACTIVITY DIAGRAM: 3-Way Match Process

```mermaid
flowchart TB
    A([Start]) --> B[Receive Vendor Invoice]
    B --> C[Find Related PO]
    C --> D{PO Found?}
    D -->|No| E[Manual Entry]
    D -->|Yes| F[Find Related Receipt]
    F --> G{Receipt Found?}
    G -->|No| H[Wait for Goods]
    H --> F

    G -->|Yes| I[Compare Quantities]
    I --> J{Qty Match?}
    J -->|No, Under| K[Partial Invoice]
    J -->|No, Over| L[Discrepancy Alert]
    L --> M[AP Investigation]
    M --> N{Resolved?}
    N -->|No| O[Escalate to Manager]
    O --> N
    N -->|Yes| P[Adjust or Approve]

    J -->|Yes| Q[Compare Prices]
    K --> Q
    P --> Q

    Q --> R{Price Match ±2%?}
    R -->|No| S[Price Variance Alert]
    S --> T[Approve or Reject]
    T -->|Reject| U([End - Return Invoice])
    T -->|Approve| V[Accept Variance]

    R -->|Yes| V
    V --> W[Post Invoice]
    W --> X[Create Withholding]
    X --> Y([End - Ready for Payment])
```

---

## 5. TIMING DIAGRAM: 5-Day Rule

```mermaid
gantt
    title Retention 5-Day Rule Timeline
    dateFormat YYYY-MM-DD

    section Invoice
    Invoice Date        :milestone, m1, 2026-01-15, 0d

    section Retention Window
    Day 1 (Safe)        :active, d1, 2026-01-15, 1d
    Day 2 (Safe)        :active, d2, 2026-01-16, 1d
    Day 3 (Warning)     :active, d3, 2026-01-17, 1d
    Day 4 (Urgent)      :crit, d4, 2026-01-18, 1d
    Day 5 (Critical)    :crit, d5, 2026-01-19, 1d

    section Deadline
    Deadline Expires    :milestone, m2, 2026-01-20, 0d
```

---

## 6. COMPONENT DIAGRAM: P2P Integration

```mermaid
flowchart LR
    subgraph Purchasing
        A[purchase.order]
    end

    subgraph Inventory
        B[stock.picking]
        C[stock.move]
    end

    subgraph Accounting
        D[account.move]
        E[account.retention]
        F[account.payment]
    end

    subgraph SRI
        G[Retention XML]
        H[SRI SOAP]
    end

    A --> B
    B --> C
    A --> D
    C --> D
    D --> E
    E --> G
    G --> H
    D --> F
```

---

**UML Classification**: ISO 19501 / UML 2.5 Compliant
