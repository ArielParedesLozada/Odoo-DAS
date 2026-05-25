# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.exceptions import ValidationError
import random
import logging
import re

_logger = logging.getLogger(__name__)


class L10nEcSriXml(models.AbstractModel):
    _name = "l10n_ec.sri.xml"
    _description = "SRI XML Generator"

    @api.model
    def _get_environment_code(self, company):
        return "2" if company.l10n_ec_sri_environment == "production" else "1"

    @api.model
    def _only_digits(self, value):
        return re.sub(r"\D", "", str(value or ""))

    @api.model
    def _get_document_series(self, record):
        journal = record.journal_id
        entity = self._only_digits(getattr(journal, "l10n_ec_entity", "")) or "001"
        emission = self._only_digits(getattr(journal, "l10n_ec_emission", "")) or "001"

        if len(entity) != 3 or len(emission) != 3:
            raise ValidationError(
                "SRI: El establecimiento y punto de emisión del diario deben tener 3 dígitos."
            )
        return f"{entity}{emission}"

    @api.model
    def _get_document_sequential(self, record):
        sequential = self._only_digits((record.name or "").split("-")[-1])
        if not sequential:
            raise ValidationError(
                "SRI: No se pudo obtener el secuencial numérico desde el número de factura."
            )
        return sequential[-9:].zfill(9)

    @api.model
    def _validate_base_key(self, base_key):
        if len(base_key) != 48 or not base_key.isdigit():
            raise ValidationError(
                "SRI: La clave de acceso base debe tener 48 dígitos. Valor generado: %s"
                % base_key
            )

    @api.model
    def generate_access_key(self, record):
        """
        Generate 49-digit Access Key.
        Format:
        [0:8]   Date (DDMMYYYY)
        [8:10]  Doc Type (01)
        [10:23] RUC (1234567890001)
        [23:24] Environment (1 or 2)
        [24:30] Establisment/Series (001-001) -> 001001
        [30:39] Sequential (000000001)
        [39:47] Random Number (8 digits)
        [47:48] Emission Type (1)
        [48:49] Verifier Digit (Mod 11)
        """
        # 1. Extraction
        date_inv = record.invoice_date.strftime("%d%m%Y")
        doc_type = record.l10n_latam_document_type_id.code  # e.g., '01'
        ruc = record.company_id.vat
        env = self._get_environment_code(record.company_id)
        serie = self._get_document_series(record)
        sequential = self._get_document_sequential(record)

        # Random 8 digits
        code_numeric = f"{random.randint(1, 99999999):08d}"
        emission_type = "1"  # Normal

        # 2. Construction (Pre-Verifier)
        base_key = f"{date_inv}{doc_type}{ruc}{env}{serie}{sequential}{code_numeric}{emission_type}"
        self._validate_base_key(base_key)

        # 3. Check Digit (Modulo 11)
        verifier = self._get_modulo_11(base_key)

        access_key = f"{base_key}{verifier}"

        if len(access_key) != 49:
            raise ValidationError(
                f"Generated Access Key length is {len(access_key)}, expected 49."
            )

        return access_key

    def _get_modulo_11(self, key):
        """
        Standard SRI Modulo 11 Algorithm
        """
        key = key[::-1]
        total = 0
        factor = 2

        for char in key:
            total += int(char) * factor
            factor += 1
            if factor > 7:
                factor = 2

        remainder = total % 11
        check_digit = 11 - remainder

        if check_digit == 11:
            check_digit = 0
        elif check_digit == 10:
            check_digit = 1

        return str(check_digit)

    @api.model
    def render_xml(self, record):
        """
        Render the XML using QWeb template.
        """
        values = self.env["account.edi.format"]._get_l10n_ec_edi_values(record)
        values["access_key"] = record.l10n_ec_sri_access_key
        values["environment"] = self._get_environment_code(record.company_id)
        return self.env["ir.qweb"]._render("l10n_ec_edi.l10n_ec_edi_factura", values)
