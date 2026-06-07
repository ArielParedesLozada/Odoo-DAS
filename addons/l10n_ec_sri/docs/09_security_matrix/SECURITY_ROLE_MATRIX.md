# SECURITY ROLE MATRIX
## Role × Permission × Object Authorization

**Document ID**: SEC-001
**Version**: 1.1 (IMPLEMENTED)
**Classification**: Big 4 Professional Grade
**Implementation Status**: ✅ GROUPS DEFINED IN `l10n_ec_base/security/l10n_ec_groups.xml`

---

## 1. ROLE DEFINITIONS

### 1.1 Ecuador Localization Roles
| Role ID | Role Name | Description | Odoo Group |
|:--------|:----------|:------------|:-----------|
| R-01 | Accountant | Full accounting access | `account.group_account_manager` |
| R-02 | Invoice Clerk | Create/post invoices only | `account.group_account_invoice` |
| R-03 | AP Clerk | Vendor bills, no payments | Custom |
| R-04 | AR Clerk | Customer invoices only | Custom |
| R-05 | Payroll Specialist | Payroll processing | `hr_payroll.group_hr_payroll_user` |
| R-06 | HR Manager | Full HR access | `hr.group_hr_manager` |
| R-07 | Warehouse User | Stock operations | `stock.group_stock_user` |
| R-08 | Warehouse Manager | Full stock access | `stock.group_stock_manager` |
| R-09 | IT Admin | System configuration | `base.group_system` |

---

## 2. PERMISSION MATRIX: ELECTRONIC INVOICING

### 2.1 account.move (Invoices)
| Permission | R-01 Accountant | R-02 Inv Clerk | R-03 AP | R-04 AR | R-09 IT |
|:-----------|:----------------|:---------------|:--------|:--------|:--------|
| **Create** Customer Invoice | ✅ | ✅ | ❌ | ✅ | ✅ |
| **Create** Vendor Bill | ✅ | ❌ | ✅ | ❌ | ✅ |
| **Post** Invoice | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Cancel** Invoice | ✅ | ❌ | ❌ | ❌ | ✅ |
| **Send to SRI** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **View** Authorization | ✅ | ✅ | ✅ | ✅ | ✅ |
| **View** XML Attachment | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Retry SRI** Transmission | ✅ | ❌ | ❌ | ❌ | ✅ |
| **Delete** Draft Invoice | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Delete** Posted Invoice | ❌ | ❌ | ❌ | ❌ | ❌ |

### 2.2 account.retention (Withholdings)
| Permission | R-01 Accountant | R-02 Inv Clerk | R-03 AP | R-09 IT |
|:-----------|:----------------|:---------------|:--------|:--------|
| **Create** Retention | ✅ | ❌ | ✅ | ✅ |
| **Validate** Retention | ✅ | ❌ | ✅ | ✅ |
| **Cancel** Retention | ✅ | ❌ | ❌ | ✅ |
| **View** Authorization | ✅ | ✅ | ✅ | ✅ |
| **Retry SRI** | ✅ | ❌ | ❌ | ✅ |

---

## 3. PERMISSION MATRIX: HR & PAYROLL

### 3.1 hr.payslip (Payroll)
| Permission | R-05 Payroll | R-06 HR Mgr | R-01 Accountant | R-09 IT |
|:-----------|:-------------|:------------|:----------------|:--------|
| **Create** Payslip | ✅ | ✅ | ❌ | ✅ |
| **Compute** Payslip | ✅ | ✅ | ❌ | ✅ |
| **Confirm** Payslip | ✅ | ✅ | ❌ | ✅ |
| **View** Payslip | ✅ | ✅ | ✅ Read-Only | ✅ |
| **Cancel** Payslip | ❌ | ✅ | ❌ | ✅ |
| **View** Salary Details | ✅ | ✅ | ❌ | ✅ |
| **Export** IESS File | ✅ | ✅ | ❌ | ✅ |

