# UML DIAGRAMS: PAYROLL CYCLE
## Appendix to PF_03 - Professional UML Suite

**Document ID**: PF-03-UML | **Version**: 1.0 | **Date**: 2026-01-22

---

## 1. SEQUENCE DIAGRAM: Monthly Payroll Processing

```mermaid
sequenceDiagram
    autonumber
    participant HR as HR Manager
    participant Odoo as Odoo HR
    participant IESS as IESS Portal
    participant Bank as Bank System
    participant Emp as Employee

    HR->>Odoo: Create Payroll Batch
    activate Odoo

    loop For Each Employee
        Odoo->>Odoo: Get Contract Details
        Odoo->>Odoo: Calculate Gross (Base + Extras)
        Odoo->>Odoo: Calculate IESS Personal (9.45%)
        Odoo->>Odoo: Calculate IESS Patronal (12.15%)
        Odoo->>Odoo: Check Fondos Reserva Eligibility
        alt Eligible (>13 months)
            Odoo->>Odoo: Calculate FR (8.33%)
        end
        Odoo->>Odoo: Calculate Income Tax
        Odoo->>Odoo: Apply Deductions
        Odoo->>Odoo: Calculate Net Pay
    end

    HR->>Odoo: Confirm Payroll Batch
    Odoo->>Odoo: Generate Journal Entries
    Odoo->>Odoo: Export IESS Planilla

    HR->>IESS: Upload Planilla CSV
    IESS-->>HR: Confirmation

    HR->>Odoo: Generate Bank File
    Odoo->>Bank: Transfer File
    Bank->>Emp: Deposit Salary
    Bank-->>Odoo: Payment Confirmation

    Odoo-->>HR: ✅ Payroll Complete
    deactivate Odoo
```

---

## 2. STATE MACHINE: Payslip Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Draft: Create Payslip

    Draft --> Computed: compute_sheet()
    Draft --> Cancelled: Cancel

    Computed --> Verified: HR Review
    Computed --> Draft: Recalculate

    Verified --> Done: action_payslip_done()
    Verified --> Computed: Corrections Needed

    Done --> Paid: Payment Processed

    Paid --> [*]: Closed

    note right of Computed: All rules executed
    note right of Done: Journal entries created
    note right of Paid: Bank transfer complete
