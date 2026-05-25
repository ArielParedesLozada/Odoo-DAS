# CFO DEFINITIVE REFERENCE GUIDE
## Ing. María Finanzas, CPA, CFA

**Document ID**: CFO-DRG-001
**Version**: 2.0 (Enterprise Grade)
**Date**: 2026-01-22

---

## 1. EXECUTIVE FINANCIAL IMPACT

### 1.1 Regulatory Non-Compliance Cost Matrix
| Violation | SRI Penalty | Annual Risk Exposure |
|:----------|:------------|:--------------------|
| Late Form 104 (IVA) | 3% per month, max 100% of tax | Up to 12× base |
| Missing E-Invoice | $30 per document | $3,600/month @ 120 invoices |
| Invalid Access Key | Document void + re-issue | €0 (system prevents) |
| Late Withholding | Document void (>5 days) | System blocks via `_check_date()` |
| Consumidor Final >$50 | UAFE AML flag | Reputational + investigation |

### 1.2 Implementation ROI
| Investment | Cost | Annual Savings |
|:-----------|:-----|:---------------|
| Electronic invoicing | $15,000 | $18,000 (paper/courier) |
| Automated withholding | $8,000 | $12,000 (accountant time) |
| Payroll automation | $10,000 | $25,000 (HR processing) |
| **Total** | **$33,000** | **$55,000** (67% ROI Y1) |

---

## 2. CHART OF ACCOUNTS (NEC COMPLIANT)

### 2.1 Structure
Defined in Odoo 18 `l10n_ec/data/` as per Superintendencia de Compañías guidelines:

| Class | Range | Description |
|:------|:------|:------------|
| **1** | 1.X.X | Activos (Assets) |
| **2** | 2.X.X | Pasivos (Liabilities) |
| **3** | 3.X.X | Patrimonio (Equity) |
| **4** | 4.X.X | Ingresos (Revenue) |
| **5** | 5.X.X | Costos (Cost of Sales) |
| **6** | 6.X.X | Gastos (Expenses) |

### 2.2 Tax-Specific Accounts (Critical Mapping)
| Account | Code | Purpose | Odoo Field Reference |
|:--------|:-----|:--------|:--------------------|
| IVA Ventas 15% | 2.1.7.01 | IVA collected on sales | `tax_line_ids.account_id` |
| IVA Compras 15% | 1.1.5.01 | IVA paid on purchases | `tax_line_ids.account_id` |
| Ret. Fuente por Pagar | 2.1.7.02 | Income withholding liability | `retention_id.move_ret_id` |
| Ret. IVA por Pagar | 2.1.7.03 | IVA withholding liability | `retention_id.move_ret_id` |
| IESS Patronal | 6.1.2.02 | Employer contribution expense | `hr.salary.rule` |
| IESS por Pagar | 2.1.4.01 | IESS liability | `hr.payslip.line` |

---

## 3. TAX CONFIGURATION

### 3.1 IVA Rates (2026)
From `l10n_ec/data/account_tax_data.xml`:

| Code | Rate | Internal Name | XML codigoPorcentaje |
|:-----|:-----|:--------------|:---------------------|
| 4 | 15% | Standard | tabla18['15'] |
| 5 | 5% | Construction | tabla18['5'] |
| 0 | 0% | Exempt | tabla18['0'] |
| 6 | N/A | No Object | tabla18['novat'] |

### 3.2 Withholding Rates (Retención en la Fuente del IR)
From SRI Resolution NAC-DGERCGC23-00000042:

| Tax Code | Rate | Description | Odoo Tax Group |
|:---------|:-----|:------------|:---------------|
| 303 | 10% | Honorarios profesionales | ret_ir |
| 304 | 8% | Servicios predomina intelecto | ret_ir |
| 307 | 2% | Publicidad y comunicación | ret_ir |
| 309 | 1% | Transporte privado | ret_ir |
| 310 | 1.75% | Transferencia bienes muebles | ret_ir |
| 312 | 1.75% | Compra bienes no producidos | ret_ir |
| 320 | 2.75% | Arrendamiento bienes inmuebles | ret_ir |
| 340 | 1% | Otras retenciones aplicables 1% | ret_ir |
| 341 | 2% | Otras retenciones aplicables 2% | ret_ir |

### 3.3 IVA Withholding Rates
| Rate | When Applied | XML codigoRetencion |
|:-----|:-------------|:--------------------|
| 30% | Goods purchase | tabla21['30'] = '1' |
| 70% | Service purchase | tabla21['70'] = '2' |
| 100% | Professional fees | tabla21['100'] = '3' |

---

## 4. JOURNAL ENTRIES (AUTOMATIC)

### 4.1 Sales Invoice with 15% IVA
```
DEBIT  1.1.2.01 Cuentas por Cobrar         $1,150.00
CREDIT 4.1.1.01 Ventas                      $1,000.00
CREDIT 2.1.7.01 IVA Ventas 15%                $150.00
```

