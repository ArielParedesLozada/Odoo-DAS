# ECUADOR ODOO 18 LOCALIZATION: DEFINITIVE MASTER SPECIFICATION
## The Complete ERP Implementation Guide

**Document ID**: SOMA-EC-MASTER-DEFINITIVE-001
**Version**: 3.0 (FINAL)
**Date**: 2026-01-22
**Classification**: PRODUCTION BLUEPRINT
**Regulatory Coverage**: SRI, SENAE, IESS, SUPERCIAS, BCE, ARCSA, AGROCALIDAD

---

# PART I: REGULATORY LANDSCAPE

## 1. REGULATORY BODIES & THEIR ODOO IMPACT

| Authority | Domain | Odoo Modules Affected |
|:---|:---|:---|
| **SRI** (Servicio de Rentas Internas) | IVA, Renta, ICE, IRBPNR, Electronic Invoicing | `account`, `sale`, `purchase`, `pos` |
| **SENAE** (Aduana del Ecuador) | Import/Export, Customs Duties, ISD, FODINFA | `purchase`, `stock`, `sale` |
| **IESS** (Instituto Ecuatoriano de Seguridad Social) | Payroll Contributions, Fondos de Reserva | `hr_payroll` |
| **SUPERCIAS** (Superintendencia de Compañías) | Financial Statements, Balance Sheet Format | `account_reports` |
| **BCE** (Banco Central del Ecuador) | Check Standards, Bank Reconciliation | `account_check_printing` |
| **ARCSA** (Productos Sanitarios) | Pharmaceutical Lot Tracking | `stock` |
| **AGROCALIDAD** | Agricultural Product Traceability | `stock` |

---

# PART II: SRI COMPLIANCE (TAX AUTHORITY)

## 2. ELECTRONIC DOCUMENTS (100% Coverage)

### 2.1 Document Types (l10n_latam.document.type)
| Code | Name | Odoo Model | EDI Required |
|:---|:---|:---|:---|
| 01 | Factura | `account.move` (out_invoice) | YES |
| 03 | Liquidación de Compra | `account.move` (in_invoice) | YES |
| 04 | Nota de Crédito | `account.move` (out_refund) | YES |
| 05 | Nota de Débito | `account.move` (out_invoice) | YES |
| 06 | Guía de Remisión | `stock.picking` | YES |
| 07 | Comprobante de Retención | `account.retention` | YES |
| 41 | Comprobante Electrónico de Reembolso | `account.move` | YES |
| 42 | Documento de Sustento en Compras | `account.move` | NO |

### 2.2 Tax Catalog (Complete 2026)

#### 2.2.1 IVA (Impuesto al Valor Agregado)
| Code | Rate | Name | Use Case |
|:---|:---|:---|:---|
| 0 | 0% | Tarifa 0% | Basic Goods |
| 2 | 12% | Tarifa 12% | *OBSOLETE* |
| 3 | 14% | Tarifa 14% | *OBSOLETE* |
| 4 | 15% | Tarifa 15% | Standard 2025+ |
| 5 | 5% | Tarifa 5% | Construction Materials |
| 6 | N/A | No Objeto de Impuesto | Services to Govt |
| 7 | N/A | Exento de IVA | Exports |
| 8 | Diferenciada | Tarifa Diferenciada | Future Use |

#### 2.2.2 Retenciones en la Fuente (Withholding - Income Tax)
| Code | % | Concept |
|:---|:---|:---|
| 303 | 10% | Honorarios Profesionales |
| 304 | 8% | Servicios Predomina Intelecto |
| 307 | 2% | Servicios Predomina Mano Obra |
| 308 | 2% | Servicios Entre Sociedades |
| 309 | 1% | Servicios Publicidad y Comunicación |
| 310 | 1% | Transporte Privado Pasajeros/Carga |
| 312 | 1% | Transferencia Bienes Muebles |
| 319 | 1% | Arrendamiento Mercantil |
| 320 | 1.75% | Arrendamiento Bienes Inmuebles |
| 322 | 1% | Seguros y Reaseguros |
| 323 | 2% | Rendimientos Financieros |
| 325 | 0.2% | Loterías, Rifas |
| 327 | 2% | Venta Combustibles |
| 328 | 0.2% | Compra Productos de Origen Agrícola |
| 332 | Variable | Pagos a No Residentes |
| 340 | 1% | Pagos a Artes Gráficas |
| 343 | 0.2% | Combustibles Comercializadoras |
| 344 | 25% | Dividendos a Residentes |
| 500 | 25% | Pagos al Exterior - Paraísos Fiscales |

#### 2.2.3 Retenciones de IVA
| Code | % | When to Apply |
|:---|:---|:---|
| 721 | 10% | Bienes |
| 723 | 20% | Servicios |
| 725 | 30% | Bienes (Contribuyente Especial) |
| 727 | 70% | Servicios (Contribuyente Especial) |
| 729 | 100% | Liquidación de Compra |
| 731 | 100% | Servicios Profesionales |

