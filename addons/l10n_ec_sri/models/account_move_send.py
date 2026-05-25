# -*- coding: utf-8 -*-
import base64

from odoo import api, models


class AccountMoveSend(models.AbstractModel):
    _inherit = "account.move.send"

    @api.model
    def _get_invoice_extra_attachments(self, move):
        attachments = super()._get_invoice_extra_attachments(move)

        if (
            move.company_id.country_id.code == "EC"
            and move.move_type in ("out_invoice", "out_refund")
            and move.l10n_ec_xml_data
        ):
            xml_name = "%s.xml" % move.name.replace("/", "-")
            xml_attachment = self.env["ir.attachment"].sudo().search(
                [
                    ("res_model", "=", move._name),
                    ("res_id", "=", move.id),
                    ("name", "=", xml_name),
                ],
                limit=1,
            )
            if not xml_attachment:
                xml_attachment = move._l10n_ec_create_or_replace_attachment(
                    xml_name,
                    base64.b64decode(move.l10n_ec_xml_data),
                    "application/xml",
                )
            attachments |= xml_attachment

        return attachments