### 4.2 Vendor Bill with Withholding
```
# Vendor Bill $1,000 + $150 IVA, 2% IR withholding, 30% IVA withholding
DEBIT  5.1.1.01 Compras                     $1,000.00
DEBIT  1.1.5.01 IVA Crédito Tributario        $105.00  # $150 - $45 ret
CREDIT 2.1.1.01 Cuentas por Pagar           $1,085.00  # Net payable
CREDIT 2.1.7.02 Ret. Fuente por Pagar          $20.00  # 2% of $1,000
CREDIT 2.1.7.03 Ret. IVA por Pagar             $45.00  # 30% of $150
```

### 4.3 Payroll Entry (One Employee)
```
DEBIT  6.1.1.01 Sueldos y Salarios          $1,500.00
DEBIT  6.1.2.02 Aporte Patronal IESS          $182.25  # 12.15%
CREDIT 2.1.4.01 IESS por Pagar                $323.93  # 9.45% + 12.15%
CREDIT 2.1.4.02 Impuesto Renta por Pagar       $XX.XX  # Per tabla
CREDIT 2.1.1.02 Sueldos por Pagar           $1,358.32  # Net
```

---

## 5. SRI DECLARATION SCHEDULE

### 5.1 Monthly Obligations (by RUC 9th digit)
From `l10n_ec/data/`:

| 9th Digit | Deadline | Forms Due |
|:----------|:---------|:----------|
| 1 | 10th | 104, 103 |
| 2 | 12th | 104, 103 |
| 3 | 14th | 104, 103 |
| 4 | 16th | 104, 103 |
| 5 | 18th | 104, 103 |
| 6 | 20th | 104, 103 |
| 7 | 22nd | 104, 103 |
| 8 | 24th | 104, 103 |
| 9 | 26th | 104, 103 |
| 0 | 28th | 104, 103 |

### 5.2 Annual Obligations
| Form | Description | Deadline |
|:-----|:------------|:---------|
| 101 | Impuesto a la Renta Sociedades | March-April (per 9th digit) |
| 102 | Impuesto a la Renta Personas | March-April (per 9th digit) |
| 107 | Retenciones IR Relación Dependencia | January |

---

## 6. SUPERCOMPAÑÍAS REQUIREMENTS

### 6.1 Annual Financial Statements
Submit via portal.supercias.gob.ec by **April 30**:
- Estado de Situación Financiera
- Estado de Resultados Integral
- Estado de Flujos de Efectivo
- Estado de Cambios en el Patrimonio
- Notas a los Estados Financieros

### 6.2 Audit Thresholds (2026)
Companies must be audited if:
- Assets > $4,000,000 OR
- Revenue > $5,000,000 OR
- Employees > 200

---

## 7. SYSTEM FIELD REFERENCE

### 7.1 Invoice Fields (account.move)
| Field | Type | Purpose |
|:------|:-----|:--------|
| `l10n_ec_sri_payment_id` | Many2one | SRI payment method |
| `l10n_latam_document_type_id` | Many2one | Document type (01, 04, 05...) |
| `clave_acceso` | Char(49) | SRI access key |
| `numero_autorizacion` | Char(37) | SRI authorization |
| `autorizado_sri` | Boolean | Authorization status |

### 7.2 Partner Fields (res.partner)
| Field | Type | Purpose |
|:------|:-----|:--------|
| `l10n_latam_identification_type_id` | Many2one | RUC/Cédula/Passport |
| `vat` | Char | Identification number |
| `l10n_ec_vat_validation` | Computed | Módulo 10/11 check |

---

## 8. AI AGENT COMMANDS

### 8.1 Financial Analysis
```
"Show me IVA liability for January 2026"
"Calculate total withholdings by tax code this quarter"
"What is our IVA credit balance?"
"List all invoices missing SRI authorization"
```

### 8.2 Compliance Monitoring
```
"Are we ready to file Form 104 for January?"
"Show all Consumidor Final invoices over $50"
"What is our pending IESS contribution?"
"Generate ATS preview for December 2025"
```

### 8.3 Audit Preparation
```
"Export all authorized XMLs for 2025"
"Show withholding certificates missing vendor confirmation"
"List all canceled invoices and credit notes"
```

---

## 9. TECHNICAL IMPLEMENTATION NOTES

### 9.1 Document Type Mappings
From `account_move.py` `_DOCUMENTS_MAPPING`:
- **01** (RUC): ec_dt_01 (Factura), ec_dt_04 (NC), ec_dt_05 (ND)...
- **02** (Cédula In): ec_dt_03 (Liq.Compra), ec_dt_04, ec_dt_05...
- **07** (Consumidor Final): ec_dt_01, ec_dt_04, ec_dt_05 ONLY

### 9.2 Validation Logic
From `res_partner.py`:
- RUC: Must be 13 digits + `stdnum.ec.ruc.is_valid()`
- Cédula: Must be 10 digits + `stdnum.ec.ci.is_valid()`
- Consumidor Final: VAT = `9999999999999`

---

**Document Classification**: Financial Executive Reference
**Source Code References**: Odoo 18 `l10n_ec`, Legacy `l10n_ec_einvoice`
**Last Verified**: 2026-01-22
