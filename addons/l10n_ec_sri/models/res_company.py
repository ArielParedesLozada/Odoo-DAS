# -*- coding: utf-8 -*-
from odoo import models, fields


class ResCompany(models.Model):
    """
    Extends res.company with additional SRI fields not in l10n_ec_edi.
    The l10n_ec_sri_environment field is inherited from l10n_ec_edi.
    """

    _inherit = "res.company"

    # Additional fields not in l10n_ec_edi - URLs can be overridden
    l10n_ec_sri_reception_url = fields.Char(
        string="Reception WSDL",
        default="https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl",
    )

    l10n_ec_sri_authorization_url = fields.Char(
        string="Authorization WSDL",
        default="https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl",
    )
