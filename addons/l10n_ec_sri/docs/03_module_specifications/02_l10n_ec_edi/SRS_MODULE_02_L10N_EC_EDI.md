# SOFTWARE REQUIREMENTS SPECIFICATION
## Module: l10n_ec_edi (Ecuador Electronic Data Interchange)

**Document Identifier**: SRS-L10N-EC-EDI-001
**Version**: 1.0
**Date**: 2026-01-22
**Status**: APPROVED
**Standard**: ISO/IEC/IEEE 29148:2018

---

## 1. INTRODUCTION

### 1.1 Purpose
This SRS describes the requirements for the `l10n_ec_edi` module, which implements electronic document generation, digital signing (XAdES-BES), and transmission to the Servicio de Rentas Internas (SRI) of Ecuador.

### 1.2 Scope
The `l10n_ec_edi` module SHALL:
1. Generate XML documents compliant with SRI Ficha Técnica v2.32.
2. Sign XML documents using XAdES-BES (BES Level).
3. Transmit documents to SRI SOAP endpoints.
4. Process SRI authorization responses.
5. Store authorized documents as attachments.

This module SHALL NOT:
- Define taxes or accounts (delegated to `l10n_ec`).
- Generate Withholding documents (delegated to `l10n_ec_withholding`).

### 1.3 Definitions, Acronyms, and Abbreviations
| Term | Definition |
|:---|:---|
| **XAdES-BES** | XML Advanced Electronic Signatures - Basic Electronic Signature |
| **SOAP** | Simple Object Access Protocol |
| **Access Key** | Clave de Acceso - 49-digit unique document identifier |
| **RIDE** | Representación Impresa del Documento Electrónico |
| **P12/PFX** | PKCS#12 Certificate Container |
| **C14N** | Canonicalization (XML Normalization) |

### 1.4 References
- SRI Ficha Técnica de Comprobantes Electrónicos Off-Line v2.32
- ETSI TS 101 903 (XAdES Specification)
- Odoo 18.0 account.edi.format Documentation

---

## 2. OVERALL DESCRIPTION

### 2.1 Product Perspective
This module extends `account.edi.format` to implement the Ecuador SRI EDI format. It integrates with `account.move` to sign and transmit invoices, credit notes, and debit notes.

### 2.2 Product Functions
1. **F-EDI-001**: XML Document Generation
2. **F-EDI-002**: Access Key Computation
3. **F-EDI-003**: XAdES-BES Digital Signing
4. **F-EDI-004**: SRI Transmission (Reception + Authorization)
5. **F-EDI-005**: Document State Management
6. **F-EDI-006**: Error Handling and Retry

### 2.3 User Classes
| User Class | Interaction |
|:---|:---|
| **Accountant** | Views authorization status, downloads XML |
| **System** | Automatic post-invoice signing |

### 2.4 Operating Environment
- Python 3.10+ with `lxml`, `cryptography`, `zeep`
- Odoo 18.0 Enterprise (account module)
- Network access to `cel.sri.gob.ec` / `celcer.sri.gob.ec`

### 2.5 Constraints
- Signing MUST be performed in pure Python (no Java).
- Real-time transmission required as of Jan 2026.
- P12 password MUST NOT be logged.

---

## 3. EXTERNAL INTERFACE REQUIREMENTS

### 3.1 User Interfaces
| Screen | Description |
|:---|:---|
| **Invoice Form** | New "SRI" tab with Access Key, Status, Download |
| **Company Settings** | P12 Upload, Password, Environment |

### 3.2 Software Interfaces
| Interface | Protocol | Endpoint |
|:---|:---|:---|
| **SRI Reception** | SOAP/WSDL | `RecepcionComprobantesOffline` |
| **SRI Authorization** | SOAP/WSDL | `AutorizacionComprobantesOffline` |

### 3.3 Communication Interfaces
| Environment | URL |
|:---|:---|
| **Test** | `https://celcer.sri.gob.ec/comprobantes-electronicos-ws/` |
| **Production** | `https://cel.sri.gob.ec/comprobantes-electronicos-ws/` |

---

## 4. SPECIFIC REQUIREMENTS

### 4.1 Functional Requirements

#### 4.1.1 XML Document Generation (F-EDI-001)
**REQ-F-001.1**: The system SHALL generate XML for document types:
| Type | Root Element | Schema |
|:---|:---|:---|
| Factura (01) | `<factura>` | factura_v2.1.0.xsd |
| Nota Crédito (04) | `<notaCredito>` | notaCredito_v1.1.0.xsd |
| Nota Débito (05) | `<notaDebito>` | notaDebito_v1.1.0.xsd |

