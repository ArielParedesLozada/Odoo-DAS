# UML DIAGRAMS: CUSTOMS IMPORT
## Appendix to PF_04 - Professional UML Suite

**Document ID**: PF-04-UML | **Version**: 1.0 | **Date**: 2026-01-22

---

## 1. SEQUENCE DIAGRAM: Import Process

```mermaid
sequenceDiagram
    autonumber
    participant Pur as Purchasing
    participant Odoo as Odoo ERP
    participant Broker as Customs Broker
    participant SENAE as SENAE/Ecuapass
    participant Bank as Bank
    participant WH as Warehouse

    Pur->>Odoo: Create International PO (purchase.order)
    Odoo->>Odoo: Set Incoterm (FOB/CIF)
    Odoo->>Odoo: Set Fiscal Position: Importación
    Pur->>Odoo: Confirm PO

    Note over Odoo,Broker: Supplier ships goods

    Broker->>SENAE: Submit DAI via Ecuapass
    SENAE->>SENAE: Risk Analysis (Aforo)

    alt Aforo Automático
        SENAE-->>Broker: Auto Release
    else Aforo Documental
        SENAE->>Broker: Request Documents
        Broker->>SENAE: Submit Documents
        SENAE-->>Broker: Release
    else Aforo Físico
        SENAE->>WH: Physical Inspection
        WH-->>SENAE: Inspection Complete
        SENAE-->>Broker: Release
    end

    SENAE->>Broker: Liquidation (Duties Calculated)
    Broker->>Odoo: Enter Duty Amounts

    Odoo->>Odoo: Create Landed Cost (stock.landed.cost)
    Odoo->>Odoo: Calculate: AD-VALOREM + FODINFA + ICE + IVA

    Pur->>Bank: Pay Customs Duties
    Bank-->>SENAE: Payment Confirmed
    SENAE-->>Broker: Release Order

    WH->>Odoo: Receive Goods (stock.picking)
    Odoo->>Odoo: Apply Landed Cost to Products
    Odoo->>Odoo: Create Journal Entry
    Odoo-->>Pur: ✅ Import Complete
```

---

## 2. STATE MACHINE: Import Document Lifecycle

```mermaid
stateDiagram-v2
    [*] --> POCreated: Create International PO

    POCreated --> POConfirmed: Confirm PO

    POConfirmed --> InTransit: Goods Shipped

    InTransit --> AtCustoms: Arrived at Port

    AtCustoms --> AforoAssigned: SENAE Risk Analysis

    state AforoType {
        AforoAssigned --> Automatico: Low Risk
        AforoAssigned --> Documental: Medium Risk
        AforoAssigned --> Fisico: High Risk
    }

    Automatico --> DutiesCalculated: Auto Liquidation
    Documental --> DutiesCalculated: After Doc Review
    Fisico --> DutiesCalculated: After Inspection

    DutiesCalculated --> DutiesPaid: Pay via Bank

    DutiesPaid --> Released: Release Order Issued

    Released --> GoodsReceived: Warehouse Receipt

    GoodsReceived --> LandedCostApplied: Allocate Costs

    LandedCostApplied --> [*]: Complete

    note right of DutiesCalculated: AD-VAL + FODINFA + ICE + IVA
    note right of LandedCostApplied: Product cost updated
```

---

## 3. ER DIAGRAM: Import Data Model (Odoo 18)

