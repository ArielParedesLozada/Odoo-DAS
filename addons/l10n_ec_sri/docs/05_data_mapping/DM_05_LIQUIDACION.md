# DATA MAPPING: LIQUIDACIÓN DE COMPRA
## DM_05 - Purchase Settlement XML for SRI

**Document ID**: DM-005 | **Version**: 1.0 | **Date**: 2026-01-22
**Owner**: Tax Manager

---

## 1. OVERVIEW

Liquidación de Compra (Purchase Settlement) for purchases from informal suppliers who cannot issue invoices.

---

## 2. WHEN TO USE

| Vendor Type | Use Liquidación? |
|:------------|:-----------------|
| Person without RUC | ✅ Yes |
| RISE contributor (small purchase) | ✅ Yes |
| Peasant/farmer | ✅ Yes |
| Artisan without invoices | ✅ Yes |
| Formal company with RUC | ❌ No |

---

## 3. XML STRUCTURE

```xml
<?xml version="1.0" encoding="UTF-8"?>
<liquidacionCompra id="comprobante" version="1.1.0">
    <infoTributaria>...</infoTributaria>
    <infoLiquidacionCompra>...</infoLiquidacionCompra>
    <detalles>...</detalles>
</liquidacionCompra>
```

---

## 4. FIELD MAPPING

| XML Element | Odoo Source | Required |
|:------------|:------------|:---------|
| `codDoc` | '03' (fixed) | ✓ |
| `fechaEmision` | `move.invoice_date` | ✓ |
| `tipoIdentificacionProveedor` | '05' (Cédula) | ✓ |
| `identificacionProveedor` | `partner.vat` | ✓ |
| `razonSocialProveedor` | `partner.name` | ✓ |
| `direccionProveedor` | `partner.street` | ✓ |

---

## 5. WITHHOLDING OBLIGATION

> [!IMPORTANT]
> Buyer MUST withhold 100% of IVA and applicable IR on liquidaciones.

| Tax | Withholding |
|:----|:------------|
| IVA | 100% |
| IR | 2% (based on concept) |

---

**Data Mapping Classification**: ISO 9001:2015 Controlled
