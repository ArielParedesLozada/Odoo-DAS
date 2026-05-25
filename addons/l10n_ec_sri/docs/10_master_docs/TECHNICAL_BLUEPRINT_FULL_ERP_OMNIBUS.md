# ODOO ECUADOR TECHNICAL BLUEPRINT: THE OMNIBUS
**Document ID**: SOMA-TECH-OMNIBUS-001
**Date**: 2026-01-22
**Level**: CODE-LEVEL SPECIFICATION
**Scope**: Full ERP (Logistics, Finance, POS, Purchasing)

---

## 1. THE LOGISTICS ENGINE (`l10n_ec_edi_stock`)
**Goal**: Generate `guiaRemision` XML (v1.1.0/2026).

### 1.1 Python Model: `stock.picking`
| Field Name | Type | XML Tag | Description |
| :--- | :--- | :--- | :--- |
| `l10n_ec_transport_permit` | Char | N/A | Permiso de Operación (Transportista) |
| `l10n_ec_entity_id` | Many2one | `rucTransportista` | Link to `res.partner` (Carrier) |
| `l10n_ec_start_date` | Date | `fechaIniTransporte` | Logistics Start |
| `l10n_ec_end_date` | Date | `fechaFinTransporte` | Logistics End |
| `l10n_ec_plate` | Char | `placa` | Vehicle Plate (Legacy: `delivery_guide`) |

### 1.2 XML Structure vs Odoo Logic
**Algorithm**: `generate_guia_xml(picking)`
1.  **InfoTributaria**: Standard Mod11 Access Key.
2.  **InfoGuiaRemision**:
    *   `dirPartida`: `picking.picking_type_id.warehouse_id.partner_id.street`
    *   `razonSocialTransportista`: `picking.carrier_id.partner_id.name`
3.  **Destinatarios (Array)**:
    *   Iterate `picking.move_ids_without_package`.
    *   `destinatario`: `picking.partner_id.name`.
    *   `motivoTraslado`: Selection Field on Picking (e.g., 'Venta', 'Traslado').
    *   `ruta`: `picking.location_id.name` -> `picking.location_dest_id.name`.
4.  **Detalles (Array)**:
    *   `codigoInterno`: `move.product_id.default_code`.
    *   `cantidad`: `move.quantity_done`.

---

## 2. THE PURCHASING ENGINE (`l10n_ec_edi_purchase`)
**Goal**: Generate `liquidacionCompra` XML (v1.1.0).

### 2.1 Python Model: `account.move` (In_Invoice)
For `move_type = 'in_invoice'` AND `l10n_ec_document_type = '03'`:
| Field Name | Type | XML Tag | Validation |
| :--- | :--- | :--- | :--- |
| `l10n_ec_foreign_regime` | Selection | `regimenFiscal` | Required if Import |
| `l10n_ec_total_reimbursement`| Monetary | `codDocReemb` | For Intermediaries |
| `l10n_ec_payment_method` | Many2one | `formaPago` | SRI Table 24 |

### 2.2 XML Structure (`liquidacionCompra`)
1.  **InfoLiquidacionCompra**:
    *   `identificacionProveedor`: `partner.vat`.
    *   `totalSinImpuestos`: Sum of Subtotals.
    *   `totalConImpuestos`: Grand Total.
2.  **Reembolsos (Optional)**:
    *   Only if `l10n_ec_is_reimbursement = True`.
    *   Iterate `move.l10n_ec_reimbursement_ids`.

---

## 3. THE FINANCIAL ENGINE (`l10n_ec_edi_finance`)
**Goal**: Generate `factura`, `comprobanteRetencion`, `notaCredito`, `notaDebito`.

### 3.1 Electronic Invoice (`factura`)
**Critical 2026 Updates**:
*   **Campos Adicionales**:
    *   `Attr: "Agente de Retención"` -> Value: `company.l10n_ec_withhold_agent_number`.
    *   `Attr: "Contribuyente RIMPE"` -> Value: `company.l10n_ec_rimpe_text`.
*   **Payments (`pagos`)**:
    *   MUST match `account.payment.term`.
    *   If Term = 30 Days -> `plazo` = 30, `unidadTiempo` = 'dias'.

### 3.2 Withholding (`comprobanteRetencion`)
**Algorithm**:
1.  **Trigger**: On `account.payment.post()` OR `account.move.post()` (Purchases).
2.  **Mapping**:
    *   Look up `account.tax` where `tax_group_id.l10n_ec_type = 'withhold'`.
    *   `codigo`: `tax.l10n_ec_code` (e.g., 312).
    *   `porcentajeRetener`: `tax.amount`.
    *   `baseImponible`: `line.balance`.

### 3.3 Credit Notes (`notaCredito`)
**Logic**:
*   Must link to Modified Document (`numDocModificado`).
*   Reason (`motivo`) is Mandatory.
*   **2026 Constraint**: Cannot issue NC to "Consumidor Final" if Invoice > $50.

---

## 4. THE RETAIL ENGINE (`l10n_ec_edi_pos`)
**Goal**: High-speed signing for Point of Sale.

### 4.1 POS Session Architecture
1.  **JS Client**:
    *   Calculates `Access Key` locally (using Python logic ported to JS).
    *   Prints Receipt with Barcode immediately.
2.  **Python Job**:
    *   `pos.order` synced to Backend.
    *   Job `process_edi_queue` picks it up.
    *   Signs XML.
    *   Sends to SRI.
    *   Updates `pos.order` state to `Authorized`.
3.  **Error Handling**:
    *   If SRI rejects, `pos.order` marked `Attention Needed`.
    *   Manager corrects Partner Data -> Retries.

---

## 5. REVERSE ENGINEERING LOG (Legacy vs New)
| Component | Legacy (V10) | New (V18 Blueprint) |
| :--- | :--- | :--- |
| **Class** | `account.invoice` | `account.move` |
| **Signer** | Java JAR | `cryptography` (Python) |
| **Logic** | Manual `wizard` for Ret | Automated on Post |
| **Guía** | Text Field | `stock.picking` Model Integration |
| **Liquidación**| Not Implemented | Native `account.move` Type |

**Verification**: This plan maps 1:1 to the User's "Full ERP" demand.
