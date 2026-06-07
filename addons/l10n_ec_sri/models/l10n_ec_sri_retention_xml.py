# -*- coding: utf-8 -*-
from odoo import models
import logging

_logger = logging.getLogger(__name__)


class L10nEcSriRetentionXml(models.AbstractModel):
    _name = "l10n_ec.sri.retention.xml"
    _description = "SRI Retention XML Generator"

    def render_xml(self, retention):
        """
        Render the XML for Comprobante de Retencion.
        Uses the shared 49-digit access key generator from the main XML engine.
        """
        # 1. Reuse Access Key Config
        # We need to adapt the 'record' expected by generate_access_key
        # The generator expects: invoice_date, l10n_latam_document_type_id, journal_id
        # Retention itself acts as the document.

        # NOTE: Retention needs its own Access Key logic or we adapt the helper.
        # For strict Odoo native pattern, we often duplicate or abstract the helper.
        # Here we will call the helper but ensure the record has the fields.

        # We must generate the key HERE because the helper might depend on fields 'retention' doesn't map 1:1 with 'move'.
        # Use the shared modulo 11 helper from l10n_ec.sri.xml.
        # Retention implements its own key generation for document type 07.

        # We'll assume the l10n_ec.sri.xml model is generic enough or we extend it.
        # Let's inspect l10n_ec_sri_xml.py again? I recall it used 'record.invoice_date' etc.
        # Retention has 'date_issue'. We might need a bridge.

        pkey = self._generate_retention_access_key(retention)
        retention.l10n_ec_sri_access_key = pkey

        values = {
            "record": retention,
            "access_key": pkey,
            "company": retention.company_id,
            "partner": retention.partner_id,
            "formatted_date": retention.date_issue.strftime("%d/%m/%Y"),
            # Period: MM/YYYY of the fiscal period
            "periodo_fiscal": retention.date_issue.strftime("%m/%Y"),
        }

        return self.env["ir.qweb"]._render("l10n_ec_sri.xml_retention", values)

    def _generate_retention_access_key(self, record):
        """
        Specific Access Key Gen for Retention (Doc Type 07).
        """
        # 1. Extraction
        date_inv = record.date_issue.strftime("%d%m%Y")
        doc_type = "07"  # SRM Code for Comprobante de Retención
        ruc = record.company_id.vat
        xml_helper = self.env["l10n_ec.sri.xml"]
        env = xml_helper._get_environment_code(record.company_id)

        # Retention Sequence is usually 001-001-00000001
        try:
            # We assume name format '001-001-000000001'
            parts = record.name.split("-")
            serie = f"{parts[0]}{parts[1]}"
            sequential = parts[2]
        except:
            # Fallback if sequence is simple integer
            serie = "001001"
            sequential = (
                f"{int(record.name):09d}" if record.name.isdigit() else "000000001"
            )

        # Random 8 digits
        import random

        code_numeric = f"{random.randint(1, 99999999):08d}"
        emission_type = "1"

        # 2. Construction
        base_key = f"{date_inv}{doc_type}{ruc}{env}{serie}{sequential}{code_numeric}{emission_type}"
        xml_helper._validate_base_key(base_key)

        # 3. Check Digit (Reuse from main xml engine)
        verifier = xml_helper._get_modulo_11(base_key)

        return f"{base_key}{verifier}"