### 3.2 hr.contract (Contracts)
| Permission | R-05 Payroll | R-06 HR Mgr | R-09 IT |
|:-----------|:-------------|:------------|:--------|
| **Create** Contract | ❌ | ✅ | ✅ |
| **Modify** Salary | ❌ | ✅ | ✅ |
| **View** Salary | ✅ | ✅ | ✅ |
| **Terminate** Contract | ❌ | ✅ | ✅ |
| **Archive** Contract | ❌ | ✅ | ✅ |

---

## 4. PERMISSION MATRIX: STOCK OPERATIONS

### 4.1 stock.picking (Transfers)
| Permission | R-07 WH User | R-08 WH Mgr | R-01 Accountant | R-09 IT |
|:-----------|:-------------|:------------|:----------------|:--------|
| **Create** Transfer | ✅ | ✅ | ❌ | ✅ |
| **Validate** Transfer | ✅ | ✅ | ❌ | ✅ |
| **Cancel** Transfer | ❌ | ✅ | ❌ | ✅ |
| **Generate** Guía | ✅ | ✅ | ❌ | ✅ |
| **View** Guía Auth | ✅ | ✅ | ✅ | ✅ |

---

## 5. SENSITIVE DATA ACCESS

### 5.1 Confidential Fields
| Field | Model | Access Restricted To |
|:------|:------|:--------------------|
| `electronic_signature` (P12) | res.company | R-09 IT Admin |
| `password_electronic_signature` | res.company | R-09 IT Admin |
| `wage` (Salary) | hr.contract | R-05, R-06, R-09 |
| `net_receivable` | hr.payslip | R-05, R-06, R-09 |

### 5.2 Odoo Field-Level Security
```xml
<!-- P12 Password restricted to System Admin -->
<field name="password_electronic_signature"
       groups="base.group_system"/>
```

---

## 6. SEGREGATION OF DUTIES

### 6.1 Incompatible Role Combinations
| Combination | Risk | Mitigation |
|:------------|:-----|:-----------|
| AP Clerk + Payment Approver | Fraud | Different users required |
| Invoice Creator + Invoice Approver | Fraud | Workflow enforcement |
| Payroll Processor + Payroll Approver | Fraud | Manager approval required |
| Data Entry + System Admin | Errors | Separate roles |

### 6.2 Workflow Approvals
| Process | Creator | Approver | Final Authorization |
|:--------|:--------|:---------|:--------------------|
| Vendor Bill >$5,000 | AP Clerk | AP Manager | Controller |
| Customer Credit Note | AR Clerk | AR Manager | - |
| Payroll Run | Payroll Spec | HR Manager | CFO |
| New Vendor | Purchasing | AP Manager | - |

---

## 7. AUDIT TRAIL REQUIREMENTS

### 7.1 Logged Activities
| Activity | Log Location | Retention |
|:---------|:-------------|:----------|
| Invoice creation | `mail.message` | 7 years |
| SRI transmission | Custom log table | 7 years |
| Payslip changes | `mail.tracking.value` | 7 years |
| User login | `res.users.log` | 1 year |
| Configuration changes | `ir.logging` | 1 year |

### 7.2 Non-Repudiation
| Action | Evidence | Location |
|:-------|:---------|:---------|
| Invoice authorization | `numero_autorizacion` | account.move |
| Retention authorization | `clave_acceso` | account.retention |
| User action | `write_uid`, `write_date` | All models |

---

## 8. ROLE ASSIGNMENT TEMPLATE

### 8.1 Sample User Assignments
| User | Department | Role(s) |
|:-----|:-----------|:--------|
| Maria Garcia | Accounting | R-01 Accountant |
| Juan Perez | Accounting | R-02 Invoice Clerk |
| Ana Torres | Purchasing | R-03 AP Clerk |
| Carlos Lopez | Sales | R-04 AR Clerk |
| Sofia Mendez | HR | R-05 Payroll, R-06 HR Mgr |
| Pedro Ruiz | Warehouse | R-07 WH User |
| Luis Vega | Warehouse | R-08 WH Manager |
| Admin | IT | R-09 IT Admin |

---

**Document Classification**: Security Matrix
**Owner**: IT Security / Compliance
**Approval**: IT Director, Internal Audit
**Last Updated**: 2026-01-22