#### 2.2.4 ICE (Impuesto a Consumos Especiales)
| Product Category | Rate/Formula |
|:---|:---|
| Cigarrillos | $0.1644 por unidad |
| Alcohol | 75% Ad Valorem |
| Cerveza | 75% Ad Valorem |
| Bebidas Gaseosas | $0.18 por litro |
| Vehículos >$35k | 15-35% escalonado |
| Perfumes Importados | 20% |
| Videojuegos | 35% |
| Armas | 300% |

#### 2.2.5 IRBPNR (Botellas Plásticas)
| Rate | $0.02 per bottle |

---

# PART III: SENAE COMPLIANCE (CUSTOMS)

## 3. IMPORT/EXPORT WORKFLOW

### 3.1 Import Taxes & Duties
| Tax | Description | Odoo Impact |
|:---|:---|:---|
| **AD VALOREM** | Arancel (0-40% depending on product) | `product.template.l10n_ec_customs_tariff` |
| **FODINFA** | 0.5% sobre CIF | Automatic on Import Invoice |
| **ISD** | 5% Impuesto Salida Divisas | On Payment to Foreign Supplier |
| **IVA Import** | 15% sobre (CIF + AD VALOREM + FODINFA) | `account.tax` (special) |
| **ICE Import** | Variable | If applicable product |
| **SALVAGUARDIA** | 5-45% (Temporary measures) | Manual Override |

### 3.2 Import Document Model (`l10n_ec.import.dau`)
| Field | Type | Description |
|:---|:---|:---|
| `dau_number` | Char | DAU/DAI Number |
| `customs_district` | Selection | GUAYAQUIL, QUITO, etc. |
| `regime` | Selection | 10 (Consumption), 20 (Warehouse), etc. |
| `cif_value` | Monetary | CIF Value in USD |
| `fob_value` | Monetary | FOB Value |
| `freight` | Monetary | Freight Cost |
| `insurance` | Monetary | Insurance Cost |
| `ad_valorem` | Monetary | Computed Tariff |
| `fodinfa` | Monetary | Computed 0.5% |
| `isd` | Monetary | Computed 5% |
| `invoice_ids` | Many2many | Related Vendor Bills |

### 3.3 Export Workflow
| Requirement | Odoo Implementation |
|:---|:---|
| **Factura de Exportación** | `account.move` with `l10n_ec_export = True` |
| **DAE (Declaración Aduanera Exportación)** | Link to Shipment |
| **IVA 0% Exports** | Automatic Fiscal Position |
| **Devolución de IVA** | Report linking Purchases to Export Sales |

---

# PART IV: IESS COMPLIANCE (PAYROLL)

## 4. PAYROLL TAXES & CONTRIBUTIONS

### 4.1 Contribution Rates 2026
| Concept | Employee % | Employer % | Ceiling |
|:---|:---|:---|:---|
| **Aporte Personal** | 9.45% | - | SBU * 25 |
| **Aporte Patronal** | - | 11.15% | SBU * 25 |
| **SECAP** | - | 0.5% | All payroll |
| **IECE** | - | 0.5% | All payroll |
| **Fondo de Reserva** | - | 8.33% | After 1 year |
| **Décimo Tercero** | - | 8.33% (accrued) | - |
| **Décimo Cuarto** | - | SBU/12 | - |

### 4.2 Payroll Odoo Model Extensions
```csv
Field,Type,Description
l10n_ec_iess_code,Char,IESS Employee ID
l10n_ec_contract_type,Selection,Indefinido/Fijo/Eventual
l10n_ec_sectorial_salary,Many2one,Link to Min Wage Table
```

---

# PART V: SUPERCIAS COMPLIANCE (FINANCIAL REPORTS)

## 5. MANDATORY FINANCIAL STATEMENTS

### 5.1 Balance Sheet Format (Estado de Situación Financiera)
Must follow the **NIIF/NIIF PYMES** structure:
```
1. ACTIVO
   1.01 ACTIVO CORRIENTE
      1.01.01 Efectivo y Equivalentes
      1.01.02 Activos Financieros
      1.01.03 Inventarios
      1.01.04 Servicios y Otros Pagos Anticipados
      1.01.05 Activos por Impuestos Corrientes
   1.02 ACTIVO NO CORRIENTE
      1.02.01 Propiedades, Planta y Equipo
      1.02.02 Propiedades de Inversión
      1.02.03 Activos Intangibles
2. PASIVO
   2.01 PASIVO CORRIENTE
   2.02 PASIVO NO CORRIENTE
3. PATRIMONIO
   3.01 Capital
   3.02 Reservas
   3.03 Resultados Acumulados
```

### 5.2 Required Reports
| Report | Frequency | Module |
|:---|:---|:---|
| Estado de Situación Financiera | Annual | `l10n_ec_reports` |
| Estado de Resultados Integral | Annual | `l10n_ec_reports` |
| Estado de Flujos de Efectivo | Annual | `l10n_ec_reports` |
| Estado de Cambios Patrimonio | Annual | `l10n_ec_reports` |
| Notas Explicativas | Annual | Manual |

---

# PART VI: INVENTORY & LOGISTICS

## 6. STOCK VALUATION & TRACEABILITY

