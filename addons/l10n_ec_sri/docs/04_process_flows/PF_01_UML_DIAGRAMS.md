# UML DIAGRAMS: INVOICE-TO-CASH
## Appendix to PF_01 - Professional UML Suite

**Document ID**: PF-01-UML | **Version**: 1.0 | **Date**: 2026-01-22

---

## 1. SEQUENCE DIAGRAM: Electronic Invoice Flow

```mermaid
sequenceDiagram
    autonumber
    participant User as Accountant
    participant Odoo as Odoo ERP
    participant SRI as SRI Web Service
    participant Email as Email Server
    participant Customer as Customer

    User->>Odoo: Validate Invoice
    activate Odoo
    Odoo->>Odoo: Generate Access Key (Módulo 11)
    Odoo->>Odoo: Render XML (Jinja2)
    Odoo->>Odoo: Validate XSD Schema
    Odoo->>Odoo: Apply XAdES-BES Signature
    Odoo->>SRI: validarComprobante(xml_base64)
    activate SRI
    SRI-->>Odoo: RECIBIDA / DEVUELTA
    deactivate SRI

    alt RECIBIDA
        Odoo->>SRI: autorizacionComprobante(claveAcceso)
        activate SRI
        SRI-->>Odoo: AUTORIZADO + numeroAutorizacion
        deactivate SRI
        Odoo->>Odoo: Store Authorization
        Odoo->>Odoo: Generate RIDE PDF + QR
        Odoo->>Email: Send XML + PDF
        Email->>Customer: Deliver Invoice
        Customer-->>Odoo: Delivery Confirmed
        Odoo-->>User: ✅ Invoice Authorized
    else DEVUELTA
        SRI-->>Odoo: Error Messages
        Odoo-->>User: ❌ Display Errors
        User->>Odoo: Correct and Retry
    end
    deactivate Odoo
```

---

## 2. STATE MACHINE: Invoice Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Draft: Create Invoice

    Draft --> Cancelled: Cancel
    Draft --> Posted: action_post()

    Posted --> PendingSRI: Generate XML

    PendingSRI --> SentSRI: validarComprobante()
    PendingSRI --> XMLError: XSD Validation Fail
    XMLError --> PendingSRI: Fix & Retry

    SentSRI --> Authorized: AUTORIZADO
    SentSRI --> Rejected: DEVUELTA
    Rejected --> PendingSRI: Correct & Retry

    Authorized --> PartialPayment: Receive Payment
    Authorized --> Authorized: Send Reminders

    PartialPayment --> Paid: Full Payment
    PartialPayment --> PartialPayment: Additional Payment

    Paid --> [*]: Closed

    Authorized --> CreditNoteIssued: Issue Credit Note
    CreditNoteIssued --> [*]: Reversed

    note right of Draft: l10n_ec_sri_state = 'draft'
    note right of Authorized: autorizado_sri = True
    note right of Paid: payment_state = 'paid'
```

---

## 3. ER DIAGRAM: Invoice Data Model

```mermaid
erDiagram
    ACCOUNT_MOVE ||--o{ ACCOUNT_MOVE_LINE : contains
    ACCOUNT_MOVE ||--|| RES_PARTNER : "invoiced_to"
    ACCOUNT_MOVE ||--o| L10N_LATAM_DOCUMENT_TYPE : "document_type"
    ACCOUNT_MOVE ||--o{ SRI_AUTHORIZATION : "authorizations"
    ACCOUNT_MOVE_LINE ||--|| ACCOUNT_ACCOUNT : "account"
    ACCOUNT_MOVE_LINE ||--o{ ACCOUNT_TAX : "taxes"
    RES_PARTNER ||--o| RES_COUNTRY : "country"

    ACCOUNT_MOVE {
        int id PK
        string name "Invoice Number"
        date invoice_date
        date date
        string move_type "out_invoice/in_invoice"
        string state "draft/posted/cancel"
        float amount_total
        float amount_untaxed
        float amount_tax
        string l10n_ec_sri_state "pending/sent/authorized/rejected"
        string l10n_ec_clave_acceso "49 digits"
        string l10n_ec_numero_autorizacion
        datetime l10n_ec_fecha_autorizacion
        boolean l10n_ec_autorizado_sri
        string l10n_ec_xml_file
        string l10n_ec_ride_file
    }

    ACCOUNT_MOVE_LINE {
        int id PK
        int move_id FK
        int account_id FK
        string name "Description"
        float quantity
        float price_unit
        float price_subtotal
        float price_total
        float debit
        float credit
    }

    RES_PARTNER {
        int id PK
        string name
        string vat "RUC/Cedula"
        string l10n_ec_id_type "ruc/cedula/pasaporte"
        boolean l10n_ec_contribuyente_especial
        boolean l10n_ec_obligado_contabilidad
        string street
        string city
        string email
    }

    SRI_AUTHORIZATION {
        int id PK
        int move_id FK
        string clave_acceso
        string numero_autorizacion
        datetime fecha_autorizacion
        string estado "AUTORIZADO/NO_AUTORIZADO"
        text xml_content
        text messages
    }

    L10N_LATAM_DOCUMENT_TYPE {
        int id PK
        string code "01/04/05/06/07"
        string name "Factura/NC/ND/Guia/Retencion"
    }
```

---

## 4. ACTIVITY DIAGRAM: SRI Authorization Process

```mermaid
flowchart TB
    A([Start]) --> B[Validate Invoice Data]
    B --> C{Data Valid?}
    C -->|No| D[Show Errors]
    D --> E([End - Fix Required])

    C -->|Yes| F[Generate Access Key]
    F --> G[Build XML from Template]
    G --> H[Validate Against XSD]
    H --> I{XSD Valid?}
    I -->|No| J[Log Schema Errors]
    J --> D

    I -->|Yes| K[Load P12 Certificate]
    K --> L[Apply XAdES-BES Signature]
    L --> M[Base64 Encode]
    M --> N[Call validarComprobante]
    N --> O{Response Status?}

    O -->|DEVUELTA| P[Parse Error Messages]
    P --> D

    O -->|RECIBIDA| Q[Wait 2 seconds]
    Q --> R[Call autorizacionComprobante]
    R --> S{Auth Status?}

    S -->|NO AUTORIZADO| T[Parse Rejection Reason]
    T --> D

    S -->|AUTORIZADO| U[Extract numeroAutorizacion]
    U --> V[Store in Database]
    V --> W[Generate RIDE PDF]
    W --> X[Attach QR Code]
    X --> Y[Send Email to Customer]
    Y --> Z([End - Success])
```

---

## 5. COMPONENT DIAGRAM: System Architecture

```mermaid
flowchart LR
    subgraph Odoo["Odoo 18.0"]
        A[account.move]
        B[l10n_ec_sri Module]
        C[XAdES Signer]
        D[SOAP Client]
    end

    subgraph External["External Services"]
        E[SRI SOAP API]
        F[SMTP Server]
    end

    subgraph Storage["Storage"]
        G[(PostgreSQL)]
        H[(File Store)]
    end

    A --> B
    B --> C
    C --> D
    D <--> E
    B --> F
    A --> G
    B --> H
```

---

**UML Classification**: ISO 19501 / UML 2.5 Compliant
