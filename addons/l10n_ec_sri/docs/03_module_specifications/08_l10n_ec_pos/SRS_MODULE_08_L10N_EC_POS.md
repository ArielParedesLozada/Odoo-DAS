# SOFTWARE REQUIREMENTS SPECIFICATION
## Module: l10n_ec_pos (Ecuador Point of Sale)

**Document Identifier**: SRS-L10N-EC-POS-001
**Version**: 1.0
**Date**: 2026-01-22
**Status**: APPROVED
**Standard**: ISO/IEC/IEEE 29148:2018

---

## 1. INTRODUCTION

### 1.1 Purpose
This SRS describes the requirements for the `l10n_ec_pos` module, which implements electronic invoicing for Point of Sale operations in Ecuador, including the $50 Consumidor Final limit, offline contingency mode, and session reconciliation.

### 1.2 Scope
The module SHALL:
1. Generate electronic invoices from POS orders in real-time.
2. Enforce UAFE $50 limit for Consumidor Final.
3. Support offline contingency mode when SRI is unavailable.
4. Reconcile electronic documents with POS sessions.
5. Print RIDE (receipt format) with Access Key barcode.

### 1.3 Legal References
- SRI Resolución NAC-DGERCGC14-00790
- UAFE Normativa
- Ficha Técnica v2.32 (POS requirements)

---

## 2. EXPERT CREW PERSPECTIVES

### 2.1 Operations Director Perspective (Roberto Operaciones)
> "We have 15 stores, each with 3-5 POS terminals. If SRI goes down for 10 minutes during peak hours, we cannot stop selling. We need bulletproof offline mode."

### 2.2 Compliance Officer Perspective (Sofía Cumplimiento)
> "The $50 rule is non-negotiable. I don't care if the customer is in a hurry - if it's over $50, we need their data. The system must physically block the sale."

### 2.3 IT Architect Perspective (Patricia Sistemas)
> "POS terminals have limited connectivity. We need to pre-compute Access Keys client-side to avoid latency. The sync to SRI happens in background."

### 2.4 CFO Perspective (María Finanzas)
> "Session closing must match: Total POS sales = Total electronic invoices. Any discrepancy is an audit red flag."

---

## 3. SPECIFIC REQUIREMENTS

### 3.1 POS Order Extensions (`pos.order`)
| Field | Type | Description |
|:---|:---|:---|
| `l10n_ec_access_key` | Char(49) | Pre-computed access key |
| `l10n_ec_authorization_number` | Char | SRI authorization (after sync) |
| `l10n_ec_edi_state` | Selection | pending, authorized, rejected |
| `l10n_ec_is_consumidor_final` | Boolean | Auto-set if partner = CF |
| `l10n_ec_invoice_id` | Many2one | Link to generated invoice |

### 3.2 UAFE Consumidor Final Enforcement
**REQ-UAFE-001**: On POS Order Validation:
```javascript
if (order.partner.vat === '9999999999999' && order.total > 50.00) {
    throw new UserError(
        'LÍMITE UAFE EXCEDIDO\n' +
        'Para ventas mayores a $50.00, debe identificar al cliente.\n' +
        'Por favor solicite RUC o Cédula.'
    );
}
```

**REQ-UAFE-002**: The POS interface SHALL:
1. Display prominent warning when approaching $50.
2. Require explicit manager override if attempting to bypass.
3. Log all override attempts with reason.

### 3.3 Offline Contingency Mode
**REQ-OFF-001**: When SRI is unreachable:
1. Order proceeds with pre-computed Access Key.
2. Receipt prints with Access Key barcode.
3. Order is queued for background sync.
4. Maximum offline duration: 24 hours (regulated limit).

**REQ-OFF-002**: Contingency Queue (`l10n_ec.pos.pending`):
| Field | Type | Description |
|:---|:---|:---|
| `order_id` | Many2one | POS Order |
| `access_key` | Char(49) | Pre-computed |
| `xml_content` | Binary | Signed XML |
| `retry_count` | Integer | Attempts made |
| `last_error` | Text | Last SRI error |
| `state` | Selection | pending, synced, failed |

**REQ-OFF-003**: Background Sync Job:
- Runs every 5 minutes.
- Processes oldest pending orders first.
- Maximum 3 retries per order.
- Alerts manager if order fails after 3 retries.

