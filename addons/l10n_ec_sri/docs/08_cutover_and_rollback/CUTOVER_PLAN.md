# CUTOVER & ROLLBACK PLAN
## Go-Live Procedure and Recovery Strategy

**Document ID**: CUT-001
**Version**: 1.0
**Classification**: Big 4 Professional Grade

---

## 1. CUTOVER OVERVIEW

### 1.1 Timeline Summary
| Phase | Duration | Window |
|:------|:---------|:-------|
| **Preparation** | 2 weeks before | T-14 to T-1 |
| **Freeze** | 1 day before | T-1 |
| **Cutover** | 8 hours | T (Go-Live Day) |
| **Stabilization** | 2 weeks after | T+1 to T+14 |

### 1.2 Go/No-Go Criteria
| # | Criterion | Required | Actual | Status |
|:--|:----------|:---------|:-------|:-------|
| 1 | All test cases passed | 100% | | ☐ |
| 2 | Data migration validated | Yes | | ☐ |
| 3 | SRI test env approved | Yes | | ☐ |
| 4 | Key users trained | 100% | | ☐ |
| 5 | Rollback tested | Yes | | ☐ |
| 6 | Backup verified | Yes | | ☐ |

---

## 2. CUTOVER SCHEDULE (HOUR-BY-HOUR)

### 2.1 T-1 Day (Preparation)
| Time | Activity | Owner | Duration |
|:-----|:---------|:------|:---------|
| 18:00 | Announce system freeze | PM | 15 min |
| 18:15 | Disable user logins (except IT) | IT | 15 min |
| 18:30 | Export final legacy data | IT | 1 hr |
| 19:30 | Full database backup | DBA | 30 min |
| 20:00 | Backup verification | DBA | 30 min |
| 20:30 | Document current sequences | IT | 30 min |
| 21:00 | End of prep | - | - |

### 2.2 T Day (Go-Live)
| Time | Activity | Owner | Duration | Checkpoint |
|:-----|:---------|:------|:---------|:-----------|
| 00:00 | Start cutover window | PM | - | - |
| 00:15 | Disable legacy system | IT | 15 min | ☐ |
| 00:30 | Final data export | IT | 30 min | ☐ |
| 01:00 | **POINT OF NO RETURN** | PM | - | GO/NO-GO |
| 01:15 | Run data migration scripts | IT | 2 hr | ☐ |
| 03:15 | Data validation scripts | QA | 1 hr | ☐ |
| 04:15 | Switch SRI to Production | IT | 15 min | ☐ |
| 04:30 | Enable Odoo production | IT | 15 min | ☐ |
| 04:45 | Smoke test: Create invoice | QA | 30 min | ☐ |
| 05:15 | Smoke test: SRI authorization | QA | 30 min | ☐ |
| 05:45 | Smoke test: Withholding | QA | 30 min | ☐ |
| 06:15 | Enable user access | IT | 15 min | ☐ |
| 06:30 | Monitor first transactions | Support | 1.5 hr | ☐ |
| 08:00 | **CUTOVER COMPLETE** | PM | - | ☐ |

### 2.3 T+1 (First Business Day)
| Time | Activity | Owner |
|:-----|:---------|:------|
| 08:00 | Support team on-site | Support |
| 08:00-12:00 | Monitor all transactions | IT |
| 12:00 | First SRI batch check | Accounting |
| 17:00 | Day 1 status report | PM |
| 18:00 | End of hypercare Day 1 | - |

---

## 3. DATA MIGRATION CHECKLIST

### 3.1 Master Data
| # | Data Set | Source | Records | Migrated | Validated |
|:--|:---------|:-------|:--------|:---------|:----------|
| 3.1.1 | Chart of Accounts | Standard | ~500 | ☐ | ☐ |
| 3.1.2 | Partners (Customers) | Legacy | [Count] | ☐ | ☐ |
| 3.1.3 | Partners (Vendors) | Legacy | [Count] | ☐ | ☐ |
| 3.1.4 | Products | Legacy | [Count] | ☐ | ☐ |

