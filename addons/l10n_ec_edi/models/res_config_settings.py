# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    l10n_ec_sri_environment = fields.Selection(
        related="company_id.l10n_ec_sri_environment",
        readonly=False,
    )
    l10n_ec_certificate_id = fields.Many2one(
        related="company_id.l10n_ec_certificate_id",
        readonly=False,
    )
    l10n_ec_forced_accounting = fields.Boolean(
        related="company_id.l10n_ec_forced_accounting",
        readonly=False,
    )
    l10n_ec_commercial_name = fields.Char(
        related="company_id.l10n_ec_commercial_name",
        readonly=False,
    )
    l10n_ec_withhold_agent = fields.Boolean(
        related="company_id.l10n_ec_withhold_agent",
        readonly=False,
    )
    l10n_ec_withhold_resolution = fields.Char(
        related="company_id.l10n_ec_withhold_resolution",
        readonly=False,
    )
    l10n_ec_special_resolution = fields.Char(
        related="company_id.l10n_ec_special_resolution",
        readonly=False,
    )
    l10n_ec_sri_reception_url = fields.Char(
        related="company_id.l10n_ec_sri_reception_url",
        readonly=False,
    )
    l10n_ec_sri_authorization_url = fields.Char(
        related="company_id.l10n_ec_sri_authorization_url",
        readonly=False,
    )
    l10n_ec_sri_pending_cron_interval_minutes = fields.Integer(
        related="company_id.l10n_ec_sri_pending_cron_interval_minutes",
        readonly=False,
    )
    l10n_ec_sri_first_check_delay_seconds = fields.Integer(
        related="company_id.l10n_ec_sri_first_check_delay_seconds",
        readonly=False,
    )
