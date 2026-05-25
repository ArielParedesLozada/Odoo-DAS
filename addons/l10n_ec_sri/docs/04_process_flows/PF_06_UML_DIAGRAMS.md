# UML DIAGRAMS: INVENTORY CYCLE
## Appendix to PF_06 - Professional UML Suite

**Document ID**: PF-06-UML | **Version**: 1.0 | **Date**: 2026-01-22

---

## 1. SEQUENCE DIAGRAM: Goods Receipt & Delivery

```mermaid
sequenceDiagram
    autonumber
    participant Sales as Sales
    participant Odoo as Odoo ERP
    participant WH as Warehouse
    participant SRI as SRI API
    participant Customer as Customer

    Note over Odoo: RECEIVING
    Odoo->>WH: Notify: Incoming Shipment
    WH->>Odoo: Open stock.picking (IN)
    WH->>Odoo: Validate Quantities
    WH->>Odoo: button_validate()
    Odoo->>Odoo: Create stock.move entries
    Odoo->>Odoo: Update stock.quant
    Odoo-->>WH: ✅ Receipt Complete

    Note over Odoo: DELIVERY
    Sales->>Odoo: Confirm sale.order
    Odoo->>Odoo: Create stock.picking (OUT)
    Odoo->>WH: Notify: Delivery Order

    WH->>Odoo: Reserve Products
    WH->>Odoo: Pick Products
    WH->>Odoo: Pack Products

    WH->>Odoo: Check: Guía de Remisión Required?

    alt External Delivery
        Odoo->>Odoo: Generate Guía XML
        Odoo->>Odoo: XAdES Sign
        Odoo->>SRI: validarComprobante(guia_xml)
        SRI-->>Odoo: AUTORIZADO
        Odoo->>Odoo: Generate Guía RIDE
        WH->>Customer: Deliver with Guía
    else Same Location
        WH->>Customer: Direct Delivery
    end

    WH->>Odoo: button_validate()
    Odoo->>Odoo: Update stock.quant
    Odoo-->>Sales: ✅ Delivery Complete
```

---

## 2. STATE MACHINE: stock.picking Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Draft: Create Picking

    Draft --> Waiting: Confirm
    Draft --> Cancelled: Cancel

    Waiting --> Confirmed: Availability Check

    Confirmed --> Assigned: Reserve Stock
    Confirmed --> Waiting: Partial Reserve

    Assigned --> Done: button_validate()
    Assigned --> Confirmed: Unreserve

    state GuiaFlow {
        Assigned --> GuiaRequired: External Delivery
        GuiaRequired --> GuiaGenerated: Create XML
        GuiaGenerated --> GuiaSigned: XAdES Sign
        GuiaSigned --> GuiaAuthorized: SRI OK
        GuiaAuthorized --> Done: With Guía
    }

    Done --> [*]: Complete

    note right of Assigned: Products reserved in stock.quant
    note right of Done: stock.move.state = 'done'
```

---

## 3. STATE MACHINE: Guía de Remisión Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Draft: Create from Picking

    Draft --> Validated: Confirm Details

    Validated --> XMLGenerated: Render XML (codDoc='06')

    XMLGenerated --> Signed: XAdES-BES

    Signed --> Sent: validarComprobante()

    Sent --> Authorized: AUTORIZADO
    Sent --> Rejected: DEVUELTA

    Rejected --> XMLGenerated: Fix & Retry

    Authorized --> Printed: Generate RIDE

    Printed --> Delivered: With Shipment

    Delivered --> [*]: Complete

    note right of Authorized: numero_autorizacion stored
```

---

## 4. ER DIAGRAM: Inventory Data Model (Odoo 18)

