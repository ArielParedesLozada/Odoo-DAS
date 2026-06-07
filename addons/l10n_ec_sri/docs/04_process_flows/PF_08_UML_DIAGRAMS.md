# UML DIAGRAMS: WITHHOLDING (RETENCIÓN)
## Appendix to PF_08 - Professional UML Suite

**Document ID**: PF-08-UML | **Version**: 1.0 | **Date**: 2026-01-22

---

## 1. SEQUENCE DIAGRAM: Withholding Authorization

```mermaid
sequenceDiagram
    autonumber
    participant AP as Accounts Payable
    participant Odoo as Odoo ERP
    participant Validator as Date Validator
    participant XAdES as XAdES Signer (Rust)
    participant SRI as SRI SOAP API
    participant Vendor as Vendor

    AP->>Odoo: Select Posted Vendor Bill
    Odoo->>Odoo: Load invoice.account_move
    AP->>Odoo: Create Retention (account.retention)

    Odoo->>Validator: validate_5_day_rule(invoice_date, today)
    activate Validator

    alt Within 5 Days
        Validator-->>Odoo: ✅ Valid
        deactivate Validator

        AP->>Odoo: Add Retention Lines
        Note over Odoo: IR Code 303: 10%<br>IVA Ret: 70%

        AP->>Odoo: Confirm Retention
        Odoo->>Odoo: Generate clave_acceso (codDoc='07')
        Odoo->>Odoo: Render retencion.xml (Jinja2)
        Odoo->>Odoo: Validate against retencion.xsd

        Odoo->>XAdES: sign_xml(xml, p12_cert)
        activate XAdES
        XAdES-->>Odoo: signed_xml
        deactivate XAdES

        Odoo->>SRI: validarComprobante(base64(signed_xml))
        activate SRI
        SRI-->>Odoo: {estado: 'RECIBIDA'}

        Odoo->>SRI: autorizacionComprobante(clave_acceso)
        SRI-->>Odoo: {estado: 'AUTORIZADO', numeroAutorizacion: '...'}
        deactivate SRI

        Odoo->>Odoo: Store authorization
        Odoo->>Odoo: Create journal_entry (account.move)
        Odoo->>Odoo: Reconcile with vendor bill
        Odoo->>Odoo: Generate RIDE PDF

        Odoo->>Vendor: Email XML + PDF
        Vendor-->>AP: Retention Received

    else > 5 Days
        Validator-->>Odoo: ❌ BLOCKED
        Odoo-->>AP: Error: 5-Day Rule Violated
    end
```

---

## 2. STATE MACHINE: Retention Document Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Draft: Create from Vendor Bill

    Draft --> Validated: Add lines & confirm
    Draft --> Cancelled: Cancel

    Validated --> DateCheck: Check 5-day rule

    DateCheck --> Blocked: > 5 days
    DateCheck --> XMLGeneration: ≤ 5 days

    Blocked --> [*]: Cannot proceed

    XMLGeneration --> Signed: XAdES-BES applied

    Signed --> Sent: validarComprobante()

    Sent --> Authorized: AUTORIZADO
    Sent --> Rejected: DEVUELTA

    Rejected --> XMLGeneration: Fix & Retry

    Authorized --> JournalCreated: Create account.move

    JournalCreated --> Delivered: Send to vendor

    Delivered --> [*]: Complete

    note right of DateCheck: invoice.invoice_date + 5 days
    note right of Authorized: numero_autorizacion stored
    note right of JournalCreated: Debit A/P, Credit Ret. Payable
