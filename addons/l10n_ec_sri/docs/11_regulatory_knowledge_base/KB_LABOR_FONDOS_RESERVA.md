# REGULATORY KNOWLEDGE BASE: FONDOS DE RESERVA
## Verified from IESS and ecuadorlegalonline.com

**Sources**:
- https://www.ecuadorlegalonline.com/laboral/fondos-de-reserva/
- Código del Trabajo Art. 196-200
- Ley para el Pago Mensual del Fondo de Reserva (R.O. 644, July 29, 2009)

**Last Verified**: 2026-01-22

---

## 1. DEFINITION

Fondos de Reserva is a labor benefit for workers and public servants under dependency relationship. After the first year of work (from month 13), employees are entitled to receive a monthly payment of **8.33%** of their IESS-reported salary.

---

## 2. KEY PARAMETERS

| Attribute | Value |
|:----------|:------|
| **Rate** | **8.33%** of monthly salary |
| **Eligibility** | After 13 months of continuous service with same employer |
| **Administrator** | IESS (Instituto Ecuatoriano de Seguridad Social) |
| **Legal Basis** | Código del Trabajo Art. 196-200 |
| **Payment Options** | Mensualizado (monthly) OR Acumulado (annual withdrawal) |

---

## 3. CALCULATION

### 3.1 Formula
```
Fondos de Reserva = Monthly Salary × 8.33%
```

### 3.2 Example
```
Salary: $600/month
Fondos de Reserva = $600 × 0.0833 = $49.98/month
```

---

## 4. PAYMENT OPTIONS

### 4.1 Mensualizado (Monthly)
- Employer deposits 8.33% directly in employee's payroll
- Employee receives in rol de pagos each month
- No accumulation in IESS

### 4.2 Acumulado (Accumulated)
- Employee requests accumulation via IESS portal
- Funds deposited to IESS account
- Can be withdrawn as lump sum

### 4.3 How to Request Accumulation
1. Go to www.iess.gob.ec → Trámites Virtuales/Afiliados
2. Select "Fondos de Reserva"
3. Enter cédula and personal key
4. Select "Solicitud de Acumulación Fondo Reserva"
5. System pre-qualifies request → Click "Registrar"

---

## 5. WITHDRAWAL PROCESS

### 5.1 Online Withdrawal Steps
1. Go to IESS portal → "Fondos de Reserva"
2. Enter cédula and password
3. Select "Consulta Fondos Reserva" → "Cuenta Individual de Fondos de Reserva"
4. Select "Solicitudes Fondo Reserva" → "Solicitud Devolución Fondos Reserva"
5. Enter amount to withdraw → Accept
6. Transfer to registered bank account in ~48 hours

### 5.2 Who Can Withdraw
- Employees who have accumulated funds in IESS
- Must have bank account registered with IESS

---

## 6. SYSTEM IMPLEMENTATION NOTES

For `l10n_ec_hr_payroll` module:

1. **Eligibility Tracking**: Calculate months of service, trigger at month 13
2. **Preference Field**: `fondos_mode = Selection(['iess', 'mensualizado'])`
3. **Salary Rule**: Create rule with 8.33% rate
4. **Payslip Line**: Show as separate line item
5. **IESS Integration**: If accumulated, include in monthly planilla

---

**Knowledge Base Entry ID**: KB-LABOR-002
**Verification Status**: VERIFIED
**Legal Authority**: CT Art. 196-200, R.O. 644 (2009)
**Next Review Date**: 2027-01-01
