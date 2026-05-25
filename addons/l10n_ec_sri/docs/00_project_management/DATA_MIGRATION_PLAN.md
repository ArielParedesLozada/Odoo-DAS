# DATA MIGRATION PLAN
## Ecuador Odoo 18.0 Localization

**Document ID**: SOMA-DMP-001
**Version**: 1.0
**Date**: 2026-01-22

---

## 1. MIGRATION SCOPE

### 1.1 Data Sources
| Source System | Data Type | Volume (Est.) |
|:---|:---|:---|
| Legacy Odoo | Chart of Accounts | 500 records |
| Legacy Odoo | Partners (Customers/Vendors) | 5,000 records |
| Legacy Odoo | Products | 2,000 records |
| Legacy Odoo | Open Invoices | 500 records |
| Legacy Odoo | Historical Invoices | 50,000 records |
| Excel | Payroll History | 1,000 records |
| Excel | Employee Data | 100 records |

### 1.2 Data NOT Migrated
- Closed fiscal years (archived)
- Cancelled documents
- Test/dummy data

---

## 2. MIGRATION PHASES

### Phase 1: Master Data (Week 1)
| Data Type | Source | Target | Method |
|:---|:---|:---|:---|
| Chart of Accounts | Legacy | l10n_ec_base | CSV Import |
| Partners | Legacy | res.partner | CSV Import |
| Products | Legacy | product.template | CSV Import |
| Employees | Excel | hr.employee | CSV Import |

### Phase 2: Open Transactions (Week 2)
| Data Type | Source | Target | Method |
|:---|:---|:---|:---|
| Open AR Invoices | Legacy | account.move | Script |
| Open AP Bills | Legacy | account.move | Script |
| Open POs | Legacy | purchase.order | Script |
| Open SOs | Legacy | sale.order | Script |

### Phase 3: Historical Data (Week 3)
| Data Type | Approach |
|:---|:---|
| Historical Invoices | Opening balance journal entry |
| Historical Payroll | Summary journal entries |

---

## 3. FIELD MAPPING

### 3.1 Partner Mapping
| Source Field | Target Field | Transformation |
|:---|:---|:---|
| name | name | Direct |
| vat | vat | Direct |
| - | l10n_ec_identifier_type | Derive from VAT length |
| phone | phone | Direct |
| email | email | Direct |
| street | street | Direct |
| city | city | Direct |

### 3.2 Account Mapping
| Source Account | Target Account | Notes |
|:---|:---|:---|
| 1.1.1.01 | 1010101 | Cash - Map to NEC |
| 1.1.1.02 | 1010102 | Banks - Map to NEC |
| ... | ... | ... |

---

## 4. DATA CLEANSING RULES

### 4.1 Duplicate Detection
- Partners: Match by VAT number
- Products: Match by internal reference

### 4.2 Normalization
- Vendor names: Standardize format
- Product names: Remove special characters
- Addresses: Proper capitalization

### 4.3 Validation
- VAT: Validate Mod10/11 before import
- Emails: Validate format
- Phones: Normalize to +593 format

---

## 5. MIGRATION SCHEDULE

| Activity | Start | End | Owner |
|:---|:---|:---|:---|
| Data Extraction | Week 1 Day 1 | Week 1 Day 2 | IT |
| Data Cleansing | Week 1 Day 2 | Week 1 Day 4 | IT + Functional |
| Test Migration 1 | Week 1 Day 5 | Week 1 Day 5 | IT |
| Validation | Week 2 Day 1 | Week 2 Day 2 | Business |
| Test Migration 2 | Week 2 Day 3 | Week 2 Day 3 | IT |
| Production Migration | Go-Live Day | Go-Live Day | IT |

---

## 6. ROLLBACK PLAN

If migration fails:
1. Restore database from pre-migration backup
2. Identify and fix data issues
3. Re-run migration

---

## 7. SIGN-OFF

| Role | Name | Signature | Date |
|:---|:---|:---|:---|
| IT Lead | _________ | _________ | _____ |
| Business Lead | _________ | _________ | _____ |
