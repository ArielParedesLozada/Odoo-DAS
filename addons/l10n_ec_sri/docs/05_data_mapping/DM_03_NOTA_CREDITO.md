# DATA MAPPING: NOTA DE CRÉDITO
## DM_03 - Credit Note XML for SRI

**Document ID**: DM-003 | **Version**: 1.0 | **Date**: 2026-01-22
**Owner**: Tax Manager

---

## 1. OVERVIEW

Credit Note (Nota de Crédito) XML for SRI when correcting/refunding invoices.

---

## 2. XML STRUCTURE

```xml
<?xml version="1.0" encoding="UTF-8"?>
<notaCredito id="comprobante" version="1.1.0">
    <infoTributaria>...</infoTributaria>
    <infoNotaCredito>...</infoNotaCredito>
    <detalles>...</detalles>
    <infoAdicional>...</infoAdicional>
</notaCredito>
```

---

## 3. FIELD MAPPING

| XML Element | Odoo Source | Required |
|:------------|:------------|:---------|
| `codDoc` | '04' (fixed) | ✓ |
| `fechaEmision` | `move.invoice_date` | ✓ |
| `codDocModificado` | Original invoice type | ✓ |
| `numDocModificado` | Original invoice number | ✓ |
| `fechaEmisionDocSustento` | Original invoice date | ✓ |
| `motivo` | `move.narration` | ✓ |
| `valorModificacion` | `move.amount_total` | ✓ |

---

## 4. LINK TO ORIGINAL

```python
# Credit note must reference original invoice
original_invoice = credit_note.reversed_entry_id
num_doc_modificado = original_invoice.l10n_latam_document_number
fecha_doc_sustento = original_invoice.invoice_date
```

---

## 5. REASONS (Motivo)

| Code | Reason |
|:-----|:-------|
| 01 | Devolución |
| 02 | Error en facturación |
| 03 | Descuento |
| 04 | Cambio de condiciones |

---

**Data Mapping Classification**: ISO 9001:2015 Controlled
