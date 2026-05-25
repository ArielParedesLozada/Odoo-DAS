# PROJECT TECHNOLOGY MANDATES
## Ecuador Odoo 18.0 Localization

**Document Identifier**: SOMA-TECH-MANDATES-001
**Version**: 1.0
**Date**: 2026-01-22
**Status**: ENFORCED

---

## MANDATORY TECHNOLOGY STACK

These rules are **NON-NEGOTIABLE** and derive from the global VIBE CODING RULES.

---

### 1. API FRAMEWORK: DJANGO NINJA ONLY

> **RULE**: All API endpoints MUST be implemented with **Django + Django Ninja**.
> **NO FastAPI**, Starlette, or uvicorn.

**For this Odoo project, this means:**

| Component | Technology | Notes |
|:----------|:-----------|:------|
| Odoo Backend | Odoo ORM + Controllers | For native Odoo UI/Web |
| External APIs | Django Ninja | For MCP, integrations, microservices |
| SRI Integration API | Django Ninja | `django_mcp/api/sri.py` |
| Webhook Receivers | Django Ninja | External system callbacks |

**Example Structure:**
```
django_mcp/
├── api/
│   ├── __init__.py
│   ├── sri.py         # SRI webhook/API endpoints
│   ├── iess.py        # IESS integration endpoints
│   └── schemas.py     # Pydantic-style schemas
├── manage.py
└── requirements.txt
```

---

### 2. DATABASE ORM: DJANGO ORM FOR NEW MODELS

> **RULE**: All database models MUST use **Django ORM**.
> **NO SQLAlchemy** for new models.

**For this Odoo project:**

| Model Type | Technology | Location |
|:-----------|:-----------|:---------|
| Odoo Standard Extensions | Odoo ORM | `odoo_custom_addons/l10n_ec_*/models/` |
| Django MCP Models | Django ORM | `django_mcp/models/` |
| Shared Data | Django ORM with Odoo sync | Via API or DB views |

**Pattern for Django Models:**
```python
# django_mcp/models/sri_log.py
from django.db import models
import uuid

class SriTransmissionLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    access_key = models.CharField(max_length=49, unique=True, db_index=True)
    document_type = models.CharField(max_length=2)
    status = models.CharField(max_length=20)
    sri_response = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sri_transmission_log'
```

---

### 3. UI FRAMEWORK: LIT WEB COMPONENTS

> **RULE**: ALL UI components MUST use **Lit Web Components** (Lit 3.x).
> **NO Alpine.js** - DEPRECATED and FORBIDDEN.

**For this Odoo project:**

| UI Layer | Technology | Notes |
|:---------|:-----------|:------|
| Odoo Backend Views | Odoo XML + OWL | Standard Odoo patterns |
| Custom Dashboards | Lit Web Components | Embedded in Odoo |
| External Portals | Lit Web Components | Customer/Supplier portals |
| Mobile Components | Lit Web Components | PWA if needed |

**Lit Component Pattern:**
```javascript
// static/src/components/sri-status.js
import { LitElement, html, css } from 'lit';

export class SriStatusBadge extends LitElement {
  static properties = {
    status: { type: String },
    accessKey: { type: String }
  };

  static styles = css`
    :host { display: inline-block; }
    .badge { padding: 4px 8px; border-radius: 4px; }
    .authorized { background: #22c55e; color: white; }
    .rejected { background: #ef4444; color: white; }
    .pending { background: #f59e0b; color: white; }
  `;

  render() {
    return html`
      <span class="badge ${this.status}">
        ${this.status.toUpperCase()}
      </span>
    `;
  }
}
customElements.define('sri-status-badge', SriStatusBadge);
```

---

### 4. PERFORMANCE-CRITICAL: RUST VIA PyO3

> **RULE**: For performance-critical components, use **Rust with PyO3** bindings.

**Candidates for Rust:**

| Component | Justification | Rust Crate |
|:----------|:--------------|:-----------|
| XAdES-BES Signing | 100x speedup, memory safety | `ec_sri_crypto` |
| Módulo 11 Check Digit | High-volume validation | `ec_sri_crypto` |
| XML Canonicalization | CPU-intensive | `ec_sri_crypto` |
| Batch PDF Generation | Memory-hungry | Future consideration |

---

### 5. MESSAGES & I18N: CENTRALIZED

> **RULE**: NO hardcoded strings. ALL user-facing text MUST use `admin.common.messages`.

**For this Odoo project:**
- Use Odoo's native i18n for Odoo modules
- Use Django's translation framework for Django MCP
- Maintain consistency between both

---

### 6. FORBIDDEN TECHNOLOGIES

| Technology | Reason | Alternative |
|:-----------|:-------|:------------|
| FastAPI | Global mandate | Django Ninja |
| SQLAlchemy | Global mandate | Django ORM |
| Alpine.js | Deprecated | Lit Web Components |
| Java (for signing) | Dependency nightmare | Rust/Python |
| Node.js backend | Not in stack | Django/Rust |

---

## ARCHITECTURE SUMMARY

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND                                 │
│  ┌─────────────────┐  ┌──────────────────────────────────┐  │
│  │   Odoo Web      │  │    Lit Web Components            │  │
│  │   (OWL)         │  │    (Custom Dashboards)           │  │
│  └────────┬────────┘  └─────────────┬────────────────────┘  │
│           │                         │                        │
├───────────┴─────────────────────────┴────────────────────────┤
│                    BACKEND                                   │
│  ┌─────────────────────────┐  ┌────────────────────────────┐ │
│  │     ODOO 18.0           │  │    DJANGO MCP              │ │
│  │  ┌─────────────────┐    │  │  ┌──────────────────────┐  │ │
│  │  │ Odoo ORM        │    │  │  │ Django ORM           │  │ │
│  │  │ (account.move)  │    │  │  │ (SriTransmissionLog) │  │ │
│  │  └─────────────────┘    │  │  └──────────────────────┘  │ │
│  │  ┌─────────────────┐    │  │  ┌──────────────────────┐  │ │
│  │  │ Odoo Controllers│◄───┼──┼─►│ Django Ninja APIs    │  │ │
│  │  └─────────────────┘    │  │  └──────────────────────┘  │ │
│  └─────────────────────────┘  └────────────────────────────┘ │
│                    │                      │                   │
├────────────────────┴──────────────────────┴──────────────────┤
│                    CRYPTO CORE (RUST)                        │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  ec_sri_crypto (PyO3)                                   │ │
│  │  - sign_xml()                                           │ │
│  │  - compute_mod11()                                      │ │
│  │  - canonicalize_xml()                                   │ │
│  └─────────────────────────────────────────────────────────┘ │
│                           │                                   │
├───────────────────────────┴───────────────────────────────────┤
│                    EXTERNAL SERVICES                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │   SRI    │  │   IESS   │  │  SENAE   │  │ Supercias│      │
│  │   SOAP   │  │   API    │  │   API    │  │   Portal │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
└───────────────────────────────────────────────────────────────┘
```

---

## ENFORCEMENT

These rules are checked:
1. **Code Review**: All PRs must comply
2. **CI/CD**: Linting for forbidden imports
3. **Architecture Review**: Quarterly audit

**Violations will be rejected.**

---

**Document Author**: Antigravity (Chief ERP Architect)
**Approved**: 2026-01-22
