# TEST SPECIFICATION: WITHHOLDING (RETENCIÓN)
## Numbered Test Cases with Acceptance Criteria

**Document ID**: TS-RET-002
**Version**: 1.0
**Classification**: Big 4 Professional Grade

---

## TEST CASE MATRIX

### TC-RET-001: Basic IR Withholding Creation
| Attribute | Specification |
|:----------|:--------------|
| **Precondition** | Posted vendor bill exists, within 5 days |
| **Test Data** | Vendor: ABC CIA, Bill: $1,000, Type: Services |
| **Steps** | 1. Open vendor bill<br/>2. Click "Create Withholding"<br/>3. Select IR code 312 (1.75%)<br/>4. Confirm |
| **Expected** | Withholding created with $17.50 IR amount |
| **Acceptance** | Amount = base × rate, document linked |

### TC-RET-002: IVA Withholding 30% (Goods)
| Attribute | Specification |
|:----------|:--------------|
| **Precondition** | Vendor bill with IVA 15%, we are Contribuyente Especial |
| **Test Data** | Bill: $1,000 base + $150 IVA |
| **Steps** | 1. Create withholding<br/>2. Select IVA 30%<br/>3. Post |
| **Expected** | IVA retained = $45.00 (30% of $150) |
| **Acceptance** | IVA amount correct, code = 1 in XML |

### TC-RET-003: IVA Withholding 70% (Services)
| Attribute | Specification |
|:----------|:--------------|
| **Precondition** | Service bill, we are CE |
| **Test Data** | Bill: $500 base + $75 IVA |
| **Steps** | 1. Create withholding<br/>2. Select IVA 70% |
| **Expected** | IVA retained = $52.50 (70% of $75) |
| **Acceptance** | Amount correct, code = 2 in XML |

### TC-RET-004: IVA Withholding 100% (Professional)
| Attribute | Specification |
|:----------|:--------------|
| **Precondition** | Professional services bill |
| **Test Data** | Abogado invoice: $800 + $120 IVA |
| **Steps** | 1. Create withholding<br/>2. Select IR 303 (10%) + IVA 100% |
| **Expected** | IR = $80, IVA = $120 |
| **Acceptance** | Both taxes in same retention |

### TC-RET-005: 5-Day Rule - Within Limit
| Attribute | Specification |
|:----------|:--------------|
| **Precondition** | Vendor bill dated today |
| **Test Data** | Bill date: Jan 20, Retention date: Jan 22 |
| **Steps** | 1. Create withholding 2 days after |
| **Expected** | ✅ Created successfully |
| **Acceptance** | No error, retention posted |

### TC-RET-006: 5-Day Rule - Violation
| Attribute | Specification |
|:----------|:--------------|
| **Precondition** | Vendor bill from 10 days ago |
| **Test Data** | Bill date: Jan 12, Attempt: Jan 22 |
| **Steps** | 1. Try to create withholding |
| **Expected** | ❌ Error CODE_701 |
| **Acceptance** | System blocks with message about 5-day rule |

### TC-RET-007: Multiple IR Codes in One Retention
| Attribute | Specification |
|:----------|:--------------|
| **Precondition** | Bill with mixed services |
| **Test Data** | Transport $200, Professional $500 |
| **Steps** | 1. Add line IR 309 (1%)<br/>2. Add line IR 303 (10%) |
| **Expected** | IR total = $2 + $50 = $52 |
| **Acceptance** | Multiple impuesto elements in XML |

### TC-RET-008: Withholding XAdES Signing
| Attribute | Specification |
|:----------|:--------------|
| **Precondition** | Draft retention ready |
| **Test Data** | Valid P12 certificate |
| **Steps** | 1. Post retention<br/>2. Check signed XML |
| **Expected** | XAdES-BES signature present |
| **Acceptance** | ds:Signature element in XML, valid hash |

### TC-RET-009: SRI Authorization - Success
| Attribute | Specification |
|:----------|:--------------|
| **Precondition** | Signed retention ready |
| **Test Data** | Production environment |
| **Steps** | 1. Post and send to SRI |
| **Expected** | Status = AUTORIZADO |
| **Acceptance** | 37-digit authorization number returned |

### TC-RET-010: SRI Authorization - Retry on Timeout
| Attribute | Specification |
|:----------|:--------------|
| **Precondition** | SRI temporarily unavailable |
| **Test Data** | Simulate 30-second timeout |
| **Steps** | 1. Send retention<br/>2. Wait for retry |
| **Expected** | Automatic retry after 5 min |
| **Acceptance** | Background job attempts 3 retries |

### TC-RET-011: Access Key Uniqueness
| Attribute | Specification |
|:----------|:--------------|
| **Precondition** | Two retentions same day |
| **Test Data** | Sequential retentions |
| **Steps** | 1. Create retention 1<br/>2. Create retention 2 |
| **Expected** | Different clave_acceso for each |
| **Acceptance** | Unique 49-digit keys |

### TC-RET-012: AI Agent - Create Withholding
| Attribute | Specification |
|:----------|:--------------|
| **Precondition** | AI agent active, vendor bill exists |
| **Test Data** | "Genera retención para factura de PROVEEDOR X" |
| **Steps** | 1. Issue voice command<br/>2. AI creates withholding<br/>3. User approves |
| **Expected** | Draft retention for approval |
| **Acceptance** | Correct rates applied automatically |

---

## EXECUTION MATRIX

| Test ID | P0 Smoke | Regression | UAT | Performance |
|:--------|:---------|:-----------|:----|:------------|
| TC-RET-001 | ✅ | ✅ | ✅ | |
| TC-RET-002 | ✅ | ✅ | ✅ | |
| TC-RET-003 | | ✅ | ✅ | |
| TC-RET-004 | | ✅ | ✅ | |
| TC-RET-005 | ✅ | ✅ | ✅ | |
| TC-RET-006 | ✅ | ✅ | ✅ | |
| TC-RET-007 | | ✅ | | |
| TC-RET-008 | ✅ | ✅ | | |
| TC-RET-009 | ✅ | ✅ | ✅ | ✅ |
| TC-RET-010 | | ✅ | | ✅ |
| TC-RET-011 | | ✅ | | |
| TC-RET-012 | | ✅ | ✅ | |

---

**Document Classification**: Test Specification
**Owner**: QA Team
**KB Reference**: KB_TAX_RATES_WITHHOLDINGS, DM_02_RETENCION
**Last Updated**: 2026-01-22
