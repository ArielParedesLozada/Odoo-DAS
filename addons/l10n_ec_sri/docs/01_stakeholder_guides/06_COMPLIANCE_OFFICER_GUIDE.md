# COMPLIANCE OFFICER DEFINITIVE REFERENCE GUIDE
## Ing. Sofía Cumplimiento, CIA

**Document ID**: COMP-DRG-001
**Version**: 2.0 (Enterprise Grade)
**Date**: 2026-01-22

---

## 1. REGULATORY CALENDAR (2026)

### 1.1 Monthly Deadlines (by RUC 9th Digit)
| 9th Digit | Day | Forms Due |
|:----------|:----|:----------|
| 1 | 10th | 103, 104, ATS (prior month) |
| 2 | 12th | 103, 104, ATS (prior month) |
| 3 | 14th | 103, 104, ATS (prior month) |
| 4 | 16th | 103, 104, ATS (prior month) |
| 5 | 18th | 103, 104, ATS (prior month) |
| 6 | 20th | 103, 104, ATS (prior month) |
| 7 | 22nd | 103, 104, ATS (prior month) |
| 8 | 24th | 103, 104, ATS (prior month) |
| 9 | 26th | 103, 104, ATS (prior month) |
| 0 | 28th | 103, 104, ATS (prior month) |

### 1.2 Annual Calendar
| Month | Deadline | Obligation | Responsible |
|:------|:---------|:-----------|:------------|
| January | 31st | Form 107 (IR Rel. Dependencia) | HR |
| March | 15th (Costa) | Décimo Cuarto | HR |
| March-April | Per 9th digit | Form 101/102 (IR Annual) | CFO |
| April | 15th | Utilidades (15%) | HR |
| April | 30th | Supercias Financials | CFO |
| August | 15th (Sierra) | Décimo Cuarto | HR |
| December | 24th | Décimo Tercero | HR |
| Monthly | Last day | IESS Planilla | HR |

---

## 2. FORM SUBMISSION MATRIX

### 2.1 Form 103 - Retenciones en la Fuente
| Field | Source | Odoo Query |
|:------|:-------|:-----------|
| Casillero 301 | IR 1% | `tax_code='ret_ir_1'` |
| Casillero 302 | IR 2% | `tax_code='ret_ir_2'` |
| Casillero 303 | IR 10% (prof) | `tax_code='ret_ir_10'` |
| ... | ... | ... |

### 2.2 Form 104 - IVA Mensual
| Field | Source | Odoo Query |
|:------|:-------|:-----------|
| Casillero 401 | Ventas 15% | `tax_group='vat_15_sale'` |
| Casillero 411 | Compras 15% | `tax_group='vat_15_purchase'` |
| Casillero 531 | IVA por pagar | Calculated |
| Casillero 605 | Crédito tributario | Calculated |

### 2.3 ATS (Anexo Transaccional Simplificado)
| Section | Content | Module |
|:--------|:--------|:-------|
| Ventas | All sales invoices | `l10n_ec_reports` |
| Compras | All purchase invoices | `l10n_ec_reports` |
| Retenciones | All withholdings issued | `l10n_ec_reports` |
| Anulados | Voided documents | `l10n_ec_reports` |

---

## 3. DOCUMENT RETENTION POLICY

### 3.1 Retention Periods
| Document Type | Period | Legal Basis | Storage |
|:--------------|:-------|:------------|:--------|
| E-Invoices (XML) | **7 years** | LORTI Art. 55 | `ir.attachment` |
| E-Withholdings | **7 years** | LORTI | `ir.attachment` |
| Accounting entries | **7 years** | NEC | PostgreSQL |
| Payroll records | **7 years** | CT Art. 42 | PostgreSQL |
| Contracts | **Indefinite** | CT Art. 19 | PostgreSQL |
| Financial statements | **10 years** | Ley Compañías | Archive |

### 3.2 Destruction Policy
- **After retention period**: Document destruction committee
- **Destruction log**: Maintained for 3 years
- **Exception**: Under audit = extend retention

---

