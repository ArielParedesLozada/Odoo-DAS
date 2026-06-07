# REGULATORY KNOWLEDGE BASE: MINISTERIO DEL TRABAJO
## Labor Ministry and SUT System

**Source**: https://www.trabajo.gob.ec
**Official Name**: Ministerio del Trabajo
**Last Verified**: 2026-01-22

---

## 1. AGENCY OVERVIEW

| Attribute | Value |
|:----------|:------|
| **Name** | Ministerio del Trabajo |
| **Role** | Labor law enforcement and worker protection |
| **Portal** | https://www.trabajo.gob.ec |
| **SUT Portal** | https://sut.trabajo.gob.ec |

---

## 2. SISTEMA ÚNICO DE TRABAJO (SUT)

### 2.1 Definition
Unified system for managing all labor-related registrations and obligations.

### 2.2 Employer Obligations in SUT
| Action | Deadline | Legal Basis |
|:-------|:---------|:------------|
| **Contract Registration** | 15 days after signing | CT Art. 42 |
| **Acta de Finiquito** | 15 days after termination | CT Art. 185 |
| **Décimo Tercero Registration** | Before Dec 24 or per cronogram | CT Art. 95 |
| **Décimo Cuarto Registration** | Before Mar 15 / Aug 15 | CT Art. 97 |
| **Utilidades Registration** | Before Apr 15 | CT Art. 97 |

### 2.3 Contract Types in SUT
| Type | Code | Description |
|:-----|:-----|:------------|
| Indefinido | 01 | Permanent contract |
| Fijo | 02 | Fixed-term contract |
| Eventual | 03 | Occasional work |
| Por obra | 04 | Project-based |
| Parcial | 05 | Part-time |
| Doméstico | 06 | Domestic worker |

---

## 3. CONTRACT REGISTRATION

### 3.1 Required Information
- Employee personal data (cédula, name, address)
- Contract type
- Start date
- Salary (must be ≥ SBU or sectoral minimum)
- Work schedule
- Job position

### 3.2 Digital Contract Process
1. Create contract in SUT
2. Both parties sign digitally
3. System generates registered contract
4. Available for verification

---

## 4. TERMINATION PROCESS

### 4.1 Acta de Finiquito
Mandatory settlement document signed before labor inspector.

### 4.2 Components
| Item | Calculation |
|:-----|:------------|
| Pending salary | Days worked × daily rate |
| Décimo 13 proporcional | (Earnings ÷ 12) × months |
| Décimo 14 proporcional | (SBU ÷ 360) × days |
| Vacations not taken | (Salary ÷ 24) × unused days |
| Fondos de reserva | If pending |
| Indemnification | If applicable (despido/desahucio) |

### 4.3 Registration Timeline
- **Payment deadline**: 15 days after termination
- **SUT registration**: Per RUC cronogram

---

## 5. LABOR INSPECTIONS

### 5.1 Inspection Authority
The Ministry conducts inspections to verify:
- Contract registration
- Salary compliance (≥ SBU/sectoral)
- Décimos payment
- IESS affiliation
- Working conditions
- Utilidades distribution

### 5.2 Penalties
| Violation | Penalty |
|:----------|:--------|
| Unregistered contract | Fine (multiple of SBU) |
| Late décimo payment | 100% surcharge |
| Missing IESS affiliation | Back payment + fines |
| Labor law violations | Variable fines |

---

## 6. DÉCIMOS REGISTRATION

### 6.1 Décimo Tercero
| Region | Registration Cronogram |
|:-------|:-----------------------|
| All | Per RUC 9th digit, early December |

### 6.2 Décimo Cuarto
| Region | Registration Deadline |
|:-------|:---------------------|
| Costa/Galápagos | Before March 15 |
| Sierra/Amazonía | Before August 15 |

---

## 7. UTILIDADES REGISTRATION

### 7.1 Timeline
| Event | Deadline |
|:------|:---------|
| Utilidades payment | April 15 |
| No profit declaration | April 15 |
| SUT registration | Per RUC cronogram |

### 7.2 Required Data
- Total profit distributed (15%)
- Number of beneficiaries
- Individual amounts paid
- Family loads considered

---

## 8. DENUNCIAS (WORKER COMPLAINTS)

### 8.1 How to File
- Online via SUT portal
- In person at Ministry offices
- Anonymous complaint line

### 8.2 Response Timeline
Ministry must respond within 72 hours for urgent matters.

---

## 9. SYSTEM IMPLEMENTATION NOTES

For `l10n_ec_hr` module:

1. **SUT Integration**: Consider API integration for future
2. **Contract Types**: Match SUT contract codes
3. **Termination Wizard**: Generate Acta de Finiquito data
4. **Décimos Tracking**: Regional logic for deadlines
5. **Report Generation**: Décimos and Utilidades reports for SUT upload
6. **Document Archive**: Store signed contracts

---

## 10. KEY RESOURCES

| Resource | URL |
|:---------|:----|
| **Main Portal** | https://www.trabajo.gob.ec |
| **SUT System** | https://sut.trabajo.gob.ec |
| **Labor Code** | Available on portal |
| **Complaint Portal** | Via SUT |

---

**Knowledge Base Entry ID**: KB-MINTRABAJO-001
**Verification Status**: PARTIALLY VERIFIED (URL structure changed)
**Legal Authority**: Código del Trabajo
**Next Review Date**: 2026-07-01
