# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import UserError
import base64
import datetime
import logging
import time


_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    """
    Extends account.move with SRI integration logic.
    Field definitions inherited from l10n_ec_edi.

    Note: 2026 Consumidor Final validations are handled by l10n_ec_edi module.
    """

    _inherit = "account.move"

    # Additional fields not in l10n_ec_edi
    l10n_ec_authorization_date = fields.Datetime(
        string="Authorization Date", copy=False
    )
    l10n_ec_sri_error = fields.Text(string="SRI Error Message", copy=False)
    l10n_ec_authorized_email_sent = fields.Boolean(
        string="Authorized Documents Sent", copy=False
    )
    l10n_ec_authorized_email_sent_date = fields.Datetime(
        string="Authorized Documents Sent On", copy=False
    )

    def _generate_l10n_ec_xml_content(self):
        self.ensure_one()
        if not self._l10n_ec_access_key_matches_move():
            self.l10n_ec_sri_access_key = self.env[
                "l10n_ec.sri.xml"
            ].generate_access_key(self)

        xml_content = self.env["l10n_ec.sri.xml"].render_xml(self)
        if not isinstance(xml_content, bytes):
            xml_content = xml_content.encode("utf-8")
        return xml_content

    def _l10n_ec_access_key_matches_move(self):
        self.ensure_one()
        access_key = self.l10n_ec_sri_access_key or ""
        if len(access_key) != 49 or not access_key.isdigit():
            return False

        sri_xml = self.env["l10n_ec.sri.xml"]
        expected_ruc = sri_xml._only_digits(self.company_id.vat)
        expected_environment = sri_xml._get_environment_code(self.company_id)
        expected_series = sri_xml._get_document_series(self)
        expected_sequential = sri_xml._get_document_sequential(self)

        return (
            access_key[10:23] == expected_ruc
            and access_key[23:24] == expected_environment
            and access_key[24:30] == expected_series
            and access_key[30:39] == expected_sequential
        )

    def action_generate_demo_xml(self):
        for move in self:
            if move.state != "posted":
                raise UserError(_("Invoice must be Posted before generating the demo XML."))

            xml_content = move._generate_l10n_ec_xml_content()
            move.l10n_ec_xml_data = base64.b64encode(xml_content)
            move._l10n_ec_create_or_replace_attachment(
                "%s.xml" % move.name.replace("/", "-"),
                xml_content,
                "application/xml",
            )
            move.l10n_ec_sri_status = "signed"
            move.l10n_ec_sri_error = False
            move.l10n_ec_sri_response = _(
                "Demo local: XML generated without signature and without SRI transmission."
            )

    def action_send_sri(self):
        """
        Queue the SRI process without blocking the user interface.

        The expensive work (SOAP reception, authorization check, PDF/XML
        attachment generation and email delivery) is processed by the cron.
        """
        for move in self:
            if move.l10n_ec_sri_status in ["authorized", "sent", "signed"]:
                continue

            if move.company_id.l10n_ec_sri_environment == "demo":
                move.action_generate_demo_xml()
                continue

            if move.state != "posted":
                raise UserError(_("Invoice must be Posted before sending to SRI."))

            move._l10n_ec_prepare_signed_xml_for_sri()
            move.l10n_ec_sri_status = "signed"
            move.l10n_ec_sri_error = False
            move.l10n_ec_sri_response = _(
                "Queued for SRI transmission. The electronic invoice is being processed in the background."
            )

        self._l10n_ec_trigger_sri_cron()
        return True

    def _l10n_ec_prepare_signed_xml_for_sri(self):
        self.ensure_one()
        if self.company_id.l10n_ec_sri_environment == "demo":
            return self.action_generate_demo_xml()

        if self.state != "posted":
            raise UserError(_("Invoice must be Posted before sending to SRI."))

        certificate = self.company_id.l10n_ec_certificate_id
        if not certificate or certificate.state != "active":
            raise UserError(_("No active Electronic Signature found for this company."))

        # Generate the signed XML and store it immediately so the file exists
        # while the SRI transmission continues in the background.
        xml_content = self._generate_l10n_ec_xml_content()
        signed_xml = self._sign_xml(xml_content)
        self.l10n_ec_xml_data = base64.b64encode(signed_xml)
        self._l10n_ec_create_or_replace_attachment(
            "%s.xml" % self.name.replace("/", "-"),
            signed_xml,
            "application/xml",
        )
        return signed_xml

    def _l10n_ec_send_sri_now(self):
        """
        Execute the real SRI transmission.

        This method is intended for cron/background usage. It can be called
        manually by tests or maintenance scripts, but UI buttons should call
        action_send_sri() to avoid blocking the web request.
        """
        for move in self:
            if move.l10n_ec_sri_status in ["authorized", "sent"]:
                continue

            if move.company_id.l10n_ec_sri_environment == "demo":
                move.action_generate_demo_xml()
                continue

            if not move.l10n_ec_xml_data or move.l10n_ec_sri_status == "rejected":
                signed_xml = move._l10n_ec_prepare_signed_xml_for_sri()
            else:
                signed_xml = base64.b64decode(move.l10n_ec_xml_data)

            move.l10n_ec_sri_response = _("Sending signed XML to SRI.")

            env_code = self.env["l10n_ec.sri.xml"]._get_environment_code(move.company_id)
            response = self.env["l10n_ec.sri.service"].send_document(
                signed_xml, environment=env_code
            )

            if response.get("status") == "RECIBIDA":
                move.l10n_ec_sri_status = "sent"
                move.l10n_ec_sri_error = False
                move.l10n_ec_sri_response = _(
                    "RECIBIDA. Waiting for authorization."
                )
                move._l10n_ec_first_authorization_check()
            else:
                move.l10n_ec_sri_status = "rejected"
                move.l10n_ec_sri_error = "\n".join(response.get("messages", []))

    def _l10n_ec_trigger_sri_cron(self):
        cron = self.env.ref(
            "l10n_ec_sri.ir_cron_l10n_ec_sri_process_pending",
            raise_if_not_found=False,
        )
        if cron:
            cron.sudo()._trigger()

    def _l10n_ec_first_authorization_check(self):
        self.ensure_one()
        delay = max(self.company_id.l10n_ec_sri_first_check_delay_seconds or 0, 0)
        if delay:
            time.sleep(min(delay, 60))
        self.action_check_sri()

    def action_check_sri(self):
        """
        Ping Check Status service (Real Implementation)
        """
        for move in self:
            if not move.l10n_ec_sri_access_key:
                raise UserError(_("No Access Key generated yet."))

            response = self.env["l10n_ec.sri.service"].check_authorization(
                move.l10n_ec_sri_access_key
            )

            if response.get("status") == "AUTORIZADO":
                move.l10n_ec_sri_status = "authorized"
                move.l10n_ec_sri_error = False
                move.l10n_ec_sri_response = _("AUTORIZADO")
                if response.get("date"):
                    move.l10n_ec_authorization_date = (
                        move._l10n_ec_to_odoo_datetime(response["date"])
                    )

                authorized_xml = response.get("authorized_xml") or response.get("xml")
                if authorized_xml:
                    move.l10n_ec_xml_data = base64.b64encode(
                        authorized_xml.encode("utf-8")
                    )
                move._l10n_ec_send_authorized_documents_email()
            elif response.get("status") == "NO AUTORIZADO":
                move.l10n_ec_sri_status = "rejected"
                move.l10n_ec_sri_error = "\n".join(response.get("messages", []))
            elif response.get("status") in ("PENDING", "EN PROCESO"):
                move.l10n_ec_sri_status = "sent"
                move.l10n_ec_sri_error = False
                move.l10n_ec_sri_response = "\n".join(response.get("messages", []))
            elif response.get("status") == "ERROR":
                move.l10n_ec_sri_status = "sent"
                move.l10n_ec_sri_error = "\n".join(response.get("messages", []))

    def _sign_xml(self, xml_content):
        """
        Internal helper to call the signer lib.
        """
        self.ensure_one()
        certificate = self.company_id.l10n_ec_certificate_id
        if not certificate:
            raise UserError(_("No active Electronic Signature found for this company."))

        return self.env["l10n_ec.sri.signer"].sign_xml(
            xml_content, certificate.content, certificate.password
        )

    def _l10n_ec_to_odoo_datetime(self, value):
        if not value:
            return False

        if isinstance(value, str):
            value = fields.Datetime.to_datetime(value)

        if isinstance(value, datetime.datetime) and value.tzinfo:
            value = value.astimezone(datetime.timezone.utc).replace(tzinfo=None)

        return value

    def _is_ready_to_be_sent(self):
        self.ensure_one()
        if (
            self.company_id.country_id.code == "EC"
            and self.move_type in ("out_invoice", "out_refund")
        ):
            # Avoid Odoo's generic automatic invoice email from sale/payment.
            # Ecuadorian electronic invoices must be delivered by the SRI flow
            # after authorization, with the final RIDE and XML.
            return False
        return super()._is_ready_to_be_sent()

    @api.model
    def _cron_l10n_ec_process_pending_sri(self, limit=50):
        invoices = self.search(
            [
                ("move_type", "in", ("out_invoice", "out_refund")),
                ("state", "=", "posted"),
                ("l10n_ec_sri_status", "in", ("signed", "sent")),
            ],
            limit=limit,
            order="invoice_date asc, id asc",
        )
        for move in invoices:
            try:
                if move.l10n_ec_sri_status == "signed":
                    move._l10n_ec_send_sri_now()
                else:
                    move.action_check_sri()
            except Exception:
                _logger.exception("Could not process pending SRI invoice %s", move.name)

    def _l10n_ec_send_authorized_documents_email(self):
        for move in self:
            self.env.cr.execute(
                "SELECT id FROM account_move WHERE id = %s FOR UPDATE",
                [move.id],
            )
            move.invalidate_recordset(
                ["l10n_ec_authorized_email_sent", "is_move_sent"]
            )
            if move.l10n_ec_authorized_email_sent:
                continue
            if not move.partner_id.email:
                move.l10n_ec_sri_response = _(
                    "AUTORIZADO. Customer has no email, documents were not sent."
                )
                continue

            move.l10n_ec_authorized_email_sent = True
            move.l10n_ec_authorized_email_sent_date = fields.Datetime.now()
            attachments = move._l10n_ec_prepare_authorized_attachments()
            template = self.env.ref(
                "account.email_template_edi_invoice", raise_if_not_found=False
            )
            try:
                move._l10n_ec_post_and_send_authorized_documents(
                    attachments, template
                )
            except Exception:
                move.l10n_ec_authorized_email_sent = False
                move.l10n_ec_authorized_email_sent_date = False
                raise

            move.is_move_sent = True

    def _l10n_ec_get_authorized_documents_message_values(self, template=False):
        self.ensure_one()

        subject = _("Electronic Invoice %s") % self.name
        body = _("<p>Attached are your electronic invoice PDF and XML.</p>")
        if template:
            values = template.with_context(lang=self.partner_id.lang)._generate_template(
                [self.id], ["subject", "body_html"]
            ).get(self.id, {})
            subject = values.get("subject") or subject
            body = values.get("body_html") or body

        return subject, body

    def _l10n_ec_post_and_send_authorized_documents(self, attachments, template=False):
        self.ensure_one()
        subject, body = self._l10n_ec_get_authorized_documents_message_values(template)

        existing_message = self.message_ids.filtered(
            lambda message: message.subject == subject
        )
        if existing_message:
            return

        self.with_context(
            mail_create_nosubscribe=True,
            mail_notify_force_send=True,
            email_notification_allow_footer=True,
        ).message_post(
            body=body,
            subject=subject,
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
            partner_ids=[self.partner_id.id],
            email_layout_xmlid="mail.mail_notification_layout_with_responsible_signature",
            mail_auto_delete=True,
            attachments=[
                (attachment.name, attachment.raw)
                for attachment in attachments.sudo()
            ],
        )

    def _l10n_ec_prepare_authorized_attachments(self):
        self.ensure_one()
        attachments = self.env["ir.attachment"]

        report = self.env.ref("account.account_invoices")
        pdf_content, _ = report.with_context(lang=self.partner_id.lang)._render_qweb_pdf(
            report.report_name, [self.id]
        )
        attachments |= self._l10n_ec_create_or_replace_attachment(
            "%s-RIDE.pdf" % self.name.replace("/", "-"),
            pdf_content,
            "application/pdf",
        )

        if self.l10n_ec_xml_data:
            xml_content = base64.b64decode(self.l10n_ec_xml_data)
            attachments |= self._l10n_ec_create_or_replace_attachment(
                "%s.xml" % self.name.replace("/", "-"),
                xml_content,
                "application/xml",
            )

        return attachments

    def _l10n_ec_create_or_replace_attachment(self, name, content, mimetype):
        self.ensure_one()
        attachment = self.env["ir.attachment"].sudo().search(
            [
                ("res_model", "=", self._name),
                ("res_id", "=", self.id),
                ("name", "=", name),
            ],
            limit=1,
        )
        values = {
            "name": name,
            "type": "binary",
            "datas": base64.b64encode(content),
            "res_model": self._name,
            "res_id": self.id,
            "mimetype": mimetype,
        }
        if attachment:
            attachment.write(values)
        else:
            attachment = self.env["ir.attachment"].sudo().create(values)
        return attachment
