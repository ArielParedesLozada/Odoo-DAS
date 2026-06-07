# Legacy Codebase Analysis: Odoo-Ecuador (v10) vs 2026 Mandates

## 1. Executive Summary
The analyzed codebase is a **Legacy Odoo 10.0 implementation** of the Ecuadorian SRI localization. While it provides a functional logic flow for Electronic Invoicing (Facturación Electrónica), it is **architecturally incompatible** with Odoo 18.0 and currently violates the "Pure Python" and "No Binary Dependencies" rules of the Vibe Coding Framework due to its reliance on a Java JAR for signing.

**Verdict**: **REWRITE REQUIRED**. We cannot simply migrate this code; we must reimplement the logic using modern Python libraries (`zeep`, `cryptography`, `lxml`) while preserving the business logic for key generation and validation.

## 2. Architectural Audit

### 2.1 Critical Dependencies (Violations)
| Component | Legacy Impl | Vibe/Soma Mandate | Action |
| :--- | :--- | :--- | :--- |
| **XAdES Signing** | `firmaXadesBes.jar` (Java via `subprocess`) | **Native Python** (`lxml` + `cryptography`) | **REPLACE**. Eliminate Java. |
| **SOAP Client** | `suds-jurko` (Unmaintained) | **Zeep** | **REPLACE**. Use `zeep` with async support if needed. |
| **XML Validation** | `lxml` (Correct) | `lxml` | **KEEP**. Reuse XSDs (updated). |
| **HTTP Requests** | `requests` (Sync) | `requests` / `httpx` | **UPDATE**. Ensure timeouts are robust. |

### 2.2 Data Model Patterns
The legacy code uses an `AbstractModel` pattern (`account.edocument`) to share logic between `account.invoice` and `account.retention`.
- **Legacy**: `class Edocument(models.AbstractModel)`
- **Odoo 18**: Should be a `Mixin` or integrated directly into `account.move` (for invoices) and a separate model for specialized SRI docs if they don't fit `account.move`.
- **Field Mappings**: The legacy mapping `_FIELDS = {'account.invoice': 'invoice_number'}` is fragile. We should use consistent field names across models or a unified Document interface.

### 2.3 Hardcoded Configuration
The file `l10n_ec_einvoice/models/utils.py` contains **Hardcoded Tables** (Table 17, 18, 20, 21) from the *old* technical data sheet.
- **Risk**: These tables do not include the **15% IVA** (Code 4/5 depending on table version) or **RIMPE** codes.
- **Remediation**: Move these to a `Configuration` model or update them strictly against the **SRI Ficha Técnica Offline V2.21 (2025)**.

## 3. Regulatory Gap Analysis (2016 vs 2026)

| Feature | Legacy Code (2016) | 2026 Regulation | Gap |
| :--- | :--- | :--- | :--- |
| **IVA Rate** | 12%, 14% (Earthquake) | **15%** (Standard) | **CRITICAL**. Missing 15% rate logic. |
| **Signing** | XAdES-BES (Java) | XAdES-BES (SHA1/SHA256) | **HIGH**. Must implement in Python. |
| **Transmission** | "24h limit" (Offline) | **Real-Time** (Online mandatory for most) | **MEDIUM**. Logic needs to support immediate sending. |
| **Withholdings** | Old Percentages | **New 2024/2025 Percentages** | **HIGH**. Update `l10n_ec_withholding` data. |
| **Consumidor Final** | Basic Logic | **$50 Lock** (Invoice >$50 requires data) | **HIGH**. Missing validation logic. |
| **RIMPE** | Not Existent | **Mandatory** | **CRITICAL**. Missing RIMPE tax codes/regimes. |

## 4. Reusable Logic (The "Bases")
Despite the age, the following logic is mathematically sound and should be ported:

1.  **Access Key Generation (Clave de Acceso)**:
    *   **Algorithm**: Modulo 11.
    *   **Source**: `l10n_ec_einvoice/xades/xades.py` (`CheckDigit.compute_mod11`).
    *   **Status**: **Reusable**. This math hasn't changed.

2.  **XML Structure (Base)**:
    *   The `templates/` folder structure is a good starting point, but the XSDs have changed versions.
    *   **Action**: Use the *latest* XSDs from SRI, but reference the legacy templates for Odoo field mapping.

3.  **State Machine**:
    *   `draft` -> `generated` -> `signed` -> `sent` -> `authorized`.
    *   This flow is standard and should be preserved.

## 5. Technical Implementation Plan

### 5.1 New Module Structure (`l10n_ec_sri_2026`)
Do not clutter the workspace with 14 small modules. Consolidate into a cohesive `l10n_ec_sri` suite.

```text
l10n_ec_sri/
├── models/
│   ├── account_move.py      # Inherits for E-Inv
│   ├── sri_credentials.py   # Signature & Env Config
│   ├── sri_tax_codes.py     # RIMPE, IVA 15%
│   └── res_partner.py       # RUC/Cedula Validation
├── signing/
│   ├── signer.py            # Python Native XAdES
│   └── templates/           # Jinja2/QWeb for XML
├── service/
│   ├── sri_client.py        # Zeep SOAP Client
│   └── error_handling.py    # SRI Error parsers
└── wizards/
    └── ats_report.py        # Anexo Transaccional
```

### 5.2 Python Signing Implementation
Instead of `subprocess.call('java -jar ...')`:
```python
from lxml import etree
from signxml import XMLSigner, methods

def sign_xml(xml_root, p12_file, password):
    # Load P12 and Cert
    # Canonicalize
    # Sign using RSA-SHA1 (SRI Requirement)
    # Inject Signature into <firma> tag
    pass
```

### 5.3 Roadmap
1.  **Environment Setup**: Create `l10n_ec_sri` module structure.
2.  **Port Math**: Copy Mod11 logic from Legacy.
3.  **Implement Signer**: Build Python XAdES-BES signer.
4.  **Tax Update**: Create CSVs for 15% IVA and Withholdings.
5.  **Service Layer**: Implement Zeep client for `cel.sri.gob.ec`.
6.  **Integration**: Hook into `account.move.action_post()`.
