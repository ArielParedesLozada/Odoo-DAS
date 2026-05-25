# -*- coding: utf-8 -*-
import datetime

from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from email.utils import make_msgid

from odoo import models
from odoo import tools


class IrMailServer(models.Model):
    _inherit = 'ir.mail_server'

    def build_email(self, email_from, email_to, subject, body, email_cc=None, email_bcc=None,
                    reply_to=False, attachments=None, message_id=None, references=None,
                    object_id=False, subtype='plain', headers=None, body_alternative=None,
                    subtype_alternative='plain'):
        """Soporta adjuntos inline con Content-ID (logo DAS en campañas)."""
        if not attachments or not any(len(a) > 3 for a in attachments):
            return super().build_email(
                email_from, email_to, subject, body,
                email_cc=email_cc, email_bcc=email_bcc, reply_to=reply_to,
                attachments=attachments, message_id=message_id, references=references,
                object_id=object_id, subtype=subtype, headers=headers,
                body_alternative=body_alternative, subtype_alternative=subtype_alternative,
            )

        email_from = email_from or self.env.context.get('domain_notifications_email') or self._get_default_from_address()
        headers = headers or {}
        email_cc = email_cc or []
        email_bcc = email_bcc or []

        msg = EmailMessage(policy=policy.SMTP)
        if not message_id:
            if object_id:
                message_id = tools.mail.generate_tracking_message_id(object_id)
            else:
                message_id = make_msgid()
        msg['Message-Id'] = message_id
        if references:
            msg['references'] = references
        msg['Subject'] = subject
        msg['From'] = email_from
        msg['Reply-To'] = reply_to or email_from
        msg['To'] = email_to
        if email_cc:
            msg['Cc'] = email_cc
        if email_bcc:
            msg['Bcc'] = email_bcc
        msg['Date'] = datetime.datetime.utcnow()
        for key, value in headers.items():
            msg[key] = value

        email_body = body or ''
        target = msg
        if subtype == 'html' and not body_alternative:
            msg['MIME-Version'] = '1.0'
            msg.add_alternative(tools.html2plaintext(email_body), subtype='plain', charset='utf-8')
            target = msg.add_alternative('', subtype='related')
            target.set_content(email_body, subtype='html', charset='utf-8')
        elif body_alternative:
            msg['MIME-Version'] = '1.0'
            msg.add_alternative(body_alternative, subtype=subtype_alternative, charset='utf-8')
            msg.add_alternative(email_body, subtype=subtype, charset='utf-8')
        else:
            msg.set_content(email_body, subtype=subtype, charset='utf-8')

        for attachment in attachments:
            if len(attachment) >= 4:
                fname, fcontent, mime, content_id = attachment[:4]
                maintype, subtype_part = mime.split('/') if mime and '/' in mime else ('application', 'octet-stream')
                cid = content_id if content_id.startswith('<') else '<%s>' % content_id
                target.add_attachment(
                    fcontent,
                    maintype=maintype,
                    subtype=subtype_part,
                    filename=fname,
                    cid=cid,
                )
            else:
                fname, fcontent = attachment[0], attachment[1]
                mime = attachment[2] if len(attachment) > 2 else 'application/octet-stream'
                maintype, subtype_part = mime.split('/') if '/' in mime else ('application', 'octet-stream')
                if maintype == 'message' and subtype_part == 'rfc822':
                    target.add_attachment(BytesParser().parsebytes(fcontent), filename=fname)
                else:
                    target.add_attachment(fcontent, maintype, subtype_part, filename=fname)
        return msg
