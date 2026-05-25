# -*- coding: utf-8 -*-
from markupsafe import Markup

from odoo import models
from odoo.addons.mail.wizard.mail_compose_message import MailComposer


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def _das_body_is_das_campaign(self, body=None):
        body = body or self.body or ''
        return 'Academia Virtual DAS' in body

    def _prepare_mail_values(self, res_ids):
        is_das_mass = (
            self.composition_mode == 'mass_mail'
            and self.mass_mailing_id
            and self.model_is_thread
            and self._das_body_is_das_campaign()
        )
        if not is_das_mass:
            return super()._prepare_mail_values(res_ids)

        mail_values_all = MailComposer._prepare_mail_values(self, res_ids)
        trace_values_all = self._prepare_mail_values_mailing_traces(mail_values_all)

        for res_id, mail_values in mail_values_all.items():
            body_html = mail_values.get('body_html')
            if body_html:
                rendered = self.env['ir.qweb']._render(
                    'das_email_campaigns.das_email_mail_layout',
                    {'body': Markup(body_html)},
                    minimal_qcontext=True,
                    raise_if_not_found=False,
                )
                if rendered:
                    mail_values['body_html'] = rendered

            mail_values.update({
                'mailing_id': self.mass_mailing_id.id,
                'mailing_trace_ids': (
                    [(0, 0, trace_values_all[res_id])] if res_id in trace_values_all else False
                ),
            })
        return mail_values_all