```

---

## 3. ER DIAGRAM: Payroll Data Model

```mermaid
erDiagram
    HR_EMPLOYEE ||--o{ HR_CONTRACT : "contracts"
    HR_EMPLOYEE ||--o{ HR_PAYSLIP : "payslips"
    HR_CONTRACT ||--o{ HR_PAYSLIP : "payslip_contract"
    HR_PAYSLIP ||--o{ HR_PAYSLIP_LINE : "lines"
    HR_PAYSLIP_LINE ||--|| HR_SALARY_RULE : "rule"
    HR_PAYSLIP ||--|| HR_PAYSLIP_RUN : "batch"

    HR_EMPLOYEE {
        int id PK
        string name
        string identification_id "Cedula"
        string l10n_ec_iess_number
        date birthday
        string marital
        int department_id FK
        int address_id FK
        string bank_account_id
    }

    HR_CONTRACT {
        int id PK
        int employee_id FK
        string name
        date date_start
        date date_end
        float wage "Monthly Salary"
        string l10n_ec_contract_type
        string l10n_ec_sector_code
        boolean l10n_ec_fondos_reserva_mensual
        int l10n_ec_months_worked "Computed"
    }

    HR_PAYSLIP {
        int id PK
        int employee_id FK
        int contract_id FK
        int payslip_run_id FK
        string name
        date date_from
        date date_to
        string state "draft/verify/done/cancel"
        float gross "Computed"
        float net "Computed"
        float l10n_ec_iess_personal
        float l10n_ec_iess_patronal
        float l10n_ec_fondos_reserva
        float l10n_ec_income_tax
    }

    HR_PAYSLIP_LINE {
        int id PK
        int slip_id FK
        int salary_rule_id FK
        string name
        string code
        float quantity
        float rate
        float amount
        float total
    }

    HR_SALARY_RULE {
        int id PK
        string name
        string code "BASIC/HE50/IESS_PER/etc"
        string category_id
        int sequence
        string amount_select "code/percentage/fix"
        text amount_python_compute
    }

    HR_PAYSLIP_RUN {
        int id PK
        string name "January 2026"
        date date_start
        date date_end
        string state "draft/close"
    }
```

---

## 4. ACTIVITY DIAGRAM: IESS Contribution Calculation

```mermaid
flowchart TB
    A([Start]) --> B[Get Employee Contract]
    B --> C[Get Gross Income]
    C --> D{Gross > Ceiling?}

    D -->|Yes| E[Use Ceiling: 25 x SBU]
    D -->|No| F[Use Actual Gross]

    E --> G[Calculate IESS Personal]
    F --> G

    G --> H[Base × 9.45%]
    H --> I[Calculate IESS Patronal]
    I --> J[Base × 12.15%]

    J --> K{Months Worked >= 13?}
    K -->|No| L[No Fondos Reserva]
    K -->|Yes| M{Mensualizado?}

    M -->|Yes| N[Pay to Employee: Base × 8.33%]
    M -->|No| O[Deposit to IESS Account]

    N --> P[Add to Payslip]
    O --> P
    L --> P

    P --> Q[Create IESS Planilla Record]
    Q --> R([End])
```

---

## 5. TIMING DIAGRAM: Annual Benefits Calendar

```mermaid
gantt
    title Ecuador Payroll Annual Calendar 2026
    dateFormat YYYY-MM-DD

    section Décimo Tercero
    Accrual Period      :d13a, 2025-12-01, 2026-11-30
    Payment Deadline    :milestone, d13p, 2026-12-24, 0d

    section Décimo Cuarto (Sierra)
    Accrual Period      :d14sa, 2025-08-01, 2026-07-31
    Payment Deadline    :milestone, d14sp, 2026-04-15, 0d

    section Décimo Cuarto (Costa)
    Accrual Period      :d14ca, 2025-03-01, 2026-02-28
    Payment Deadline    :milestone, d14cp, 2026-08-15, 0d

    section Utilidades
    Fiscal Year         :util, 2026-01-01, 2026-12-31
    Payment Deadline    :milestone, utilp, 2026-04-15, 0d

    section IESS Monthly
    Jan Planilla        :iess1, 2026-01-01, 2026-01-15
    Feb Planilla        :iess2, 2026-02-01, 2026-02-15
    Mar Planilla        :iess3, 2026-03-01, 2026-03-15
```

---

## 6. CLASS DIAGRAM: Salary Rule Structure

```mermaid
classDiagram
    class SalaryRule {
        +String name
        +String code
        +String category_id
        +int sequence
        +compute_rule()
    }

    class EarningsRule {
        +compute_rule()
    }

    class DeductionRule {
        +compute_rule()
    }

    class EmployerContributionRule {
        +compute_rule()
    }

    SalaryRule <|-- EarningsRule
    SalaryRule <|-- DeductionRule
    SalaryRule <|-- EmployerContributionRule

    class BasicSalary {
        +code = "BASIC"
        +compute_rule()
    }

    class OvertimeRule {
        +code = "HE50" / "HE100"
        +compute_rule()
    }

    class IESSPersonalRule {
        +code = "IESS_PER"
        +rate = 9.45%
        +compute_rule()
    }

    class IESSPatronalRule {
        +code = "IESS_PAT"
        +rate = 12.15%
        +compute_rule()
    }

    class FondosReservaRule {
        +code = "FR"
        +rate = 8.33%
        +check_eligibility()
        +compute_rule()
    }

    EarningsRule <|-- BasicSalary
    EarningsRule <|-- OvertimeRule
    DeductionRule <|-- IESSPersonalRule
    EmployerContributionRule <|-- IESSPatronalRule
    EmployerContributionRule <|-- FondosReservaRule
```

---

**UML Classification**: ISO 19501 / UML 2.5 Compliant
