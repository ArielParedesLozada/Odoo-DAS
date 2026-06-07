# -*- coding: utf-8 -*-
from odoo import models, _
from odoo.exceptions import UserError
import base64
import datetime
import logging
from lxml import etree
import hashlib

# External Libs (Verified in manifest)
try:
    from cryptography.hazmat.primitives.serialization import pkcs12
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
except ImportError:
    logging.getLogger(__name__).warning("Cryptography or LXML not installed")

_logger = logging.getLogger(__name__)


class SriSigner(models.AbstractModel):
    _name = "l10n_ec.sri.signer"
    _description = "XAdES-BES Signer Service"

    def _decode_p12_content(self, p12_binary):
        if isinstance(p12_binary, str):
            raw_content = p12_binary.encode("utf-8")
        else:
            raw_content = bytes(p12_binary or b"")

        try:
            return base64.b64decode(raw_content.strip(), validate=True)
        except Exception:
            return raw_content

    def sign_xml(self, xml_content_bytes, p12_binary, p12_password):
        """
        Signs the XML with XAdES-BES standard (Enveloped).

        :param xml_content_bytes: The canonical XML to sign (bytes)
        :param p12_binary: .p12 file content (base64 or bytes)
        :param p12_password: Password for the .p12
        :return: Signed XML bytes
        """
        # 1. Load Certificate & Private Key
        p12_binary = self._decode_p12_content(p12_binary)

        try:
            private_key, certificate, additional_certs = (
                pkcs12.load_key_and_certificates(
                    p12_binary, str(p12_password or "").encode("utf-8")
                )
            )
        except Exception as e:
            raise UserError(_("Invalid Certificate Password or File: %s") % str(e))

        # 2. Parse XML
        parser = etree.XMLParser(remove_blank_text=True)
        root = etree.fromstring(xml_content_bytes, parser)

        # 3. Create Signature Structure (XAdES-BES, SRI Anexo 14 style)
        signature_id = "Signature-SRI"
        signed_info_id = "Signature-SignedInfo-SRI"
        signature_value_id = "SignatureValue-SRI"
        key_info_id = "Certificate"
        object_id = "Signature-SRI-Object"
        signed_properties_id = "Signature-SRI-SignedProperties"
        reference_id = "Reference-ID-comprobante"
        ns_dsig = "http://www.w3.org/2000/09/xmldsig#"
        ns_xades = "http://uri.etsi.org/01903/v1.3.2#"

        # 3.1 Digest of the Document (SHA1)
        xml_to_hash = etree.tostring(
            root, method="c14n", exclusive=False, with_comments=False
        )
        document_digest_b64 = self._sha1_b64(xml_to_hash)

        # 3.2 Build KeyInfo and XAdES properties referenced by SignedInfo
        cert_der = certificate.public_bytes(serialization.Encoding.DER)
        cert_b64 = base64.b64encode(
            cert_der
        ).decode()
        key_info = self._build_key_info(certificate, cert_b64, key_info_id)
        object_node = self._build_qualifying_properties(
            certificate,
            cert_der,
            signature_id,
            signed_properties_id,
            reference_id,
            object_id,
        )

        # 3.3 Assemble Signature before canonicalizing referenced nodes.
        signature_node = etree.Element(
            f"{{{ns_dsig}}}Signature",
            Id=signature_id,
            nsmap={"ds": ns_dsig, "etsi": ns_xades},
        )
        signed_info = self._build_signed_info(
            signed_info_id,
            signed_properties_id,
            key_info_id,
            reference_id,
            document_digest_b64,
        )
        signature_node.append(signed_info)

        sig_val_node = etree.Element(f"{{{ns_dsig}}}SignatureValue", Id=signature_value_id)
        signature_node.append(sig_val_node)

        signature_node.append(key_info)
        signature_node.append(object_node)
        root.append(signature_node)

        # 3.4 Fill the digest values that depend on final XML namespace context.
        signed_properties = signature_node.find(
            f".//{{{ns_xades}}}SignedProperties"
        )
        self._set_reference_digest(
            signed_info,
            f"#{signed_properties_id}",
            self._sha1_b64(self._canonicalize(signed_properties)),
        )
        self._set_reference_digest(
            signed_info,
            f"#{key_info_id}",
            self._sha1_b64(self._canonicalize(key_info)),
        )

        # 3.5 Sign SignedInfo (RSA-SHA1) after all references have digests.
        signature = private_key.sign(
            self._canonicalize(signed_info),
            padding.PKCS1v15(),
            hashes.SHA1(),
        )
        sig_val_node.text = base64.b64encode(signature).decode()

        return etree.tostring(
            root, xml_declaration=True, encoding="UTF-8", standalone="yes"
        )

    def _canonicalize(self, node):
        return etree.tostring(
            node, method="c14n", exclusive=False, with_comments=False
        )

    def _sha1_b64(self, value):
        return base64.b64encode(hashlib.sha1(value).digest()).decode()

    def _build_signed_info(
        self,
        signed_info_id,
        signed_properties_id,
        key_info_id,
        reference_id,
        document_digest_b64,
    ):
        ns = "http://www.w3.org/2000/09/xmldsig#"
        signed_info = etree.Element(f"{{{ns}}}SignedInfo", Id=signed_info_id)

        c14n = etree.SubElement(signed_info, f"{{{ns}}}CanonicalizationMethod")
        c14n.set("Algorithm", "http://www.w3.org/TR/2001/REC-xml-c14n-20010315")

        sig_method = etree.SubElement(signed_info, f"{{{ns}}}SignatureMethod")
        sig_method.set("Algorithm", "http://www.w3.org/2000/09/xmldsig#rsa-sha1")

        signed_props_ref = etree.SubElement(
            signed_info,
            f"{{{ns}}}Reference",
            Id="SignedPropertiesID-SRI",
            Type="http://uri.etsi.org/01903#SignedProperties",
            URI=f"#{signed_properties_id}",
        )
        digest_method = etree.SubElement(signed_props_ref, f"{{{ns}}}DigestMethod")
        digest_method.set("Algorithm", "http://www.w3.org/2000/09/xmldsig#sha1")
        etree.SubElement(signed_props_ref, f"{{{ns}}}DigestValue")

        key_info_ref = etree.SubElement(
            signed_info, f"{{{ns}}}Reference", URI=f"#{key_info_id}"
        )
        digest_method = etree.SubElement(key_info_ref, f"{{{ns}}}DigestMethod")
        digest_method.set("Algorithm", "http://www.w3.org/2000/09/xmldsig#sha1")
        etree.SubElement(key_info_ref, f"{{{ns}}}DigestValue")

        reference = etree.SubElement(
            signed_info,
            f"{{{ns}}}Reference",
            Id=reference_id,
            URI="#comprobante",
        )

        transforms = etree.SubElement(reference, f"{{{ns}}}Transforms")
        trans = etree.SubElement(transforms, f"{{{ns}}}Transform")
        trans.set("Algorithm", "http://www.w3.org/2000/09/xmldsig#enveloped-signature")

        digest_method = etree.SubElement(reference, f"{{{ns}}}DigestMethod")
        digest_method.set("Algorithm", "http://www.w3.org/2000/09/xmldsig#sha1")

        digest_val = etree.SubElement(reference, f"{{{ns}}}DigestValue")
        digest_val.text = document_digest_b64

        return signed_info

    def _set_reference_digest(self, signed_info, reference_uri, digest_b64):
        ns = "http://www.w3.org/2000/09/xmldsig#"
        for reference in signed_info.findall(f"{{{ns}}}Reference"):
            if reference.get("URI") == reference_uri:
                reference.find(f"{{{ns}}}DigestValue").text = digest_b64
                return
        raise UserError(_("Signature reference %s was not found.") % reference_uri)

    def _build_key_info(self, certificate, cert_b64, key_info_id):
        ns = "http://www.w3.org/2000/09/xmldsig#"
        key_info = etree.Element(f"{{{ns}}}KeyInfo", Id=key_info_id)
        x509_data = etree.SubElement(key_info, f"{{{ns}}}X509Data")
        x509_cert = etree.SubElement(x509_data, f"{{{ns}}}X509Certificate")
        x509_cert.text = cert_b64

        key_value = etree.SubElement(key_info, f"{{{ns}}}KeyValue")
        rsa_key_value = etree.SubElement(key_value, f"{{{ns}}}RSAKeyValue")
        public_numbers = certificate.public_key().public_numbers()
        modulus = etree.SubElement(rsa_key_value, f"{{{ns}}}Modulus")
        modulus.text = self._int_to_b64(public_numbers.n)
        exponent = etree.SubElement(rsa_key_value, f"{{{ns}}}Exponent")
        exponent.text = self._int_to_b64(public_numbers.e)
        return key_info

    def _int_to_b64(self, value):
        value_bytes = value.to_bytes((value.bit_length() + 7) // 8, "big")
        return base64.b64encode(value_bytes).decode()

    def _build_qualifying_properties(
        self,
        certificate,
        cert_der,
        signature_id,
        signed_properties_id,
        reference_id,
        object_id,
    ):
        ns_xades = "http://uri.etsi.org/01903/v1.3.2#"
        ns_dsig = "http://www.w3.org/2000/09/xmldsig#"

        obj = etree.Element(f"{{{ns_dsig}}}Object", Id=object_id)
        qp = etree.SubElement(
            obj,
            f"{{{ns_xades}}}QualifyingProperties",
            Target=f"#{signature_id}",
        )

        signed_props = etree.SubElement(
            qp, f"{{{ns_xades}}}SignedProperties", Id=signed_properties_id
        )
        signed_sig_props = etree.SubElement(
            signed_props, f"{{{ns_xades}}}SignedSignatureProperties"
        )

        signing_time = etree.SubElement(signed_sig_props, f"{{{ns_xades}}}SigningTime")
        ec_tz = datetime.timezone(datetime.timedelta(hours=-5))
        signing_time.text = (
            datetime.datetime.now(ec_tz).replace(microsecond=0).isoformat()
        )

        signing_certificate = etree.SubElement(
            signed_sig_props, f"{{{ns_xades}}}SigningCertificate"
        )
        cert_node = etree.SubElement(signing_certificate, f"{{{ns_xades}}}Cert")
        cert_digest = etree.SubElement(cert_node, f"{{{ns_xades}}}CertDigest")
        digest_method = etree.SubElement(cert_digest, f"{{{ns_dsig}}}DigestMethod")
        digest_method.set("Algorithm", "http://www.w3.org/2000/09/xmldsig#sha1")
        digest_value = etree.SubElement(cert_digest, f"{{{ns_dsig}}}DigestValue")
        digest_value.text = self._sha1_b64(cert_der)

        issuer_serial = etree.SubElement(cert_node, f"{{{ns_xades}}}IssuerSerial")
        issuer_name = etree.SubElement(issuer_serial, f"{{{ns_dsig}}}X509IssuerName")
        issuer_name.text = certificate.issuer.rfc4514_string()
        serial_number = etree.SubElement(
            issuer_serial, f"{{{ns_dsig}}}X509SerialNumber"
        )
        serial_number.text = str(certificate.serial_number)

        signed_data_props = etree.SubElement(
            signed_props, f"{{{ns_xades}}}SignedDataObjectProperties"
        )
        data_object_format = etree.SubElement(
            signed_data_props,
            f"{{{ns_xades}}}DataObjectFormat",
            ObjectReference=f"#{reference_id}",
        )
        description = etree.SubElement(
            data_object_format, f"{{{ns_xades}}}Description"
        )
        description.text = "contenido comprobante"
        mime_type = etree.SubElement(data_object_format, f"{{{ns_xades}}}MimeType")
        mime_type.text = "text/xml"

        return obj
