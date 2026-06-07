# CHANGE MANAGER DEFINITIVE REFERENCE GUIDE
## Lic. Andrea Cambio, Prosci Certified

**Document ID**: CHANGE-DRG-001
**Version**: 2.0 (Enterprise Grade)
**Date**: 2026-01-22

---

## 1. CHANGE IMPACT ASSESSMENT

### 1.1 Stakeholder Group Analysis
| Group | Population | Impact Level | Key Concerns |
|:------|:-----------|:-------------|:-------------|
| **Accountants** | 5-10 | **High** | Tax complexity, SRI errors |
| **Sales** | 10-20 | Medium | Invoice workflow changes |
| **Purchasing** | 3-5 | Medium | Withholding requirements |
| **Warehouse** | 5-10 | Low | Guía process |
| **HR** | 2-3 | **High** | Payroll accuracy |
| **IT Admin** | 1-2 | **High** | System configuration |

### 1.2 Resistance Risk Matrix
| Group | Risk Level | Drivers | Mitigation |
|:------|:-----------|:--------|:-----------|
| Accountants | Medium | Fear of errors, complexity | Extra training, sandbox |
| HR | **High** | Payroll responsibility | 1-on-1 support, parallel run |
| Sales | Low | Faster invoicing benefit | Benefits demo |
| Warehouse | Low | Simple process | Quick reference cards |

---

## 2. TRAINING PROGRAM

### 2.1 Role-Based Training Matrix
| Role | Modules | Hours | Format |
|:-----|:--------|:------|:-------|
| **Accountant** | base, edi, withholding, reports | 8 | Workshop + hands-on |
| **Sales** | base, edi, pos | 4 | Workshop |
| **Purchasing** | purchase, customs, withholding | 6 | Workshop + hands-on |
| **Warehouse** | stock_guia | 2 | Quick training |
| **HR** | hr_payroll | 8 | Workshop + hands-on |
| **IT Admin** | ALL | 16 | Technical deep-dive |

### 2.2 Training Curriculum Detail

#### 2.2.1 Accountant Track (8 hours)
| Session | Duration | Topics |
|:--------|:---------|:-------|
| 1. COA & Taxes | 1.5 hr | NEC structure, tax configuration |
| 2. Electronic Invoicing | 2 hr | Invoice creation, SRI status, errors |
| 3. Withholdings | 2 hr | Creating retentions, 5-day rule |
| 4. Reports | 1.5 hr | ATS, Form 103/104, audits |
| 5. Practice Lab | 1 hr | Hands-on exercises |

#### 2.2.2 HR Track (8 hours)
| Session | Duration | Topics |
|:--------|:---------|:-------|
| 1. Employee Setup | 1 hr | Master data, contracts |
| 2. Contract Management | 1 hr | Types, SUT registration |
| 3. Payroll Processing | 3 hr | Salary rules, IESS, deductions |
| 4. Décimos & Benefits | 1.5 hr | 13th, 14th, Utilidades, Fondos |
| 5. Terminations | 1.5 hr | Liquidation calculator |

---

## 3. TRAINING MATERIALS

### 3.1 Material Inventory
| Material | Format | Audience | Status |
|:---------|:-------|:---------|:-------|
| User Manual | PDF (100+ pages) | All users | Ready |
| Quick Reference Cards | Laminated PDF | Field users | Ready |
| Video Tutorials | MP4 (20 videos) | Self-paced | Ready |
| FAQ Document | PDF | All users | Ready |
| Technical Admin Guide | PDF | IT | Ready |

### 3.2 Quick Reference Card Content
| Card | Key Topics |
|:-----|:-----------|
| Invoice Creation | Steps, SRI status icons, error handling |
| Withholding | 5-day rule, tax codes, workflow |
| Guía de Remisión | When required, fleet selection |
| Payroll Run | Monthly checklist, IESS submission |

---

## 4. GO-LIVE SUPPORT MODEL

### 4.1 Hypercare Schedule
| Week | Support Level | On-Site | Helpdesk |
|:-----|:--------------|:--------|:---------|
| Week 1 | **Full** | All trainers | 24/7 |
| Week 2 | High | 2 trainers | Business hours + |
| Week 3 | Medium | 1 trainer | Business hours |
| Week 4 | Standard | As needed | Business hours |
| Week 5+ | BAU | Scheduled | Normal SLA |