```

---

## 3. ER DIAGRAM: Retention Data Model (Odoo 18)

```mermaid
erDiagram
    ACCOUNT_MOVE ||--o{ L10N_EC_WITHHOLDING : "source_bill"
    L10N_EC_WITHHOLDING ||--o{ L10N_EC_WITHHOLDING_LINE : "lines"
    L10N_EC_WITHHOLDING ||--|| RES_PARTNER : "vendor"
    L10N_EC_WITHHOLDING ||--o| ACCOUNT_MOVE : "journal_entry"
    L10N_EC_WITHHOLDING_LINE ||--|| ACCOUNT_TAX : "tax"

    ACCOUNT_MOVE {
        int id PK
        string name "Bill Number"
        date invoice_date
        float amount_total
        float amount_untaxed
        float amount_tax
        int partner_id FK
        string move_type "in_invoice"
        string state "posted"
    }

    L10N_EC_WITHHOLDING {
        int id PK
        int source_move_id FK "Vendor Bill"
        int partner_id FK
        int journal_entry_id FK "Created Journal"
        string name "001-001-000000123"
        date date "Emission Date"
        string state "draft/sent/authorized/cancelled"
        string l10n_ec_clave_acceso "49 digits"
        string l10n_ec_numero_autorizacion
        datetime l10n_ec_fecha_autorizacion
        float amount_ir_total
        float amount_iva_total
        float amount_total
        boolean within_5_days "Computed"
        binary xml_file
        binary ride_file
    }

    L10N_EC_WITHHOLDING_LINE {
        int id PK
        int withholding_id FK
        int tax_id FK
        string tax_type "ir/iva"
        string codigo_retencion "303/312/1/2/3"
        float base_imponible
        float porcentaje_retencion
        float valor_retenido
    }

    ACCOUNT_TAX {
        int id PK
        string name "Ret. Fuente 10%"
        string l10n_ec_code "303"
        float amount "10.0"
        string l10n_ec_type "withhold_income_tax"
        string type_tax_use "purchase"
    }

    RES_PARTNER {
        int id PK
        string name
        string vat "RUC"
        string l10n_latam_identification_type_id
        boolean l10n_ec_contribuyente_especial
        boolean supplier_rank
    }
```

---

## 4. ACTIVITY DIAGRAM: Rate Determination

```mermaid
flowchart TB
    A([Start]) --> B[Get Vendor Invoice]
    B --> C{Vendor is Contribuyente Especial?}

    C -->|Yes| D[No IR Withholding Required]
    C -->|No| E{Invoice Concept?}

    E -->|Professional Services| F[IR Code 303: 10%]
    E -->|General Services| G[IR Code 312: 10%]
    E -->|Goods Purchase| H[IR Code 310: 1%]
    E -->|Rent| I[IR Code 319: 8%]
    E -->|Transport| J[IR Code 309: 1%]
    E -->|Other| K[IR Code 343: 2%]

    F --> L{My Company is Withholding Agent?}
    G --> L
    H --> L
    I --> L
    J --> L
    K --> L
    D --> L

    L -->|No| M[No IVA Withholding]
    L -->|Yes| N{Invoice Has IVA?}

    N -->|No| M
    N -->|Yes| O{Concept Type?}

    O -->|Goods| P[IVA Ret: 30%]
    O -->|Services| Q[IVA Ret: 70%]
    O -->|Prof. Fees| R[IVA Ret: 100%]
    O -->|Liquidación| S[IVA Ret: 100%]

    P --> T[Create Withholding Lines]
    Q --> T
    R --> T
    S --> T
    M --> T

    T --> U([End - Ready to Emit])
```

---

## 5. COMPONENT DIAGRAM: Withholding System

```mermaid
flowchart LR
    subgraph Odoo["Odoo 18.0"]
        A[account.move<br>Vendor Bill]
        B[l10n_ec_withholding<br>Retention Model]
        C[l10n_ec_edi<br>XML Generation]
        D[XAdES Signer<br>Rust/PyO3]
        E[SRI Client<br>zeep SOAP]
    end

    subgraph External["External"]
        F[SRI SOAP API<br>validarComprobante]
        G[SRI SOAP API<br>autorizacionComprobante]
    end

    subgraph Outputs["Outputs"]
        H[XML File]
        I[RIDE PDF]
        J[Journal Entry]
    end

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    E --> G
    B --> H
    B --> I
    B --> J
```

---

## 6. TIMING DIAGRAM: 5-Day Rule Enforcement

```mermaid
gantt
    title Withholding 5-Day Rule Timeline
    dateFormat YYYY-MM-DD

    section Invoice
    Invoice Date            :milestone, inv, 2026-01-15, 0d

    section Safe Zone
    Day 1 - Create OK       :active, d1, 2026-01-15, 1d
    Day 2 - Create OK       :active, d2, 2026-01-16, 1d
    Day 3 - Warning         :active, d3, 2026-01-17, 1d

    section Danger Zone
    Day 4 - Urgent          :crit, d4, 2026-01-18, 1d
    Day 5 - Last Chance     :crit, d5, 2026-01-19, 1d

    section Blocked
    Day 6+ BLOCKED          :done, d6, 2026-01-20, 3d

    section System Alerts
    Warning Email           :milestone, w1, 2026-01-17, 0d
    Urgent Dashboard        :milestone, w2, 2026-01-18, 0d
    Block Enforcement       :milestone, w3, 2026-01-20, 0d
```

---

**UML Classification**: ISO 19501 / UML 2.5 Compliant
**Odoo Version**: 18.0 (Canonical Model Names)
