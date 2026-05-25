# BUSINESS PROCESS FLOWS & DIAGRAMS
## Ecuador Odoo 18.0 Localization

**Document ID**: SOMA-BPF-001
**Date**: 2026-01-22

---

## 1. ELECTRONIC INVOICE FLOW (Order-to-Cash)

```mermaid
flowchart TD
    A[Sales Order Created] --> B[Confirm Order]
    B --> C[Create Delivery]
    C --> D[Validate Delivery]
    D --> E[Create Invoice]
    E --> F{Partner = Consumidor Final?}
    F -->|Yes| G{Amount > $50?}
    G -->|Yes| H[BLOCK - Request Customer ID]
    G -->|No| I[Allow Consumidor Final]
    F -->|No| I
    H --> J[Customer Provides RUC/Cedula]
    J --> K[Update Partner]
    K --> I
    I --> L[Post Invoice]
    L --> M[Generate XML]
    M --> N[Compute Access Key - Mod11]
    N --> O[Sign XML - XAdES-BES]
    O --> P[Send to SRI - validarComprobante]
    P --> Q{SRI Response?}
    Q -->|RECIBIDA| R[Call autorizacionComprobante]
    Q -->|DEVUELTA| S[Log Error - Retry]
    R --> T{Authorized?}
    T -->|AUTORIZADO| U[Store XML + Auth Number]
    T -->|NO AUTORIZADO| V[Mark Rejected - Manual Action]
    U --> W[Print RIDE PDF]
    W --> X[Send to Customer]
    S --> O
```

---

## 2. WITHHOLDING (RETENCIÓN) FLOW

```mermaid
flowchart TD
    A[Receive Vendor Bill] --> B[Validate Bill]
    B --> C[Select Sustento Tributario]
    C --> D{Need Retention?}
    D -->|No| E[Process Payment]
    D -->|Yes| F[Create Retention Document]
    F --> G{Date within 5 days?}
    G -->|No| H[ERROR - Cannot Issue Retention]
    G -->|Yes| I[Add Retention Lines]
    I --> J[Select Tax Codes - 312, 320, etc.]
    J --> K[Compute Amounts]
    K --> L[Validate Retention]
    L --> M[Generate Retention XML]
    M --> N[Sign XML]
    N --> O[Send to SRI]
    O --> P{Authorized?}
    P -->|Yes| Q[Link to Vendor Bill]
    P -->|No| R[Fix Errors - Retry]
    Q --> S[Compute Net Payment]
    S --> E
    E --> T[Register Payment]
```

---

## 3. GUÍA DE REMISIÓN FLOW (Logistics)

```mermaid
flowchart TD
    A[Delivery Order Created] --> B{Goods Leaving Premises?}
    B -->|No| C[Internal Transfer - No Guía]
    B -->|Yes| D[Mark as Guía Required]
    D --> E[Select Driver]
    E --> F[Select Vehicle/Plate]
    F --> G[Enter Transport Dates]
    G --> H[Define Route]
    H --> I[Validate Picking]
    I --> J[Generate Guía XML]
    J --> K[Sign XML]
    K --> L[Send to SRI]
    L --> M{Authorized?}
    M -->|Yes| N[Print Guía Document]
    M -->|No| O[Fix - Cannot Ship]
    N --> P[Driver Takes Guía]
    P --> Q[Goods Shipped]
    Q --> R[Delivery Confirmed]
```

---

## 4. PURCHASE LIQUIDATION FLOW

```mermaid
flowchart TD
    A[Need to Buy from Rural Producer] --> B{Vendor has RUC?}
    B -->|Yes| C[Normal Purchase Order]
    B -->|No| D[Create Liquidación de Compra]
    D --> E[Enter Vendor with Cédula]
    E --> F[Enter Products/Services]
    F --> G[System Computes 100% IVA Retention]
    G --> H[System Computes Renta Retention]
    H --> I[Validate Liquidación]
    I --> J[Generate XML - codDoc 03]
    J --> K[Sign XML]
    K --> L[Send to SRI]
    L --> M{Authorized?}
    M -->|Yes| N[Print for Vendor Signature]
    M -->|No| O[Fix Errors]
    N --> P[Vendor Signs Receipt]
    P --> Q[Pay Net Amount to Vendor]
    Q --> R[Register Tax Liability]
```

---

## 5. POS ELECTRONIC INVOICE FLOW

```mermaid
flowchart TD
    A[POS Session Started] --> B[Customer Purchases Items]
    B --> C[Cashier Scans Products]
    C --> D[Calculate Total]
    D --> E{Total > $50?}
    E -->|Yes| F{Customer Identified?}
    F -->|No| G[BLOCK - Request ID]
    F -->|Yes| H[Continue]
    E -->|No| H
    G --> I[Enter RUC/Cédula]
    I --> H
    H --> J[Customer Pays]
    J --> K[Pre-compute Access Key JS]
    K --> L[Print Receipt with Barcode]
    L --> M[Queue for Background Sync]
    M --> N{SRI Available?}
    N -->|Yes| O[Sign + Send XML]
    N -->|No| P[Retry Later - Contingency]
    O --> Q{Authorized?}
    Q -->|Yes| R[Mark Order Complete]
    Q -->|No| S[Flag for Manager Review]
    P --> O
```