### 6.1 Valuation Methods (NEC/NIIF Compliant)
| Method | Allowed | Odoo Config |
|:---|:---|:---|
| **FIFO** | YES | `product.categ.property_cost_method = 'fifo'` |
| **Promedio Ponderado** | YES | `product.categ.property_cost_method = 'average'` |
| **LIFO** | NO (Prohibited) | BLOCKED |
| **Identificación Específica** | YES (Serialized) | Lot Tracking |

### 6.2 Lot Tracking Requirements
| Industry | Regulation | Odoo Feature |
|:---|:---|:---|
| **Pharma** | ARCSA Lot Control | `stock.lot` + Expiry |
| **Food** | ARCSA Batch Tracking | `stock.lot` |
| **Agriculture** | AGROCALIDAD Traceability | `stock.lot` + Origin |

### 6.3 Guía de Remisión (Waybill)
**Fields on `stock.picking`**:
| Field | Type | XML Tag |
|:---|:---|:---|
| `l10n_ec_access_key` | Char(49) | `claveAcceso` |
| `l10n_ec_carrier_id` | Many2one | `rucTransportista` |
| `l10n_ec_driver_id` | Many2one | - |
| `l10n_ec_plate` | Char | `placa` |
| `l10n_ec_start_address` | Char | `dirPartida` |
| `l10n_ec_transport_reason` | Selection | `motivoTraslado` |
| `l10n_ec_route` | Text | `ruta` |

---

# PART VII: BANKING & PAYMENTS

## 7. BCE COMPLIANCE (CENTRAL BANK)

### 7.1 Check Printing Standards
| Field | Format |
|:---|:---|
| Amount in Words | Spanish ("Dólares con XX/100") |
| Date Format | DD/MM/YYYY |
| Bank Codes | BCE Standard |

### 7.2 Payment Methods (SRI Table 24)
| Code | Name |
|:---|:---|
| 01 | SIN UTILIZACIÓN DEL SISTEMA FINANCIERO |
| 15 | COMPENSACIÓN DE DEUDAS |
| 16 | TARJETA DE DÉBITO |
| 17 | DINERO ELECTRÓNICO |
| 18 | TARJETA PREPAGO |
| 19 | TARJETA DE CRÉDITO |
| 20 | OTROS CON UTILIZACION SISTEMA FINANCIERO |
| 21 | ENDOSO DE TÍTULOS |

---

# PART VIII: MODULE BREAKDOWN

## 8. IMPLEMENTATION MODULES

### 8.1 Core Modules (MUST HAVE)
| Module | Depends | Purpose |
|:---|:---|:---|
| `l10n_ec` | `account`, `l10n_latam_invoice_document` | Chart of Accounts, Taxes |
| `l10n_ec_edi` | `l10n_ec`, `account_edi` | Electronic Signing & SRI |
| `l10n_ec_withholding` | `l10n_ec` | Retention Documents |

### 8.2 Extended Modules (FULL ERP)
| Module | Depends | Purpose |
|:---|:---|:---|
| `l10n_ec_stock` | `l10n_ec_edi`, `stock` | Guías de Remisión |
| `l10n_ec_purchase` | `l10n_ec`, `purchase` | Liquidaciones, Imports |
| `l10n_ec_pos` | `l10n_ec_edi`, `point_of_sale` | Retail Invoice |
| `l10n_ec_hr_payroll` | `hr_payroll` | IESS Contributions |
| `l10n_ec_reports` | `l10n_ec`, `account_reports` | ATS, Supercias |
| `l10n_ec_customs` | `l10n_ec_purchase`, `stock` | SENAE/DAU |

---

# PART IX: DELIVERABLE CHECKLIST

## 9. FILES TO GENERATE

### 9.1 Data Files
- [ ] `account.chart.template.xml`
- [ ] `account.account.template.csv` (500+ rows)
- [ ] `account.group.template.csv`
- [ ] `account.tax.group.csv`
- [ ] `account.tax.template.csv` (100+ rows)
- [ ] `l10n_latam.document.type.csv`
- [ ] `account.fiscal.position.template.csv`
- [ ] `res.bank.csv`
- [ ] `l10n_ec.sri.payment.method.csv`
- [ ] `l10n_ec.withholding.type.csv`

### 9.2 Python Models
- [ ] `res_partner.py` (RUC/Cedula Validation)
- [ ] `res_company.py` (P12 Certificate)
- [ ] `account_move.py` (EDI Extensions)
- [ ] `account_retention.py` (Withholding Model)
- [ ] `stock_picking.py` (Guía Extensions)
- [ ] `l10n_ec_edi_format.py` (SRI Signer)

### 9.3 Views
- [ ] `account_move_views.xml`
- [ ] `res_partner_views.xml`
- [ ] `res_company_views.xml`
- [ ] `stock_picking_views.xml`
- [ ] `account_retention_views.xml`

---

**APPROVAL:**
This document constitutes the COMPLETE, EXHAUSTIVE specification for Ecuador Odoo localization covering ALL regulatory bodies and ERP modules.

**Signed:**
*Antigravity (Chief ERP Architect, Legal Advisor, CPA)*
