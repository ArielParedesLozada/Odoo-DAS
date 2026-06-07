# REGULATORY KNOWLEDGE BASE: SRI ELECTRONIC INVOICING
## Verified from sri.gob.ec - January 2026

**Source**: https://www.sri.gob.ec/facturacion-electronica
**Last Verified**: 2026-01-22

---

## 1. CURRENT FICHA TÉCNICA VERSION

> **Ficha Técnica de Comprobantes Electrónicos Esquema Off-line - Versión 2.32**
> Actualizado a Noviembre 2025

**Download Link**: https://www.sri.gob.ec/o/sri-portlet-biblioteca-alfresco-internet/descargar/29562323-2e76-42f5-abb6-cb7ac542c3c6/FICHA%20TE%cc%81CNICA%20COMPROBANTES%20ELECTRO%cc%81NICOS%20ESQUEMA%20OFFLINE%20Versio%cc%81n%202.32.pdf

---

## 2. XSD SCHEMA VERSIONS (CURRENT)

| Document Type | Schema Version | Last Updated |
|:--------------|:---------------|:-------------|
| **Factura** | v1.0.0 / v1.1.0 / v2.0.0 / v2.1.0 | Feb 2022 |
| **Nota de Crédito** | v1.0.0 / v1.1.0 | Feb 2022 |
| **Nota de Débito** | v1.0.0 | Feb 2022 |
| **Liquidación de Compra** | v1.0.0 / v1.1.0 | Feb 2022 |
| **Guía de Remisión** | v1.0.0 / v1.1.0 | Feb 2022 |
| **Comprobante de Retención** | v1.0.0 / v2.0.0 | Feb 2022 |

---

## 3. ELECTRONIC SIGNATURE PROVIDERS (AUTHORIZED)

| Provider | Website |
|:---------|:--------|
| ANFAC | https://firmaselectronicas.ec/ |
| ARGOSDATA | https://www.argosdata.com.ec |
| Banco Central del Ecuador | https://www.eci.bce.ec |
| Consejo de la Judicatura | https://www.icert.fje.gob.ec/solicitud-de-certificado |
| Datilmedia S.A. | https://datil.com |
| Eclipsoft | https://firmas.eclipsoft.com/ |
| Security Data | https://www.securitydata.net.ec/firma-electronica-en-ecuador/ |
| Uanataca Ecuador | https://store.uanataca.ec |
| Lazzate (Enext) | https://enext.ec/ |
| Firma Segura EC | https://firmaseguraec.com/ |
| Newbest | https://www.newbest.net/#/inicio |

---

## 4. ENVIRONMENTS

### 4.1 Test Environment (Pruebas/Certificación)
- **Purpose**: Testing and debugging electronic document systems
- **Note**: Documents issued in this environment have NO tax validity

### 4.2 Production Environment (Producción)
- **Purpose**: Real tax documents with legal validity
- **Requirement**: All documents authorized in Production are legally binding

---

## 5. AUTHORIZATION PROCESS

**Key Change**: No es necesario solicitar la autorización al SRI para emitir comprobantes electrónicos. El SRI autoriza de oficio a todos los contribuyentes.

**How to verify authorization**:
1. Check contributor mailbox (buzón del contribuyente) for authorization letter
2. Use SRI en línea → Facturación Electrónica → Validación de emisor

---

## 6. CONTRIBUTOR GUIDES (Updated)

| Guide | Last Updated |
|:------|:-------------|
| Guía para factura comercial negociable | June 2024 |
| Guía para anulación de comprobantes electrónicos | **March 2025** |

---

## 7. SYSTEM IMPLEMENTATION NOTES

Based on official SRI documentation, the l10n_ec_sri module should:

1. **Use Ficha Técnica v2.32** as the authoritative reference
2. **Implement XSD validation** using the official schemas
3. **Support both Test and Production environments** with proper switching
4. **Track authorization status** from SRI responses
5. **Store authorized documents** for 7-year retention period

---

**Knowledge Base Entry ID**: KB-SRI-001
**Verification Status**: VERIFIED from official source
**Next Review Date**: 2026-07-01