### 3.4 Session Reconciliation
**REQ-REC-001**: On POS Session Close:
| Metric | Description |
|:---|:---|
| **Total Cash Sales** | Sum of cash payments |
| **Total Card Sales** | Sum of card payments |
| **Total Invoiced** | Sum of authorized electronic invoices |
| **Pending Invoices** | Count of orders awaiting SRI auth |
| **Failed Invoices** | Count of rejected orders |
| **Discrepancy** | Total Sales - Total Invoiced |

**REQ-REC-002**: Session cannot close if:
- Pending invoices > 0 (must wait for sync)
- Failed invoices > 0 without manager action

### 3.5 RIDE Receipt Format
**REQ-RIDE-001**: POS Receipt SHALL include:
| Section | Content |
|:---|:---|
| **Header** | Company Name, RUC, Address |
| **Document** | FACTURA ELECTRÓNICA |
| **Number** | 001-001-000000123 |
| **Date** | DD/MM/YYYY HH:MM |
| **Client** | Name, RUC/Cédula (or CONSUMIDOR FINAL) |
| **Items** | Product, Qty, Price, Subtotal |
| **Totals** | Subtotal 0%, Subtotal 15%, IVA, TOTAL |
| **Footer** | Access Key (numeric + barcode), Authorization # |
| **Legal** | "Autorizado según Resolución..." |

### 3.6 Access Key Pre-Computation (JavaScript)
**REQ-AK-001**: POS Client SHALL compute Access Key locally:
```javascript
function computeAccessKey(order) {
    // Position 1-8: Date DDMMYYYY
    let date = formatDate(order.date, 'DDMMYYYY');
    // Position 9-10: Document Type
    let docType = '01';
    // Position 11-23: RUC
    let ruc = order.company.vat;
    // Position 24: Environment
    let env = order.company.sri_environment;
    // ... continue building 48 chars
    // Position 49: Check Digit (Mod11)
    let checkDigit = computeMod11(first48);
    return first48 + checkDigit;
}
```

---

## 4. USE CASES

### 4.1 UC-001: Standard POS Sale < $50 Consumidor Final
**Actor**: Cashier
**Flow**:
1. Cashier scans products.
2. Customer pays cash.
3. Total = $35.00.
4. Cashier clicks "Validate".
5. System computes Access Key.
6. System prints receipt.
7. Background job syncs to SRI.
**Postcondition**: Invoice authorized within 5 minutes.

### 4.2 UC-002: Sale > $50 Requires Customer Data
**Actor**: Cashier
**Flow**:
1. Cashier scans products.
2. Total = $75.00.
3. Cashier clicks "Validate".
4. System blocks: "LÍMITE UAFE EXCEDIDO".
5. Cashier asks customer for Cédula.
6. Cashier selects/creates customer with Cédula.
7. Cashier clicks "Validate".
8. System proceeds with identified customer.

### 4.3 UC-003: Offline Mode During SRI Outage
**Actor**: Cashier
**Flow**:
1. SRI is unreachable (network issue).
2. System detects timeout.
3. System enters "Contingency Mode" (visual indicator).
4. Sales continue with pre-computed Access Keys.
5. Receipts print with "PENDIENTE DE AUTORIZACIÓN".
6. When SRI recovers, background job syncs all pending.
7. Session reconciliation shows all authorized.

---

## 5. VALIDATION CRITERIA

| Test ID | Description | Expected |
|:---|:---|:---|
| **T-POS-001** | Sale $40 to Consumidor Final | Success, no block |
| **T-POS-002** | Sale $60 to Consumidor Final | Block, require ID |
| **T-POS-003** | Sale during SRI outage | Queue, print receipt |
| **T-POS-004** | Session close with pending | Block close |
| **T-POS-005** | Access Key computation | Valid Mod11 |

---

## 6. TECHNICAL CONSTRAINTS

### 6.1 Performance
- Access Key computation: < 50ms
- Receipt print time: < 2s
- Background sync: Non-blocking

### 6.2 Offline Storage
- IndexedDB for browser-based POS
- SQLite for IoT Box
- Maximum 1000 pending orders

---

**Document Control**:
| Version | Date | Author |
|:---|:---|:---|
| 1.0 | 2026-01-22 | Expert Crew (Operations, Compliance, IT) |