### 4.2 Escalation Path
```
Level 1: Power User (Department)
    ↓ 15 min unresolved
Level 2: Helpdesk
    ↓ 30 min unresolved
Level 3: IT Administrator
    ↓ 1 hr unresolved
Level 4: Vendor Support
```

### 4.3 Issue Categories
| Category | Response SLA | Resolution SLA |
|:---------|:-------------|:---------------|
| Critical (SRI down) | 15 min | 2 hr |
| High (Can't invoice) | 30 min | 4 hr |
| Medium (Workaround exists) | 2 hr | 24 hr |
| Low (Question) | 24 hr | 48 hr |

---

## 5. ADOPTION METRICS

### 5.1 KPIs
| Metric | Target | Measurement |
|:-------|:-------|:------------|
| Login rate | 100% by Week 2 | Daily logins ÷ Total users |
| E-invoice adoption | >95% by Week 3 | E-invoices ÷ Total invoices |
| Error rate | <5% by Week 4 | SRI rejections ÷ Total sent |
| Support tickets | <10/week by Week 4 | Ticket count |
| User satisfaction | >4.0/5.0 | Survey |

### 5.2 Adoption Dashboard
```python
def calculate_adoption_score(week):
    metrics = {
        'login': active_users() / total_users(),
        'einvoice': einvoices_created() / total_invoices(),
        'errors': 1 - (sri_errors() / sri_sends()),
        'tickets': max(0, 1 - (tickets_opened() / 50)),
        'satisfaction': survey_score() / 5.0
    }
    weights = {
        'login': 0.15,
        'einvoice': 0.30,
        'errors': 0.25,
        'tickets': 0.15,
        'satisfaction': 0.15
    }
    return sum(metrics[k] * weights[k] for k in metrics)
```

---

## 6. COMMUNICATION PLAN

### 6.1 Phase-Based Messaging
| Phase | Timing | Message | Channel |
|:------|:-------|:--------|:--------|
| **Awareness** | Week -4 | "Change is coming: New ERP" | Email, All-hands |
| **Understanding** | Week -3 | "What's changing for YOU" | Role-based sessions |
| **Training** | Week -2/-1 | "Here's how it works" | Training sessions |
| **Go-Live** | Week 0 | "We're LIVE! Support available" | All channels |
| **Reinforcement** | Week +2 | "Celebrating early wins" | Newsletter |
| **Sustainment** | Month +1 | "Advanced features & tips" | Training drop-in |

### 6.2 Communication Channels
| Channel | Use For | Frequency |
|:--------|:--------|:----------|
| Email | Formal announcements | Weekly |
| Slack/Teams | Quick updates, support | Daily |
| Intranet | Documentation, FAQs | Always available |
| Town Hall | Major announcements | Monthly |
| 1-on-1 | Individual concerns | As needed |

---

## 7. POST-GO-LIVE OPTIMIZATION

### 7.1 Continuous Improvement Cycle
```
Week 2: Collect feedback (Survey 1)
Week 4: Address quick wins, plan improvements
Week 8: Collect feedback (Survey 2)
Week 12: Optimization release
```

### 7.2 Success Criteria for Closure
| Criterion | Threshold |
|:----------|:----------|
| All users trained | 100% |
| Login adoption | ≥95% |
| E-invoice success rate | ≥95% |
| Support tickets | <5/week |
| User satisfaction | ≥4.0/5.0 |
| No critical issues | 0 open P1s |

---

## 8. AI AGENT COMMANDS

### 8.1 Adoption Monitoring
```
"Show training completion by department"
"List users who haven't logged in this week"
"What is our e-invoice adoption rate?"
"Show support ticket trend"
```

### 8.2 Support Management
```
"Show open support tickets by category"
"Who are the top support requesters?"
"What are the most common issues?"
```

### 8.3 User Feedback
```
"What is our current user satisfaction score?"
"Show feedback themes from last survey"
"Schedule training refresher for struggling users"
```

---

**Document Classification**: Change & Training Management
**Methodology**: Prosci ADKAR + Agile
**Last Updated**: 2026-01-22