**REQ-F-001.2**: XML Structure for Factura:
```xml
<factura id="comprobante" version="2.1.0">
    <infoTributaria>
        <ambiente>2</ambiente>
        <tipoEmision>1</tipoEmision>
        <razonSocial>...</razonSocial>
        <nombreComercial>...</nombreComercial>
        <ruc>...</ruc>
        <claveAcceso>...</claveAcceso>
        <codDoc>01</codDoc>
        <estab>001</estab>
        <ptoEmi>001</ptoEmi>
        <secuencial>000000001</secuencial>
        <dirMatriz>...</dirMatriz>
    </infoTributaria>
    <infoFactura>
        <fechaEmision>22/01/2026</fechaEmision>
        <dirEstablecimiento>...</dirEstablecimiento>
        <obligadoContabilidad>SI</obligadoContabilidad>
        <tipoIdentificacionComprador>04</tipoIdentificacionComprador>
        <razonSocialComprador>...</razonSocialComprador>
        <identificacionComprador>...</identificacionComprador>
        <totalSinImpuestos>100.00</totalSinImpuestos>
        <totalDescuento>0.00</totalDescuento>
        <totalConImpuestos>
            <totalImpuesto>
                <codigo>2</codigo>
                <codigoPorcentaje>4</codigoPorcentaje>
                <baseImponible>100.00</baseImponible>
                <valor>15.00</valor>
            </totalImpuesto>
        </totalConImpuestos>
        <propina>0.00</propina>
        <importeTotal>115.00</importeTotal>
        <moneda>DOLAR</moneda>
        <pagos>
            <pago>
                <formaPago>20</formaPago>
                <total>115.00</total>
            </pago>
        </pagos>
    </infoFactura>
    <detalles>
        <detalle>
            <codigoPrincipal>PROD001</codigoPrincipal>
            <descripcion>Product Description</descripcion>
            <cantidad>1</cantidad>
            <precioUnitario>100.00</precioUnitario>
            <descuento>0.00</descuento>
            <precioTotalSinImpuesto>100.00</precioTotalSinImpuesto>
            <impuestos>
                <impuesto>
                    <codigo>2</codigo>
                    <codigoPorcentaje>4</codigoPorcentaje>
                    <tarifa>15</tarifa>
                    <baseImponible>100.00</baseImponible>
                    <valor>15.00</valor>
                </impuesto>
            </impuestos>
        </detalle>
    </detalles>
    <infoAdicional>
        <campoAdicional nombre="Email">customer@example.com</campoAdicional>
    </infoAdicional>
</factura>
```

#### 4.1.2 Access Key Computation (F-EDI-002)
**REQ-F-002.1**: Access Key Structure (49 digits):
| Position | Length | Content | Source |
|:---|:---|:---|:---|
| 1-8 | 8 | Date (DDMMYYYY) | `move.invoice_date` |
| 9-10 | 2 | Document Type | `move.l10n_latam_document_type_id.code` |
| 11-23 | 13 | RUC | `move.company_id.vat` |
| 24 | 1 | Environment | Company Setting (1=Test, 2=Prod) |
| 25-27 | 3 | Establishment | `001` |
| 28-30 | 3 | Emission Point | `001` |
| 31-39 | 9 | Sequential | Padded Invoice Number |
| 40-47 | 8 | Numeric Code | Random or Sequence |
| 48 | 1 | Emission Type | `1` |
| 49 | 1 | Check Digit | Modulo 11 |

**REQ-F-002.2**: Modulo 11 Algorithm for Check Digit:
```python
def compute_check_digit(data: str) -> int:
    """
    data: 48-character string (positions 1-48)
    return: single digit 0-9
    """
    weights = [2, 3, 4, 5, 6, 7]
    total = 0
    weight_index = 0
    for char in reversed(data):
        total += int(char) * weights[weight_index]
        weight_index = (weight_index + 1) % 6
    remainder = total % 11
    check = 11 - remainder
    if check == 11:
        return 0
    elif check == 10:
        return 1
    return check
```

#### 4.1.3 XAdES-BES Digital Signing (F-EDI-003)
**REQ-F-003.1**: The system SHALL load a P12 certificate from `res.company.l10n_ec_p12_certificate`.

