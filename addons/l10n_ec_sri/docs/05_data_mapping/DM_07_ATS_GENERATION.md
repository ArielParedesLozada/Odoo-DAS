# DATA MAPPING: ATS GENERATION
## DM_07 - Anexo Transaccional Simplificado

**Document ID**: DM-007 | **Version**: 1.0 | **Date**: 2026-01-22
**Owner**: Tax Manager | **Ref**: [KB_TAX_RATES_WITHHOLDINGS.md](../11_regulatory_knowledge_base/KB_TAX_RATES_WITHHOLDINGS.md)

---

## 1. OVERVIEW

Monthly XML file to SRI with all purchase/sales transactions.

| Attribute | Value |
|:----------|:------|
| Format | XML |
| Schema | ATS v1.1.0 |
| Deadline | Last day of following month |

---

## 2. HEADER MAPPING

| XML Element | Odoo Source | Required |
|:------------|:------------|:---------|
| `TipoIDInformante` | 'R' (RUC) | ✓ |
| `IdInformante` | `company.vat` | ✓ |
| `razonSocial` | `company.name` | ✓ |
| `Anio` | Period year | ✓ |
| `Mes` | Period month | ✓ |
| `totalVentas` | Sum of sales | ✓ |

---

## 3. PURCHASE MAPPING (detalleCompras)

| XML Element | Odoo Source |
|:------------|:------------|
| `codSustento` | `move.l10n_ec_sustento_code` |
| `tpIdProv` | `partner.l10n_ec_id_type` |
| `idProv` | `partner.vat` |
| `tipoComprobante` | `move.l10n_latam_document_type_id.code` |
| `fechaEmision` | `move.invoice_date` |
| `autorizacion` | `move.l10n_ec_authorization` |
| `baseNoGraIva` | Base without IVA |
| `baseImpGrav` | Base with IVA 15% |
| `montoIva` | IVA amount |

### Sustento Codes
| Code | Description |
|:-----|:------------|
| `01` | Crédito Tributario IVA |
| `02` | Costo o Gasto |
| `03` | Activo Fijo |

---

## 4. WITHHOLDING MAPPING (air)

```xml
<air>
  <detalleAir>
    <codRetAir>312</codRetAir>
    <baseImpAir>1000.00</baseImpAir>
    <porcentajeAir>10</porcentajeAir>
    <valRetAir>100.00</valRetAir>
  </detalleAir>
</air>
```

---

## 5. SALES MAPPING (detalleVentas)

| XML Element | Odoo Source |
|:------------|:------------|
| `tpIdCliente` | `partner.l10n_ec_id_type` |
| `idCliente` | `partner.vat` |
| `tipoComprobante` | Document type code |
| `numeroComprobantes` | Count |
| `baseImpGrav` | Sum IVA 15% base |
| `montoIva` | Sum IVA collected |

---

## 6. PAYMENT CODES

| Code | Description |
|:-----|:------------|
| `01` | Sin Sistema Financiero |
| `19` | Tarjeta Crédito |
| `20` | Otros Sistema Financiero |

---

## 7. DEADLINE BY RUC 9th DIGIT

| Digit | Day |
|:------|:----|
| 1 | 10th |
| 2 | 12th |
| 3-9 | 14th-26th |
| 0 | 28th |

---

**Classification**: ISO 9001:2015 Controlled