---

## 6. DOCUMENT STATE MACHINE

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Posted: action_post()
    Posted --> Signed: sign_xml()
    Signed --> Sent: send_to_sri()
    Sent --> Authorized: sri_response=AUTORIZADO
    Sent --> Rejected: sri_response=NO_AUTORIZADO
    Rejected --> Signed: retry()
    Authorized --> [*]
    
    note right of Draft: User creates document
    note right of Signed: XAdES-BES signature applied
    note right of Authorized: SRI has validated
```

---

## 7. ATS GENERATION FLOW

```mermaid
flowchart TD
    A[End of Month] --> B[Open ATS Wizard]
    B --> C[Select Year/Month]
    C --> D[System Validates Data]
    D --> E{All Invoices have Sustento?}
    E -->|No| F[Show Missing Items]
    F --> G[User Fixes Data]
    G --> D
    E -->|Yes| H{All Retentions Authorized?}
    H -->|No| I[Show Pending Retentions]
    I --> J[User Authorizes]
    J --> D
    H -->|Yes| K[Generate ATS XML]
    K --> L[Cross-Check Totals vs GL]
    L --> M{Balanced?}
    M -->|No| N[Show Discrepancies]
    M -->|Yes| O[Download XML]
    O --> P[Upload to SRI Portal]
    P --> Q[File ATS]
```

---

## 8. PAYROLL FLOW

```mermaid
flowchart TD
    A[New Pay Period] --> B[Create Payroll Batch]
    B --> C[Load Active Employees]
    C --> D[Fetch Attendance Data]
    D --> E[Compute Basic Salary]
    E --> F[Add Extra Hours 50%/100%]
    F --> G[Add Commissions/Bonuses]
    G --> H{D13 Mensualizado?}
    H -->|Yes| I[Add D13 Monthly]
    H -->|No| J[Skip Accrual]
    I --> K{D14 Mensualizado?}
    J --> K
    K -->|Yes| L[Add D14 Monthly]
    K -->|No| M[Skip]
    L --> N[Compute IESS 9.45%]
    M --> N
    N --> O[Compute IR Withholding]
    O --> P[Apply Other Deductions]
    P --> Q[Generate Rol de Pagos]
    Q --> R[Validate Batch]
    R --> S[Create Accounting Entries]
    S --> T[Generate Bank File]
    T --> U[Pay Employees]
```

---

## 9. IMPORT (CUSTOMS) FLOW

```mermaid
flowchart TD
    A[Purchase Order to Foreign Vendor] --> B[Goods Shipped]
    B --> C[Arrival at Port]
    C --> D[Customs Broker Processes]
    D --> E[Create DAU Record in Odoo]
    E --> F[Enter CIF Value]
    F --> G[System Computes Ad Valorem]
    G --> H[System Computes FODINFA 0.5%]
    H --> I[System Computes IVA Import]
    I --> J[Enter Any ICE if Applicable]
    J --> K[Total Customs Taxes Computed]
    K --> L[Link to Vendor Bill]
    L --> M[Pay to SENAE]
    M --> N[Goods Released]
    N --> O[Receive in Warehouse]
    O --> P[Landed Cost Applied to Products]
```

---

## 10. ENTITY RELATIONSHIP DIAGRAM

```mermaid
erDiagram
    RES_COMPANY ||--o{ ACCOUNT_MOVE : issues
    RES_PARTNER ||--o{ ACCOUNT_MOVE : customer_of
    ACCOUNT_MOVE ||--o{ ACCOUNT_MOVE_LINE : contains
    ACCOUNT_MOVE ||--o| ACCOUNT_RETENTION : has_retention
    ACCOUNT_RETENTION ||--o{ ACCOUNT_RETENTION_LINE : contains
    STOCK_PICKING ||--o| L10N_EC_GUIA : generates
    POS_ORDER ||--o| ACCOUNT_MOVE : creates_invoice
    HR_EMPLOYEE ||--o{ HR_PAYSLIP : receives
    HR_PAYSLIP ||--o{ HR_PAYSLIP_LINE : contains
    L10N_EC_CUSTOMS_DECLARATION ||--o{ ACCOUNT_MOVE : links_to
    
    RES_COMPANY {
        string vat
        binary l10n_ec_p12_certificate
        string l10n_ec_sri_environment
    }
    
    ACCOUNT_MOVE {
        string l10n_ec_access_key
        string l10n_ec_authorization
        selection l10n_ec_edi_state
        binary l10n_ec_xml_file
    }
    
    ACCOUNT_RETENTION {
        date date
        many2one invoice_id
        float total_retained
        string l10n_ec_access_key
    }
    
    STOCK_PICKING {
        string l10n_ec_access_key
        many2one l10n_ec_driver_id
        string l10n_ec_plate
        date l10n_ec_start_date
    }
```

---

**This is what a professional ERP implementor delivers.**
**Flow charts. State machines. ERDs. Real documentation.**
