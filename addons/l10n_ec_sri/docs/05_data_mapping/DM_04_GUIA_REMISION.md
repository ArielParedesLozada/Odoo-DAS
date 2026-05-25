# DATA MAPPING: GUÍA DE REMISIÓN
## DM_04 - Delivery Note XML for SRI

**Document ID**: DM-004 | **Version**: 1.0 | **Date**: 2026-01-22
**Owner**: Supply Chain Manager

---

## 1. OVERVIEW

Guía de Remisión (Delivery Note) XML for goods transport.

---

## 2. XML STRUCTURE

```xml
<?xml version="1.0" encoding="UTF-8"?>
<guiaRemision id="comprobante" version="1.1.0">
    <infoTributaria>...</infoTributaria>
    <infoGuiaRemision>...</infoGuiaRemision>
    <destinatarios>...</destinatarios>
</guiaRemision>
```

---

## 3. FIELD MAPPING

| XML Element | Odoo Source | Required |
|:------------|:------------|:---------|
| `codDoc` | '06' (fixed) | ✓ |
| `dirEstablecimiento` | `warehouse.partner_id.street` | ✓ |
| `dirPartida` | Origin address | ✓ |
| `razonSocialTransportista` | `carrier.name` | ✓ |
| `rucTransportista` | `carrier.vat` | ✓ |
| `placa` | `picking.vehicle_plate` | ✓ |
| `fechaIniTransporte` | `picking.scheduled_date` | ✓ |
| `fechaFinTransporte` | `picking.date_done` | ✓ |

---

## 4. DESTINATARIO (Recipient)

| XML Element | Odoo Source |
|:------------|:------------|
| `identificacionDestinatario` | `partner.vat` |
| `razonSocialDestinatario` | `partner.name` |
| `dirDestinatario` | `partner.street` |
| `motivoTraslado` | 'Venta' / 'Traslado' |
| `docAduaneroUnico` | DAU if import |
| `codDocSustento` | '01' (invoice) |
| `numDocSustento` | Invoice number |

---

## 5. DETALLES (Products)

| XML Element | Odoo Source |
|:------------|:------------|
| `codigoInterno` | `product.default_code` |
| `descripcion` | `product.name` |
| `cantidad` | `move_line.qty_done` |

---

**Data Mapping Classification**: ISO 9001:2015 Controlled
