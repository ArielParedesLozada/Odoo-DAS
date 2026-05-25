# -*- coding: utf-8 -*-
import re

from odoo import models, tools

from .das_email_assets import LOGO_CID_SRC, das_email_logo_attachment_tuple


class MailMail(models.Model):
    _inherit = 'mail.mail'

    def _das_body_has_logo(self, body):
        return body and ('Academia Virtual DAS' in body or LOGO_CID_SRC in body)

    def _das_inject_logo_cid(self, body, attachments):
        """Adjunta el logo como imagen inline (CID) para Gmail y otros clientes."""
        if not self._das_body_has_logo(body):
            return body, attachments

        logo_tuple = das_email_logo_attachment_tuple(self.env)
        if not logo_tuple:
            return body, attachments

        body = re.sub(
            r'<img[^>]*alt="Academia Virtual DAS"[^>]*/?>',
            lambda m: re.sub(
                r'src="[^"]*"',
                'src="%s"' % LOGO_CID_SRC,
                m.group(0),
                count=1,
            ) if LOGO_CID_SRC not in m.group(0) else m.group(0),
            body,
            count=1,
        )
        attachments = list(attachments or [])
        if not any(len(a) > 3 and a[3] == logo_tuple[3] for a in attachments):
            attachments.append(logo_tuple)
        return body, attachments

    def _prepare_outgoing_list(self, mail_server=False, recipients_follower_status=None):
        results = super()._prepare_outgoing_list(
            mail_server=mail_server,
            recipients_follower_status=recipients_follower_status,
        )
        for email_values in results:
            body, attachments = self._das_inject_logo_cid(
                email_values.get('body', ''),
                email_values.get('attachments', []),
            )
            email_values['body'] = body
            email_values['attachments'] = attachments
            email_values['body_alternative'] = tools.html2plaintext(body)
        return results