### 3.2 Transactional Data
| # | Data Set | Source | Records | Migrated | Validated |
|:--|:---------|:-------|:--------|:---------|:----------|
| 3.2.1 | Open A/R Balances | Legacy | [Count] | ☐ | ☐ |
| 3.2.2 | Open A/P Balances | Legacy | [Count] | ☐ | ☐ |
| 3.2.3 | Active Employees | Legacy | [Count] | ☐ | ☐ |
| 3.2.4 | Open POs | Legacy | [Count] | ☐ | ☐ |

### 3.3 Validation Queries
```sql
-- Partner count validation
SELECT COUNT(*) FROM res_partner WHERE active = true;

-- Open invoices balance
SELECT SUM(amount_residual) FROM account_move
WHERE state = 'posted' AND amount_residual > 0;

-- Employee count
SELECT COUNT(*) FROM hr_employee WHERE active = true;
```

---

## 4. ROLLBACK PROCEDURES

### 4.1 Rollback Decision Matrix
| Scenario | Severity | Decision | Owner |
|:---------|:---------|:---------|:------|
| SRI connection fails | High | Wait 2hr, then rollback | PM + IT Dir |
| Data migration errors >5% | High | Rollback | PM + CFO |
| First invoice fails auth | Medium | Debug 1hr, then rollback | IT |
| Performance unacceptable | Medium | Rollback | IT Dir |
| Minor bugs | Low | Continue, hotfix | IT |

### 4.2 Rollback Procedure (< Point of No Return)
| Step | Action | Owner | Duration |
|:-----|:-------|:------|:---------|
| 1 | Announce rollback decision | PM | 5 min |
| 2 | Stop migration scripts | IT | 5 min |
| 3 | Restore database from backup | DBA | 30 min |
| 4 | Re-enable legacy system | IT | 15 min |
| 5 | Verify legacy functionality | QA | 30 min |
| 6 | Enable user access to legacy | IT | 10 min |
| 7 | Post-mortem meeting | PM | - |

### 4.3 Rollback Procedure (> Point of No Return)
| Step | Action | Owner | Duration |
|:-----|:-------|:------|:---------|
| 1 | Announce rollback decision | PM + CFO | 5 min |
| 2 | Disable Odoo | IT | 5 min |
| 3 | Restore pre-cutover backup | DBA | 30 min |
| 4 | Re-enable legacy system | IT | 15 min |
| 5 | Manual reconciliation of transactions | Acct | 4-8 hr |
| 6 | User communication | PM | 15 min |
| 7 | Reschedule go-live | PM | - |

### 4.4 Rollback Communication Template
```
SUBJECT: [URGENT] ERP Go-Live Rollback - Return to Legacy System

The ERP go-live has been rolled back due to [REASON].

IMMEDIATE ACTIONS:
1. Stop using Odoo immediately
2. Resume work in legacy system
3. Any transactions entered in Odoo will be reconciled manually

TIMELINE:
- Legacy system available at: [TIME]
- New go-live date: TBD

CONTACT: [Support Hotline]
```

---

## 5. POST-CUTOVER VALIDATION

### 5.1 Day 1 Validation
| # | Check | Expected | Actual | Status |
|:--|:------|:---------|:-------|:-------|
| 5.1.1 | Invoice creation | Success | | ☐ |
| 5.1.2 | SRI authorization | Success | | ☐ |
| 5.1.3 | Credit note | Success | | ☐ |
| 5.1.4 | Vendor bill | Success | | ☐ |
| 5.1.5 | Withholding | Success | | ☐ |
| 5.1.6 | Payment | Success | | ☐ |

### 5.2 Week 1 Validation
| # | Check | Expected | Actual | Status |
|:--|:------|:---------|:-------|:-------|
| 5.2.1 | All invoices authorized | 100% | | ☐ |
| 5.2.2 | No 5-day violations | 0 | | ☐ |
| 5.2.3 | Bank reconciliation | Balanced | | ☐ |
| 5.2.4 | User tickets | <20 | | ☐ |

---

## 6. ESCALATION MATRIX

| Issue Level | Response Time | Escalation Path |
|:------------|:--------------|:----------------|
| Critical (System down) | 15 min | IT → IT Dir → CTO |
| High (SRI failures) | 30 min | IT → PM → CFO |
| Medium (Functional) | 2 hr | Support → PM |
| Low (Questions) | 24 hr | Support |

---

**Document Classification**: Cutover & Rollback Plan
**Owner**: Project Manager
**Approval**: CFO, IT Director
**Last Updated**: 2026-01-22
