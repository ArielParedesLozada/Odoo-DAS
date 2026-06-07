# UML DIAGRAMS: POS OPERATIONS
## Appendix to PF_05 - Professional UML Suite

**Document ID**: PF-05-UML | **Version**: 1.0 | **Date**: 2026-01-22

---

## 1. SEQUENCE DIAGRAM: POS Sale Transaction

```mermaid
sequenceDiagram
    autonumber
    participant Cashier as Cashier
    participant POS as pos.session
    participant Order as pos.order
    participant SRI as SRI API
    participant Customer as Customer

    Cashier->>POS: Open Session (pos.session)
    POS->>POS: Prompt Opening Balance
    Cashier->>POS: Enter Cash Count
    POS->>POS: state = 'opened'

    loop Each Sale
        Customer->>Cashier: Request Products
        Cashier->>Order: Create pos.order
        Cashier->>Order: Scan/Add Products

        alt Total > $50
            Order->>Order: Check Partner
            alt No Partner
                Order-->>Cashier: ⚠️ ID Required
                Cashier->>Order: Enter RUC/Cédula
                Order->>Order: Validate with stdnum
            end
        else Total ≤ $50
            Order->>Order: Use Consumidor Final
        end

        Cashier->>Order: Select Payment Method
        Order->>Order: Process Payment
        Order->>Order: Validate Order (action_pos_order_done)

        Order->>SRI: Generate & Send Invoice XML
        SRI-->>Order: AUTORIZADO

        Order->>Order: Generate RIDE
        Order->>Cashier: Print Receipt
        Cashier->>Customer: Deliver Receipt
    end

    Cashier->>POS: Close Session
    POS->>POS: Prompt Closing Count
    Cashier->>POS: Enter Cash Count
    POS->>POS: Calculate Difference
    POS->>POS: Generate Z Report
    POS->>POS: state = 'closed'
```

---

## 2. STATE MACHINE: POS Session Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Opening: Start Session

    Opening --> Opened: Confirm Opening Balance

    Opened --> Opened: Process Orders

    Opened --> Closing: End Session

    Closing --> ClosingControl: Enter Closing Balance

    ClosingControl --> Validated: Balance Match
    ClosingControl --> Discrepancy: Balance Mismatch

    Discrepancy --> ManagerReview: Escalate
    ManagerReview --> Validated: Approved
    ManagerReview --> Opened: Rejected - Recount

    Validated --> Closed: Generate Z Report

    Closed --> [*]: Session Complete

    note right of Opening: Cash drawer count required
    note right of Discrepancy: Requires manager PIN
    note right of Closed: All journals posted
```

---

## 3. STATE MACHINE: POS Order Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Draft: New Order

    Draft --> Draft: Add/Remove Lines

    Draft --> Invoiced: action_pos_order_done()
    Draft --> Cancelled: Cancel

    state InvoiceFlow {
        Invoiced --> XMLGenerated: Generate XML
        XMLGenerated --> SRISent: Send to SRI
        SRISent --> Authorized: AUTORIZADO
        SRISent --> SRIError: DEVUELTA
        SRIError --> XMLGenerated: Retry
    }

    Authorized --> Printed: Print RIDE

    Printed --> Done: Delivered to Customer

    Done --> [*]: Complete

    note right of Invoiced: creates account.move
    note right of Authorized: invoice marked autorizado_sri=True
```

---

## 4. ER DIAGRAM: POS Data Model (Odoo 18)

```mermaid
erDiagram
    POS_SESSION ||--o{ POS_ORDER : "orders"
    POS_SESSION ||--|| POS_CONFIG : "config"
    POS_SESSION ||--|| RES_USERS : "user"
    POS_ORDER ||--o{ POS_ORDER_LINE : "lines"
    POS_ORDER ||--|| RES_PARTNER : "customer"
    POS_ORDER ||--|| ACCOUNT_MOVE : "invoice"
    POS_ORDER ||--o{ POS_PAYMENT : "payments"
    POS_PAYMENT ||--|| POS_PAYMENT_METHOD : "method"

    POS_CONFIG {
        int id PK
        string name "POS Store 1"
        int journal_id FK
        int l10n_ec_emission_point
        int stock_location_id FK
        boolean iface_fiscal_printer
        float l10n_ec_cf_limit "50.00"
    }

    POS_SESSION {
        int id PK
        int config_id FK
        int user_id FK
        string name "POS/2026/00001"
        string state "opening/opened/closing/closed"
        datetime start_at
        datetime stop_at
        float cash_register_balance_start
        float cash_register_balance_end
        float cash_register_balance_end_real
        float cash_register_difference
    }

    POS_ORDER {
        int id PK
        int session_id FK
        int partner_id FK
        int account_move_id FK
        string name "Order 00001-001-0001"
        datetime date_order
        string state "draft/paid/done/invoiced/cancel"
        float amount_total
        float amount_tax
        float amount_paid
        boolean is_consumidor_final
    }

    POS_ORDER_LINE {
        int id PK
        int order_id FK
        int product_id FK
        float qty
        float price_unit
        float discount
        float price_subtotal
        float price_subtotal_incl
    }

    POS_PAYMENT {
        int id PK
        int pos_order_id FK
        int payment_method_id FK
        float amount
    }

    POS_PAYMENT_METHOD {
        int id PK
        string name "Cash/Card/Transfer"
        int journal_id FK
        boolean is_cash_count
    }

    ACCOUNT_MOVE {
        int id PK
        string state
        string l10n_ec_sri_state
        string l10n_ec_clave_acceso
    }
```

---

## 5. ACTIVITY DIAGRAM: Consumidor Final Check

```mermaid
flowchart TB
    A([Start Sale]) --> B[Add Products to Order]
    B --> C[Calculate Total]
    C --> D{Total > $50?}

    D -->|No| E[Use Consumidor Final]
    E --> F[Set partner = CF (9999999999999)]

    D -->|Yes| G{Partner Assigned?}
    G -->|Yes| H{Partner has valid RUC/CI?}
    H -->|Yes| I[Proceed with Partner]
    H -->|No| J[⚠️ Update Partner ID]

    G -->|No| K[Prompt: Enter RUC/Cédula]
    K --> L[Validate with stdnum]
    L --> M{Valid?}
    M -->|No| N[Show Error - Retry]
    N --> K
    M -->|Yes| O[Create/Select Partner]
    O --> I
    J --> L

    F --> P[Process Payment]
    I --> P

    P --> Q[Generate Invoice]
    Q --> R([End])
```

---

**UML Classification**: ISO 19501 / UML 2.5 Compliant
**Odoo Version**: 18.0 (Canonical Model Names)
