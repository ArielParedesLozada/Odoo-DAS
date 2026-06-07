# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountMove(models.Model):
    _inherit = "account.move"

    l10n_ec_sustento_code = fields.Char(
        string="Sustento Tributario", help="Código de Sustento Tributario para ATS"
    )
