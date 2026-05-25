# MARKET & TAX ANALYSIS: ECUADOR SAAS 2026

**Document ID**: SOMA-MKT-EC-2026
**Date**: January 22, 2026
**Scope**: Total Tax Compliance for Odoo SaaS (Multi-Tenant)
**Auditor**: SomaTech Strategic Planning (CPA Persona)

---

## 1. THE TAXPAYER LANDSCAPE (Market Segments)
To serve "Every Single Company" in Ecuador, the Odoo SaaS must handle these distinct profiles dynamically. A "One Size Fits All" approach will fail.

### 1.1 "Negocios Populares" (RIMPE) - The Micro Tier
*   **Profile**: Revenue < $20k/year.
*   **Requirement**: Do NOT charge IVA. Do NOT generate Electronic Invoices (officially optional/notes de venta), but **Odoo SaaS MUST generate them** as "Notas de Venta" XMLs for system consistency.
*   **Tax Code**: `IVA 0%` (special subcode).
*   **Legend**: "Contribuyente Negocio Popular - Régimen RIMPE".

### 1.2 "Emprendedores" (RIMPE) - The SME Tier
*   **Profile**: Revenue $20k - $300k.
*   **Requirement**: Charge IVA (15%). Electronic Invoicing MANDATORY.
*   **Withholding**: They do NOT withhold (usually), but ARE withheld against (1%).
*   **Legend**: "Contribuyente Régimen RIMPE".

### 1.3 "Régimen General" - The Standard Tier
*   **Profile**: Revenue > $300k or Professional Services.
*   **Requirement**: Full Electronic Invoicing.
*   **Withholding**:
    *   **Agent of Retention (Agente de Retención)**: If designated by SRI (Catastro). MUST withhold 1.75%, 2.75%, etc.
    *   **Non-Agent**: Only holds on special cases (Liquidations, Employees).

### 1.4 "Contribuyentes Especiales" (The Whales)
*   **Profile**: Large Corporations (Supermaxi, etc.).
*   **Requirement**: Different Withholding percentages (e.g., withhold IVA 30%, 70%, 100%).
*   **SaaS Impact**: config `l10n_ec_withhold_agent = 'special'`.

### 1.5 Exporters (The Niche)
*   **Requirement**: "Devolución de IVA". Needs perfect tracing of Import vs Export packets.
*   **Tax Code**: ISD (Impuesto Salida Divisas) handling.

---

## 2. THE TOTAL TAX MATRIX (What We Must Code)

### 2.1 Impuesto al Valor Agregado (IVA)
The SaaS must support dynamic rate switching (Time-Based) for future changes.
*   **Current**: 15% (Code 4).
*   **Construction**: 5% (Code 5) - *Specific to Real Estate SaaS tenants*.
*   **Zero**: 0% (Code 0).
*   **Exempt**: Code 6.
*   **No Object**: Code 7.

### 2.2 Impuesto a la Renta (Retenciones en la Fuente)
The SaaS must include the **Master Retention Table (2025-2026)**.
*   **312**: Transferencia de Bienes Muebles (1.75%).
*   **320**: Prestación de Servicios (2.75%).
*   **304**: Honorarios Profesionales (10%).
*   **303**: Honorarios (8%).
*   **310**: Transporte (1%).
*   **343**: Combustibles (0.2%).
*   **332**: Liquidación de Compras (Variables).
*   **502**: Pago al Exterior (25% - Paraísos Fiscales).

### 2.3 Impuesto a los Consumos Especiales (ICE)
Mandatory for: Alcohol, Cigarettes, Plastic Bags, Vehicles.
*   **Formula**: Specific (per unit) OR Ad Valorem (%).
*   **SaaS Logic**: Product Category requires an `ice_code` field.

### 2.4 IRBPNR (Plastic Bottles)
*   **Scope**: Bottlers.
*   **Rate**: Specific amount per bottle.

---

## 3. STRATEGIC RECOMMENDATION

### Architecture for "Total Cover"
We cannot embed these rules in code. We must build a **Data-Driven Tax Engine**.

1.  **The "Sovereign Tax Catalog"**: A global `l10n_ec_tax_catalog` model in the SaaS database that all tenants subscribe to. Updates are pushed centrally.
2.  **The "Taxpayer Configurator"**: A Wizard that runs on Database Creation.
    *   "Are you RIMPE?"
    *   "Are you Special Taxpayer?"
    *   "Do you sell Alcohol?"
    *   -> **Auto-Configures Fiscal Positions**.

This guarantees that **SomaTech SaaS** can sell to *any* company without code changes.
