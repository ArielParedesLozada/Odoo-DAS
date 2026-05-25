# LEGAL COUNSEL DEFINITIVE REFERENCE GUIDE
## Abg. Elena Derecho, Especialista Tributaria y Laboral

**Document ID**: LEGAL-DRG-001
**Version**: 2.0 (Enterprise Grade)
**Date**: 2026-01-22

---

## 1. REGULATORY LIABILITY FRAMEWORK

### 1.1 Primary Legal References
| Area | Law/Code | Key Articles |
|:-----|:---------|:-------------|
| **Tax** | LORTI | Art. 8-10, 50, 72-89 |
| **Tax** | Código Tributario | Art. 23-26, 89-101 |
| **Labor** | Código del Trabajo | Art. 42-185 |
| **AML** | Ley Orgánica UAFE | Art. 3-5 |
| **Electronic** | Ley Comercio Electrónico | Art. 14-18 |

---

## 2. SRI COMPLIANCE VIOLATIONS & PENALTIES

### 2.1 Electronic Invoicing (From Código Tributario Art. 97-101)
| Violation | Penalty | System Prevention |
|:----------|:--------|:------------------|
| No electronic invoice | $30 per document | Auto-generation on `action_post()` |
| Invalid XML structure | Rejection + rework | `validate_xml()` before send |
| Late transmission (>24hr) | 3% per day, max 100% | `check_date()` validation |
| Unauthorized document | Void + penalty | `autorizado_sri` field check |
| Wrong access key | Document void | `clave_acceso` Módulo 11 validation |

### 2.2 Withholding Violations
| Violation | Legal Reference | System Prevention |
|:----------|:----------------|:------------------|
| Retention >5 days | LORTI Art. 50 | `_check_date()` enforces 5-day rule |
| Wrong retention rate | LORTI Art. 92 | Validated tax templates |
| No retention issued | LORTI Art. 89 | Mandatory on `in_invoice` |

```python
# From l10n_ec_withholding/models/withholding.py (Lines 196-204)
@api.constrains('date')
def _check_date(self):
    if self.date and self.invoice_id:
        inv_date = datetime.strptime(self.invoice_id.date_invoice, '%Y-%m-%d')
        ret_date = datetime.strptime(self.date, '%Y-%m-%d')
        days = ret_date - inv_date
        if days.days not in range(1, 6):  # MUST be within 5 days
            raise ValidationError(utils.CODE_701)
```

---

## 3. UAFE ANTI-MONEY LAUNDERING

### 3.1 Consumidor Final $50 Rule
**Legal Basis**: Ley Orgánica UAFE Art. 3

| Rule | Implementation |
|:-----|:---------------|
| Invoices to CF cannot exceed $50 USD | `_check_consumidor_final_limit()` |
| Above $50 requires identification | Partner validation enforced |
| CF VAT number | `9999999999999` (13 nines) |

```python
# Validation from res_partner.py
def verify_final_consumer(vat):
    return vat == '9' * 13  # Final consumer identified with 9999999999999
```

### 3.2 Non-Reversibility Rule (2026)
**Effective**: January 1, 2026

| Rule | Implementation |
|:-----|:---------------|
| CF invoices cannot be canceled | Override `button_cancel()` |
| Only Credit Notes allowed | Force NC workflow |
| Audit trail required | `message_post()` logging |

---

## 4. LABOR LAW COMPLIANCE (CÓDIGO DEL TRABAJO)

### 4.1 Critical Articles Map
| Article | Topic | System Enforcement |
|:--------|:------|:-------------------|
| Art. 14 | Contract in writing | `hr.contract` creation wizard |
| Art. 42 | Employer obligations | Checklist validation |
| Art. 69-72 | Vacations (15 days) | `hr.leave` allocation |
| Art. 95-96 | Décimo Tercero | Auto-calculation in payslip |
| Art. 97 | Décimo Cuarto | Regional date validation |
| Art. 111-113 | Termination | Liquidation calculator |
| Art. 185 | Desahucio (25% per year) | Automatic computation |
| Art. 188 | Despido intempestivo | 3 months + 1/year formula |

