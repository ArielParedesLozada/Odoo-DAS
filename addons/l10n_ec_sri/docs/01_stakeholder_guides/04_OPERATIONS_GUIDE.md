# OPERATIONS DIRECTOR DEFINITIVE REFERENCE GUIDE
## Ing. Roberto Operaciones, PMP

**Document ID**: OPS-DRG-001
**Version**: 2.0 (Enterprise Grade)
**Date**: 2026-01-22

---

## 1. SUPPLY CHAIN REGULATORY SCOPE

### 1.1 Governing Bodies
| Entity | Scope | System Module |
|:-------|:------|:--------------|
| **SRI** | Guía de Remisión | `l10n_ec_stock_guia` |
| **SENAE** | Customs (DAU/DAE) | `l10n_ec_customs` |
| **ANT** | Transport permits | `fleet` integration |

---

## 2. GUÍA DE REMISIÓN (WAYBILL)

### 2.1 Legal Requirement
**Legal Basis**: LORTI Art. 103, Reglamento Facturación

| Scenario | Guía Required? |
|:---------|:--------------|
| Delivery to customer | **Yes** |
| Inter-warehouse transfer | **Yes** |
| Return to supplier | **Yes** |
| Movement within same address | No |
| Personal goods transport | No |

### 2.2 Document Structure (From XSD `guia_remision.xsd`)
```xml
<guiaRemision version="1.1.0">
  <infoTributaria>
    <!-- Same as Factura -->
    <codDoc>06</codDoc>  <!-- Document Type 06 = Guía -->
  </infoTributaria>
  <infoGuiaRemision>
    <dirPartida>{{ dir_partida }}</dirPartida>
    <dirDestinatario>{{ dir_destinatario }}</dirDestinatario>
    <razonSocialDestinatario>{{ razon_social }}</razonSocialDestinatario>
    <identificacionDestinatario>{{ ruc_cedula }}</identificacionDestinatario>
    <fechaIniTransporte>{{ fecha_inicio }}</fechaIniTransporte>
    <fechaFinTransporte>{{ fecha_fin }}</fechaFinTransporte>
    <placa>{{ placa }}</placa>
  </infoGuiaRemision>
  <destinatarios>
    <destinatario>
      <motivoTraslado>{{ motivo_code }}</motivoTraslado>
      <ruta>{{ ruta }}</ruta>
      <detalles>
        <!-- Product lines -->
      </detalles>
    </destinatario>
  </destinatarios>
</guiaRemision>
```

### 2.3 Motivo Traslado Codes (SRI Catalog)
| Code | Description | Use Case |
|:-----|:------------|:---------|
| 01 | Venta | Customer delivery |
| 02 | Devolución | Returns |
| 03 | Traslado entre establecimientos | Warehouse transfer |
| 04 | Consignación | Consignment |
| 05 | Transformación | Manufacturing |
| 06 | Venta como exportación | Export sale |
| 07 | Otros | Other (specify) |

### 2.4 Required Data Fields
| Field | Odoo Model | Source |
|:------|:-----------|:-------|
| `placa` | `fleet.vehicle.license_plate` | Company fleet |
| `cedula_transportista` | `res.partner.vat` | Driver partner |
| `dir_partida` | `stock.warehouse.partner_id.street` | Warehouse address |
| `dir_destinatario` | `res.partner.street` | Delivery address |
| `fecha_ini_transporte` | `stock.picking.scheduled_date` | Planned date |
| `fecha_fin_transporte` | `stock.picking.date_done` | Actual date |

### 2.5 Workflow
```
1. Picking Validated →
2. Generate Access Key (Módulo 11, codDoc='06') →
3. Render XML (Jinja2 template) →
4. Validate XSD →
5. XAdES-BES Sign →
6. SRI Reception →
7. SRI Authorization →
8. Attach authorized XML to picking →
9. Print RIDE →
10. Driver carries RIDE during transport
```

---

## 3. SENAE CUSTOMS (IMPORTS/EXPORTS)

### 3.1 Import Tax Calculation
**Legal Basis**: Ley Orgánica de Aduanas