**REQ-F-003.2**: The P12 password SHALL be stored in `res.company.l10n_ec_p12_password` with `groups="base.group_system"`.

**REQ-F-003.3**: Signing Algorithm:
1. Parse P12 to extract Private Key and X509 Certificate.
2. Canonicalize XML using C14N (Exclusive).
3. Compute SHA-1 digest of canonicalized `<comprobante>`.
4. Sign digest using RSA-SHA1.
5. Construct `<ds:Signature>` element with:
   - `<ds:SignedInfo>` (Canonicalized Reference to `#comprobante`)
   - `<ds:SignatureValue>` (Base64 Encoded)
   - `<ds:KeyInfo>` (X509 Certificate Chain)
   - `<ds:Object>` (XAdES Qualifying Properties)

**REQ-F-003.4**: XAdES Qualifying Properties SHALL include:
- `<xades:SignedProperties>` with `<xades:SigningTime>`
- `<xades:SignedSignatureProperties>` with Certificate Digest

#### 4.1.4 SRI Transmission (F-EDI-004)
**REQ-F-004.1**: Reception Call:
```python
client = zeep.Client(wsdl=RECEPTION_WSDL)
response = client.service.validarComprobante(
    xml=base64.b64encode(signed_xml)
)
# response.estado = 'RECIBIDA' or 'DEVUELTA'
```

**REQ-F-004.2**: Authorization Call:
```python
client = zeep.Client(wsdl=AUTHORIZATION_WSDL)
response = client.service.autorizacionComprobante(
    claveAccesoComprobante=access_key
)
# response.autorizaciones.autorizacion[0].estado = 'AUTORIZADO'
```

**REQ-F-004.3**: The system SHALL retry authorization up to 3 times with 5-second intervals if status is 'EN PROCESAMIENTO'.

#### 4.1.5 Document State Management (F-EDI-005)
**REQ-F-005.1**: `account.move` SHALL have field:
| Field | Type | Values |
|:---|:---|:---|
| `l10n_ec_edi_state` | Selection | `draft`, `signed`, `sent`, `authorized`, `rejected` |

**REQ-F-005.2**: State Transitions:
```
draft -> signed (on sign success)
signed -> sent (on reception success)
sent -> authorized (on authorization success)
sent -> rejected (on authorization failure)
rejected -> signed (on retry)
```

#### 4.1.6 Error Handling (F-EDI-006)
**REQ-F-006.1**: The system SHALL store error messages in `l10n_ec_edi_error`.

**REQ-F-006.2**: Common error codes:
| Code | Message | Action |
|:---|:---|:---|
| 35 | DOCUMENTO DUPLICADO | Block retry |
| 43 | CLAVE ACCESO REGISTRADA | Use existing authorization |
| 45 | ERROR EN ESTRUCTURA | Log and notify |

---

## 5. USE CASES

### 5.1 UC-001: Sign and Authorize Invoice
**Actor**: System (Automated)
**Trigger**: Invoice posted (`action_post`)
**Flow**:
1. System generates XML from invoice data.
2. System computes Access Key.
3. System signs XML with P12.
4. System calls `validarComprobante`.
5. If RECIBIDA, system calls `autorizacionComprobante`.
6. System stores authorized XML as attachment.
7. System sets state to 'authorized'.
**Exception**: If rejected, system sets state to 'rejected' and logs error.

### 5.2 UC-002: Retry Failed Document
**Actor**: Accountant
**Trigger**: User clicks "Retry" button
**Flow**:
1. System regenerates XML (if data changed).
2. System signs XML.
3. System transmits to SRI.
**Postcondition**: State updated based on response.

---

## 6. VALIDATION CRITERIA

### 6.1 Acceptance Tests
| Test ID | Description | Expected Result |
|:---|:---|:---|
| **T-EDI-001** | Generate Access Key for test invoice | 49 digits, valid Mod11 |
| **T-EDI-002** | Sign XML with test P12 | Valid XAdES signature |
| **T-EDI-003** | Send to SRI Test environment | State = 'authorized' |
| **T-EDI-004** | Invalid RUC in invoice | SRI Error 45 captured |

---

## 7. APPENDICES

### 7.1 WSDL Endpoints
**Test**:
- Reception: `https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl`
- Authorization: `https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl`

**Production**:
- Reception: `https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl`
- Authorization: `https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl`

---

**Document Control**:
| Version | Date | Author | Changes |
|:---|:---|:---|:---|
| 1.0 | 2026-01-22 | Antigravity | Initial Release |