## 4. PENALTY SCHEDULE

### 4.1 SRI Penalties (Código Tributario)
| Violation | Base Penalty | Max | Interest |
|:----------|:-------------|:----|:---------|
| Late Form 104 | 3% per month | 100% of tax | Yes |
| Late Form 103 | 3% per month | 100% of tax | Yes |
| Omitted invoice | $30 per document | No max | No |
| Late ATS | $30 per document | No max | No |
| Invalid XML | Rejection only | N/A | N/A |

### 4.2 IESS Penalties
| Violation | Penalty |
|:----------|:--------|
| Late contribution | Interest + administrative fine |
| Omitted affiliation | Back payment + penalties |
| Late entry notice | Administrative fine |
| Fraud | Criminal prosecution |

### 4.3 Labor Penalties
| Violation | Penalty | CT Reference |
|:----------|:--------|:-------------|
| Late Décimo 13 | 100% surcharge | Art. 95 |
| Late Décimo 14 | 100% surcharge | Art. 97 |
| Unregistered contract | SUT fine | Art. 42 |
| Missing Rol de Pagos | Inspection fine | Art. 42 |

---

## 5. COMPLIANCE MONITORING DASHBOARD

### 5.1 Key Metrics
| Metric | Target | Alert Threshold |
|:-------|:-------|:----------------|
| E-invoice success rate | >99% | <98% |
| Authorization time | <5 min | >30 min |
| Withholding timeliness | 100% in 5 days | Any late |
| ATS submission | On deadline | 3 days before |
| IESS planilla | On deadline | 5 days before |

### 5.2 Compliance Score Formula
```python
def compliance_score(month):
    metrics = {
        'einvoice_success': einvoice_success_rate(month),
        'retention_timeliness': retention_timeliness_rate(month),
        'form_submission': forms_on_time(month),
        'iess_contribution': iess_on_time(month),
    }
    weights = {
        'einvoice_success': 0.3,
        'retention_timeliness': 0.25,
        'form_submission': 0.25,
        'iess_contribution': 0.2,
    }
    return sum(metrics[k] * weights[k] for k in metrics)
```

---

## 6. ALERT SCHEDULE

### 6.1 System Alerts
| Alert | Timing | Recipients |
|:------|:-------|:-----------|
| Form 104 due | 5 days before | CFO, Compliance |
| Form 103 due | 5 days before | CFO, Compliance |
| ATS due | 3 days before | Accountant |
| Certificate expiry | 30 days before | IT, Compliance |
| IESS planilla | 5 days before | HR |
| Décimo payment | 15 days before | HR, CFO |
| Utilidades | 30 days before | HR, CFO |

---

## 7. AUDIT RESPONSE PROTOCOL

### 7.1 SRI Audit
| Phase | Action | Timeline |
|:------|:-------|:---------|
| Notification | Acknowledge receipt | 5 days |
| Information request | Gather documents | 10 days |
| Submission | Deliver via portal | Per notice |
| Clarification | Respond to queries | 5 days each |
| Resolution | Review determination | 20 days appeal |

### 7.2 Document Preparation
```
"Generate audit package for SRI for period 2025-01 to 2025-12"
→ Includes:
   - All authorized XMLs
   - ATS submissions
   - Form 104 declarations
   - Withholding certificates
   - Accounting ledger
```

---

## 8. AI AGENT COMMANDS

### 8.1 Deadline Monitoring
```
"What filings are due this month?"
"Show compliance calendar for Q1 2026"
"Are we on track for Form 104 deadline?"
```

### 8.2 Audit Preparation
```
"Generate compliance status report for 2025"
"List documents approaching retention expiry"
"Show all rejected SRI transmissions this quarter"
```

### 8.3 Penalty Prevention
```
"Calculate potential penalty exposure for January"
"Show late withholdings (5-day rule violations)"
"Are there any Consumidor Final invoices over $50?"
```

---

**Document Classification**: Compliance & Audit Reference
**Regulatory Sources**: Código Tributario, LORTI, CT, IESS
**Last Verified**: 2026-01-22