```python
# Import duty calculation
def calculate_import_taxes(cif_value, tariff_code):
    """
    CIF = Cost + Insurance + Freight
    """
    tariff_rate = get_tariff_rate(tariff_code)

    ad_valorem = cif_value * tariff_rate
    fodinfa = cif_value * 0.005  # 0.5%

    # ICE applies to specific products
    ice = calculate_ice(cif_value, tariff_code) if has_ice(tariff_code) else 0

    # IVA on total taxable
    taxable_base = cif_value + ad_valorem + fodinfa + ice
    iva = taxable_base * 0.15  # 15%

    return {
        'ad_valorem': round(ad_valorem, 2),
        'fodinfa': round(fodinfa, 2),
        'ice': round(ice, 2),
        'iva': round(iva, 2),
        'total': round(ad_valorem + fodinfa + ice + iva, 2)
    }
```

### 3.2 Key Import Documents
| Document | Spanish | Purpose |
|:---------|:--------|:--------|
| DAU | Declaración Aduanera Única | Single customs declaration |
| DAV | Declaración Andina de Valor | Andean value declaration |
| Bill of Lading | Conocimiento de Embarque | Shipping document |
| Commercial Invoice | Factura Comercial | Supplier invoice |
| Packing List | Lista de Empaque | Product details |

### 3.3 Import Workflow
```
1. PO Created →
2. PO Confirmed →
3. Goods Shipped (supplier) →
4. Create DAU in l10n_ec_customs →
5. Calculate import taxes →
6. Goods arrive port (Guayaquil/Esmeraldas) →
7. SENAE inspection →
8. Pay duties →
9. SENAE clearance →
10. Create Vendor Bill with import taxes →
11. Receive inventory (stock.picking)
```

### 3.4 ISD (Impuesto Salida de Divisas)
| Rate | Application |
|:-----|:------------|
| 5% | Foreign payments >$5,000 |
| 0% | Imports of raw materials (list) |

---

## 4. FLEET MANAGEMENT

### 4.1 Required Vehicle Data for Guía
| Field | Model | Validation |
|:------|:------|:-----------|
| License Plate | `fleet.vehicle.license_plate` | Format: ABC-1234 |
| Brand | `fleet.vehicle.model_id.brand_id.name` | Required |
| Year | `fleet.vehicle.model_year` | Required |
| Insurance | `fleet.vehicle.insurance_id` | Must be valid |

### 4.2 Driver Requirements
| Field | Model | Validation |
|:------|:------|:-----------|
| Name | `res.partner.name` | Required |
| Cédula | `res.partner.vat` | 10 digits |
| License Type | `res.partner.l10n_ec_license_type` | Valid for cargo |
| License Expiry | `res.partner.l10n_ec_license_expiry` | Not expired |

---

## 5. PRODUCT TRACEABILITY

### 5.1 Lot/Serial Tracking Requirements
| Product Category | Tracking | Regulatory Basis |
|:-----------------|:---------|:-----------------|
| Pharmaceuticals | Lot (ARCSA) | Health regulation |
| Food products | Lot + Expiry | ARCSA |
| Electronics | Serial | Consumer protection |
| Textiles | None | Optional |

### 5.2 Traceability Report
```
"Show complete chain for Lot ABC123"
→ Purchase: PO/2025/0001 (Supplier XYZ)
→ Receipt: WH/IN/2025/0050
→ Internal Move: WH/INT/2025/0030
→ Sale: SO/2025/0100
→ Delivery: WH/OUT/2025/0200 (Customer ABC)
→ Guía: GR/2025/0050 (Authorized)
```

---

## 6. AI AGENT COMMANDS

### 6.1 Logistics Operations
```
"Generate Guía de Remisión for delivery OUT/2026/0001"
"Show all pending deliveries without Guía"
"What vehicles are available today?"
"List drivers with expired licenses"
```

### 6.2 Customs Operations
```
"Calculate import taxes for PO/2026/0050"
"Show all pending DAU declarations"
"What is the tariff rate for HS code 8471.30.00?"
"List imports awaiting SENAE clearance"
```

### 6.3 Traceability
```
"Track lot number LOT/2025/ABC123"
"Show all products expiring in 30 days"
"Generate recall report for product X"
```

---

**Document Classification**: Operations & Logistics Reference
**Regulatory Sources**: LORTI, SENAE, ANT
**Last Verified**: 2026-01-22