```mermaid
erDiagram
    PURCHASE_ORDER ||--o{ PURCHASE_ORDER_LINE : "lines"
    PURCHASE_ORDER ||--o{ STOCK_PICKING : "receipts"
    PURCHASE_ORDER ||--|| RES_PARTNER : "supplier"
    STOCK_PICKING ||--o{ STOCK_MOVE : "moves"
    STOCK_LANDED_COST ||--o{ STOCK_LANDED_COST_LINE : "cost_lines"
    STOCK_LANDED_COST ||--o{ STOCK_PICKING : "pickings"
    STOCK_LANDED_COST ||--|| ACCOUNT_MOVE : "journal_entry"

    PURCHASE_ORDER {
        int id PK
        string name "PO/2026/00001"
        int partner_id FK
        date date_order
        date date_planned
        string state "draft/purchase/done"
        string incoterm_id "FOB/CIF/EXW"
        int fiscal_position_id "Importación"
        string currency_id
        float amount_total
    }

    PURCHASE_ORDER_LINE {
        int id PK
        int order_id FK
        int product_id FK
        float product_qty
        float price_unit
        float qty_received
        float qty_invoiced
    }

    STOCK_PICKING {
        int id PK
        int purchase_id FK
        string name "WH/IN/00001"
        string state "assigned/done"
        date scheduled_date
        date date_done
        int location_dest_id FK
    }

    STOCK_MOVE {
        int id PK
        int picking_id FK
        int product_id FK
        float product_uom_qty
        float quantity_done
        float price_unit "Updated by landed cost"
    }

    STOCK_LANDED_COST {
        int id PK
        string name "LC/2026/00001"
        date date
        string state "draft/done/cancel"
        float amount_total
    }

    STOCK_LANDED_COST_LINE {
        int id PK
        int cost_id FK
        int product_id FK
        string name "AD-VALOREM/FODINFA/IVA"
        string split_method "by_quantity/by_weight/by_value"
        float price_unit
    }

    ACCOUNT_MOVE {
        int id PK
        string name "Journal Entry"
        date date
        float amount_total
    }
```

---

## 4. ACTIVITY DIAGRAM: Duty Calculation

```mermaid
flowchart TB
    A([Start]) --> B[Get FOB Value]
    B --> C[Get Freight Cost]
    C --> D[Get Insurance Cost]
    D --> E[Calculate CIF]
    E --> F["CIF = FOB + Freight + Insurance"]

    F --> G[Lookup HS Code]
    G --> H[Get Tariff Rate]
    H --> I["AD-VALOREM = CIF × Tariff%"]

    I --> J["FODINFA = CIF × 0.5%"]

    J --> K{Product has ICE?}
    K -->|No| L[ICE = 0]
    K -->|Yes| M["ICE = (CIF + AD-VAL + FODINFA) × ICE%"]

    L --> N["Base IVA = CIF + AD-VAL + FODINFA + ICE"]
    M --> N

    N --> O["IVA = Base IVA × 15%"]

    O --> P["TOTAL DUTIES = AD-VAL + FODINFA + ICE + IVA"]

    P --> Q[Create Landed Cost Lines]
    Q --> R[Allocate to Products]
    R --> S([End])
```

---

## 5. CLASS DIAGRAM: Landed Cost Allocation

```mermaid
classDiagram
    class StockLandedCost {
        +String name
        +Date date
        +String state
        +compute_landed_cost()
        +button_validate()
    }

    class StockLandedCostLine {
        +String name
        +String split_method
        +Float price_unit
        +get_valuation_lines()
    }

    class SplitMethod {
        <<enumeration>>
        by_quantity
        by_weight
        by_volume
        by_current_cost_price
        equal
    }

    StockLandedCost "1" *-- "*" StockLandedCostLine
    StockLandedCostLine --> SplitMethod

    class AdValoremLine {
        +split_method = "by_current_cost_price"
    }

    class FodinfaLine {
        +split_method = "by_current_cost_price"
    }

    class FreightLine {
        +split_method = "by_weight"
    }

    class InsuranceLine {
        +split_method = "by_current_cost_price"
    }

    StockLandedCostLine <|-- AdValoremLine
    StockLandedCostLine <|-- FodinfaLine
    StockLandedCostLine <|-- FreightLine
    StockLandedCostLine <|-- InsuranceLine
```

---

**UML Classification**: ISO 19501 / UML 2.5 Compliant
**Odoo Version**: 18.0 (Canonical Model Names)