```mermaid
erDiagram
    STOCK_PICKING ||--o{ STOCK_MOVE : "moves"
    STOCK_PICKING ||--|| STOCK_PICKING_TYPE : "type"
    STOCK_PICKING ||--o| L10N_EC_GUIA_REMISION : "guia"
    STOCK_MOVE ||--o{ STOCK_MOVE_LINE : "move_lines"
    STOCK_MOVE_LINE ||--|| STOCK_QUANT : "updates"
    STOCK_QUANT ||--|| PRODUCT_PRODUCT : "product"
    STOCK_QUANT ||--|| STOCK_LOCATION : "location"

    STOCK_PICKING {
        int id PK
        string name "WH/OUT/00001"
        int picking_type_id FK
        int partner_id FK
        string state "draft/waiting/confirmed/assigned/done/cancel"
        date scheduled_date
        date date_done
        int location_id FK
        int location_dest_id FK
    }

    STOCK_PICKING_TYPE {
        int id PK
        string name "Delivery/Receipt"
        string code "incoming/outgoing/internal"
        int default_location_src_id FK
        int default_location_dest_id FK
    }

    STOCK_MOVE {
        int id PK
        int picking_id FK
        int product_id FK
        string name
        float product_uom_qty
        float quantity_done
        string state "draft/waiting/confirmed/assigned/done/cancel"
        float price_unit
    }

    STOCK_MOVE_LINE {
        int id PK
        int move_id FK
        int product_id FK
        int lot_id FK
        float qty_done
        int location_id FK
        int location_dest_id FK
    }

    STOCK_QUANT {
        int id PK
        int product_id FK
        int location_id FK
        int lot_id FK
        float quantity
        float reserved_quantity
    }

    L10N_EC_GUIA_REMISION {
        int id PK
        int picking_id FK
        string name "001-001-000000123"
        date date
        string state "draft/authorized/cancelled"
        string l10n_ec_clave_acceso
        string l10n_ec_numero_autorizacion
        string dir_partida
        string dir_destinatario
        string ruc_transportista
        string placa
        date fecha_ini_transporte
        date fecha_fin_transporte
    }

    PRODUCT_PRODUCT {
        int id PK
        string name
        string default_code "SKU"
        string tracking "none/lot/serial"
        boolean l10n_ec_requires_guia
    }

    STOCK_LOCATION {
        int id PK
        string name
        string usage "internal/supplier/customer/inventory/transit"
    }
```

---

## 5. ACTIVITY DIAGRAM: Inventory Adjustment

```mermaid
flowchart TB
    A([Start Inventory]) --> B[Create stock.inventory]
    B --> C[Select Products/Locations]
    C --> D[action_start: Lock Quantities]

    D --> E[Physical Count]
    E --> F[Enter Counted Quantities]

    F --> G{Difference Found?}
    G -->|No| H[Confirm: No Changes]
    G -->|Yes| I[Calculate Adjustment]

    I --> J[Review Differences]
    J --> K{Approve?}
    K -->|No| L[Investigate]
    L --> F

    K -->|Yes| M[action_validate]
    M --> N[Create stock.move for Adjustment]
    N --> O[Update stock.quant]
    O --> P[Create account.move]

    H --> Q([End])
    P --> Q
```

---

## 6. COMPONENT DIAGRAM: Inventory System

```mermaid
flowchart LR
    subgraph Odoo["Odoo 18.0 Inventory"]
        A[stock.picking]
        B[stock.move]
        C[stock.quant]
        D[stock.inventory.line]
        E[stock.valuation.layer]
    end

    subgraph Ecuador["Ecuador Localization"]
        F[l10n_ec_guia_remision]
        G[SRI XML Generator]
        H[XAdES Signer]
    end

    subgraph Accounting["Accounting"]
        I[account.move]
        J[stock.landed.cost]
    end

    A --> B
    B --> C
    A --> F
    F --> G
    G --> H
    B --> E
    E --> I
    J --> E
```

---

**UML Classification**: ISO 19501 / UML 2.5 Compliant
**Odoo Version**: 18.0 (Canonical Model Names)
