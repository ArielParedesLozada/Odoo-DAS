# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.model
    def _l10n_ec_sri_urls_for_environment(self, environment):
        if environment == "production":
            return {
                "l10n_ec_sri_reception_url": "https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl",
                "l10n_ec_sri_authorization_url": "https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl",
            }
        return {
            "l10n_ec_sri_reception_url": "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl",
            "l10n_ec_sri_authorization_url": "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl",
        }

    l10n_ec_sri_environment = fields.Selection(
        [
            ("demo", "Demo local"),
            ("test", "SRI Test"),
            ("production", "SRI Production"),
        ],
        string="SRI Environment",
        default="test",
        help=(
            "Demo local generates the access key and XML without signing or "
            "connecting to SRI. SRI Test and SRI Production require an active "
            "electronic signature."
        ),
    )

    # Linked to the robust Certificate model instead of simple binary
    l10n_ec_certificate_id = fields.Many2one(
        "l10n_ec.certificate",
        string="SRI Electronic Signature",
        domain=[("state", "=", "active")],
        help="Select the active P12 certificate for signing.",
    )

    l10n_ec_withhold_agent = fields.Boolean("Withholding Agent")
    l10n_ec_withhold_resolution = fields.Char("Resolution Number")
    l10n_ec_special_resolution = fields.Char("Special Contributor Resolution")
    l10n_ec_forced_accounting = fields.Boolean("Forced to keep Accounting")
    l10n_ec_commercial_name = fields.Char("Commercial Name")
    l10n_ec_sri_pending_cron_interval_minutes = fields.Integer(
        string="Pending Invoice Check Interval",
        default=30,
        help="Minutes between automatic checks for invoices already received by SRI.",
    )
    l10n_ec_sri_first_check_delay_seconds = fields.Integer(
        string="First Authorization Check Delay",
        default=5,
        help="Seconds to wait after SRI reception before the first authorization check.",
    )

    # URLs
    l10n_ec_sri_reception_url = fields.Char(
        string="SRI Reception URL",
        default="https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl",
    )
    l10n_ec_sri_authorization_url = fields.Char(
        string="SRI Authorization URL",
        default="https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl",
    )

    @api.onchange("l10n_ec_sri_environment")
    def _onchange_l10n_ec_sri_environment(self):
        self.update(self._l10n_ec_sri_urls_for_environment(self.l10n_ec_sri_environment))

    def write(self, vals):
        if "l10n_ec_sri_environment" in vals:
            vals = dict(vals)
            vals.update(self._l10n_ec_sri_urls_for_environment(vals["l10n_ec_sri_environment"]))
        result = super().write(vals)
        if "l10n_ec_sri_pending_cron_interval_minutes" in vals:
            cron = self.env.ref(
                "l10n_ec_sri.ir_cron_l10n_ec_sri_process_pending",
                raise_if_not_found=False,
            )
            if cron:
                interval = max(vals["l10n_ec_sri_pending_cron_interval_minutes"], 1)
                cron.sudo().write({"interval_number": interval, "interval_type": "minutes"})
        return result