### 4.2 Termination Liability Matrix
| Type | Formula | Risk Level |
|:-----|:--------|:-----------|
| **Renuncia voluntaria** | Proportional only | Low |
| **Desahucio empleador** | 25% × salary × years | Medium |
| **Desahucio trabajador** | 25% × salary × years | Medium |
| **Despido intempestivo** | 3 months + 1 month/year | **High** |
| **Visto bueno empleador** | 0 (if approved) | Low |
| **Visto bueno trabajador** | 25% × salary × years | Medium |

```python
# Despido intempestivo (CT Art. 188)
def despido_indemnization(employee):
    years = tenure_years(employee)
    wage = employee.contract_id.wage
    if years < 3:
        return wage * 3  # 3 months minimum
    else:
        return wage * (years - 3) + (wage * 3)  # +1 month per year after 3
```

---

## 5. DOCUMENT RETENTION REQUIREMENTS

### 5.1 Mandatory Retention Periods
| Document | Period | Legal Basis |
|:---------|:-------|:------------|
| Electronic invoices (XML) | **7 years** | LORTI Art. 55 |
| Withholding certificates | **7 years** | LORTI |
| Accounting entries | **7 years** | NEC/Supercias |
| Payroll records | **7 years** | Código Trabajo |
| Contracts | **Indefinite** | CT Art. 19 |
| Financial statements | **10 years** | Ley Compañías |

### 5.2 System Implementation
| Storage | Odoo Model | Attachment Type |
|:--------|:-----------|:----------------|
| XML authorized | `ir.attachment` | `{clave_acceso}.xml` |
| RIDE PDF | `ir.attachment` | `{clave_acceso}.pdf` |
| Contracts | `hr.contract` | Binary field |

---

## 6. AUDIT READINESS CHECKLIST

### 6.1 SRI Inspection
| Requested | System Location | Export Method |
|:----------|:----------------|:--------------|
| All authorized XMLs | `ir.attachment` | Bulk download |
| Access keys list | `account.move.clave_acceso` | Excel export |
| Authorization numbers | `account.move.numero_autorizacion` | Excel export |
| ATS monthly | `l10n_ec_reports` | XML export |

### 6.2 IESS Inspection
| Requested | System Location | Export Method |
|:----------|:----------------|:--------------|
| Planillas | `hr.payslip` | PDF report |
| Contribution history | IESS sync logs | Dashboard |
| Entry/Exit notices | SUT integration | Verification |

### 6.3 Ministerio del Trabajo Inspection
| Requested | System Location | Export Method |
|:----------|:----------------|:--------------|
| All contracts | `hr.contract` | PDF archive |
| Décimo payments | `hr.payslip` + bank | Reconciliation |
| Vacation records | `hr.leave` | Report |
| Turnover reports | `hr.departure.reason` | Dashboard |

---

## 7. SIGNATURE & AUTHORIZATION MATRIX

### 7.1 Electronic Signature Requirements
| Document | Signer | System Field |
|:---------|:-------|:-------------|
| Factura | Legal Representative | `company.electronic_signature` |
| Retención | Legal Representative | `company.electronic_signature` |
| Guía Remisión | Legal Representative | `company.electronic_signature` |
| Nota Crédito | Legal Representative | `company.electronic_signature` |

### 7.2 Certificate Validity
| Provider | Validity | Renewal Alert |
|:---------|:---------|:--------------|
| Security Data | 2 years | 30 days before |
| ANF Ecuador | 2 years | 30 days before |
| Banco Central | 2 years | 30 days before |

---

## 8. AI AGENT COMMANDS

### 8.1 Compliance Monitoring
```
"Show all retentions issued after 5-day deadline"
"List Consumidor Final invoices over $50"
"Are there any canceled CF invoices? (violation check)"
"Show contracts not registered in SUT"
```

### 8.2 Audit Preparation
```
"Generate document retention report for 2025"
"Export all authorized XMLs for audit"
"Show employees with missing Acta Finiquito"
```

### 8.3 Risk Assessment
```
"What is our exposure from late retentions this month?"
"Calculate potential penalty for late Form 104"
"List any UAFE compliance violations"
```

---

**Document Classification**: Legal & Compliance Reference
**Legal Authority**: LORTI, CT, Código Tributario, UAFE
**Last Verified**: 2026-01-22
