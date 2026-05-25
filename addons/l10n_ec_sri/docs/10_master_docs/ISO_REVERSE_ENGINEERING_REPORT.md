# ISO-COMPLIANT REVERSE ENGINEERING DOCUMENT
## Legacy Odoo-Ecuador (v10.0) -> Target Odoo 18.0 (SomaTech)

**Document ID**: SOMA-REV-ENG-001
**Date**: 2026-01-22
**Status**: APPROVED
**Scope**: Complete reverse engineering of logic, algorithms, and data structures from the legacy `odoo-ecuador` repository.

---

## 1. SCOPE AND PURPOSE
This document formally records the internal logic, algorithms, and architectural patterns of the legacy `odoo-ecuador/odoo-ecuador` (Version 10.0) repository. It serves as the authoritative source of truth for "Business Logic Porting" to the new Odoo 18.0 implementation.

**Objective**: Extract *verified* business logic while discarding obsolete technical implementations (Java/Suds).

## 2. LEGACY SYSTEM ARCHITECTURE
The legacy system operates on a **3-Layer Logic Model**:

1.  **Abstract Base (The "Soul")**: `account.edocument`
    *   Serves as a Mixin for `account.invoice` and `account.retention`.
    *   Holds the core SRI fields: `clave_acceso`, `numero_autorizacion`, `ambiente`.
    *   **Critical Fault**: Uses obsolete `AbstractModel` pattern instead of modern Mixins.

2.  **Business Implementations (The "Body")**:
    *   `l10n_ec_einvoice`: Factura Electronica logic.
    *   `l10n_ec_withholding`: Retenciones (Withholding) logic.
    *   `l10n_ec_authorisation`: SRI Authorization management.

3.  **External Services (The "Limbs" - DEPRECATED)**:
    *   `xades.py`: Java wrapper (`firmaXadesBes.jar`).
    *   `sri.py`: SOAP wrapper using `suds-jurko`.

---

## 3. DETAILED LOGIC SPECIFICATION

### 3.1 Algorithm: Modulo 11 Check Digit (Verified)
**Source**: `l10n_ec_einvoice/xades/xades.py:CheckDigit`
**Usage**: Generating the final digit of the Access Key (Clave de Acceso).

**Logic (Python Port)**:
```python
def compute_mod11_check_digit(numeric_string: str) -> int:
    """
    Reverse Engineered from Legacy xades.py
    Validation: Verified standard Mod11 factor 2-7.
    """
    total = 0
    factor = 2

    # Iterate from right to left
    for digit in reversed(numeric_string):
        total += int(digit) * factor
        factor += 1
        if factor > 7:
            factor = 2

    remainder = total % 11
    check_digit = 11 - remainder

    if check_digit == 11:
        return 0
    if check_digit == 10:
        return 1
    return check_digit
```

### 3.2 Algorithm: Access Key Generation (Clave de Acceso)
**Source**: `l10n_ec_einvoice/models/edocument.py:get_access_key`
**Format**: 49 numeric characters.

**Structure**:
| Position | Field | Source | Note |
| :--- | :--- | :--- | :--- |
| 0-7 | Date | `DDMMYYYY` | Invoice Date |
| 8-9 | Doc Type | `01`=Inv, `07`=Ret | From Mapping |
| 10-22 | RUC | Company RUC | 13 digits |
| 23 | Environment | `1`=Test, `2`=Prod | Config |
| 24-26 | Establishment | `001` | From Authorisation |
| 27-29 | Emission Point | `001` | From Authorisation |
| 30-38 | Sequential | `000001234` | 9 digits padded |
| 39-46 | Random Code | 8 digits | Legacy used Sequence |
| 47 | Emission Type | `1`=Normal | Always 1 for now |
| 48 | Check Digit | Mod11 | Calculated |

### 3.3 Process: Authorization State Machine
**Source**: `l10n_ec_einvoice/models/edocument.py`

1.  **Draft**: Document created.
2.  **Generated (`get_access_key`)**:
    *   Access key calculated.
    *   XML built (using Templates).
3.  **Signed (`xades.py`)**:
    *   Legacy called `java -jar`.
    *   **New**: Must call `lxml` + `cryptography`.
4.  **Sent (`send_receipt`)**:
    *   SOAP Call: `RecepcionComprobantes`.
    *   Response: `RECIBIDA` or Error.
5.  **Authorized (`request_authorization`)**:
    *   SOAP Call: `AutorizacionComprobantes` (using Access Key).
    *   Response: `AUTORIZADO` + XML with Authorization Date.

### 3.4 Logic: Withholding Restrictions
**Source**: `l10n_ec_withholding/models/withholding.py`

*   **5-Day Rule**: The Withholding date cannot be more than 5 days after the Invoice Date.
    *   *Legacy Code*: `days.days not in range(1, 6)`
*   **15-Digit Rule**: Withholding number MUST be 15 digits.
    *   *Legacy Code*: `len(self.name) == length[self.type]`

---

## 4. DATA DICTIONARY & MAPPING

### 4.1 Document Type Codes (Source: `utils.py`)
| Code | Description | New 2026 Action |
| :--- | :--- | :--- |
| `01` | Factura | Keep |
| `03` | Liquidación Compra | Keep |
| `04` | Nota Crédito | Keep |
| `05` | Nota Débito | Keep |
| `06` | Guía Remisión | Keep |
| `07` | Retención | Keep |
| `18` | Factura (Mapping) | **Verify if obsolete** |

### 4.2 Tax Codes (Missing in Legacy)
Legacy only supports basic VAT/ICE.

**REQUIRED FOR 2026 (SRI Table 17/18)**:
*   **IVA 15%**: Code `4` (check latest ficha).
*   **IVA 5%**: Materials (New).
*   **RIMPE**: New Tax Regime codes must be added.

---

## 5. MIGRATION DIRECTIVES

### 5.1 Architecture Transformation
*   **Legacy**: `account.edocument` (Abstract) + `account.invoice` (Inherit).
*   **Target (Odoo 18)**: `l10n_ec.sri.mixin` + `account.move` (Inherit).
    *   The `edocument` logic should be a Mixin applied to `account.move`.
    *   Withholdings should ideally use `account.payment` or a dedicated `l10n_ec.withholding` model if `account.payment` is too restrictive.

### 5.2 Dependency Elimination
*   **BANNED**: `firmaXadesBes.jar`, `suds-jurko`.
*   **MANDATORY**: `zeep` (SOAP), `cryptography` (Signing), `lxml` (XML).

### 5.3 User Interaction Updates
*   Legacy relied on "Offline" mode (24h send).
*   **Target**: Must default to "Online" (Synchronous sending on Post). If SRI fails, fallback to Background Job (Queue).

This document constitutes the **Bases of Code** for the new implementation.
