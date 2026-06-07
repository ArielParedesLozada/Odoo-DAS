# -*- coding: utf-8 -*-
from odoo import _, api, fields, models

from .das_email_assets import (
    das_email_body_with_cid_logo,
    das_email_qwebify_body,
)


class MailingMailing(models.Model):
    _inherit = 'mailing.mailing'

    das_campaign_config_id = fields.Many2one(
        'das.email.campaign.config',
        string='Campaña DAS',
        ondelete='set null',
        index=True,
    )
    das_campaign_period_key = fields.Char(string='Periodo DAS', index=True)
    das_campaign_channel_id = fields.Many2one(
        'slide.channel',
        string='Curso DAS',
        ondelete='set null',
    )
    das_campaign_log_count = fields.Integer(
        compute='_compute_das_campaign_log_count',
        string='Registros DAS',
    )

    @api.model
    def _das_default_outgoing_mail_values(self):
        server = self.env['ir.mail_server'].sudo().search(
            [('active', '=', True)],
            order='sequence, id',
            limit=1,
        )
        if not server:
            return {}
        email_from = server.from_filter or server.smtp_user
        if email_from and '<' not in email_from:
            email_from = '"Academia Virtual DAS" <%s>' % email_from
        return {
            'mail_server_id': server.id,
            'email_from': email_from or False,
        }

    @api.model
    def _das_finalize_body_html(self, body):
        body = das_email_qwebify_body(body or '')
        return das_email_body_with_cid_logo(body)

    def _das_finalize_body_html_record(self, body):
        return self._das_finalize_body_html(body)

    @api.model_create_multi
    def create(self, vals_list):
        defaults = self._das_default_outgoing_mail_values()
        prepared = []
        for vals in vals_list:
            vals = dict(vals)
            if defaults:
                vals.setdefault('mail_server_id', defaults.get('mail_server_id'))
                vals.setdefault('email_from', defaults.get('email_from'))
            if vals.get('body_html'):
                vals['body_html'] = self._das_finalize_body_html(vals['body_html'])
            prepared.append(vals)
        return super(MailingMailing, self.with_context(das_keep_inline_logo=True)).create(prepared)

    def write(self, vals):
        vals = dict(vals)
        if vals.get('body_html') and not self.env.context.get('das_keep_inline_logo'):
            vals['body_html'] = self._das_finalize_body_html(vals['body_html'])
        ctx = self.env.context
        if vals.get('body_html'):
            ctx = dict(ctx, das_keep_inline_logo=True)
        res = super(MailingMailing, self.with_context(**ctx)).write(vals)
        if vals.get('state') == 'done':
            Log = self.env['das.email.campaign.log'].sudo()
            for mailing in self.filtered('das_campaign_config_id'):
                Log._sync_trace_status_from_mailing(mailing)
        return res

    def _convert_inline_images_to_urls(self, html_content):
        """No convertir el logo CID a /web/image/ (rompe Gmail)."""
        if self.env.context.get('das_keep_inline_logo'):
            return html_content
        if html_content and 'cid:das_email_logo' in html_content:
            return html_content
        return super()._convert_inline_images_to_urls(html_content)

    def _action_send_mail(self, res_ids=None):
        for mailing in self:
            body = mailing._das_finalize_body_html_record(mailing.body_html)
            if body != mailing.body_html:
                mailing.with_context(das_keep_inline_logo=True).sudo().write({'body_html': body})
        return super()._action_send_mail(res_ids)

    def _compute_das_campaign_log_count(self):
        Log = self.env['das.email.campaign.log']
        grouped = Log.read_group(
            [('mailing_id', 'in', self.ids)],
            ['mailing_id'],
            ['mailing_id'],
        )
        counts = {row['mailing_id'][0]: row['mailing_id_count'] for row in grouped}
        for mailing in self:
            mailing.das_campaign_log_count = counts.get(mailing.id, 0)

    def action_view_das_campaign_logs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Registros de campaña DAS'),
            'res_model': 'das.email.campaign.log',
            'view_mode': 'list,form',
            'domain': [('mailing_id', '=', self.id)],
        }

    def _das_sample_contact(self, contact=None):
        self.ensure_one()
        if contact:
            return contact
        if self.contact_list_ids:
            return self.contact_list_ids[0]._das_sample_contact()
        model = self.mailing_model_real or 'mailing.contact'
        if model == 'res.partner':
            domain = self._parse_mailing_domain() if hasattr(self, '_parse_mailing_domain') else []
            return self.env['res.partner'].search(domain, limit=1)
        return self.env['mailing.contact'].search([], limit=1)

    def _das_render_preview_html(self, contact=None):
        self.ensure_one()
        body = self._das_finalize_body_html_record(self.body_html or '')
        if not body:
            return '<p></p>'
        sample = self._das_sample_contact(contact)
        if not sample:
            return body
        model = self.mailing_model_real or sample._name
        rendered = self.env['mail.render.mixin']._render_template(
            body,
            model,
            sample.ids,
            engine='qweb',
            options={'post_process': False},
        )[sample.id]
        import base64
        from .das_email_assets import das_email_logo_bytes
        logo_bytes = das_email_logo_bytes(self.env)
        if logo_bytes and 'cid:das_email_logo' in rendered:
            b64 = base64.b64encode(logo_bytes).decode()
            rendered = rendered.replace(
                'cid:das_email_logo@academia',
                'data:image/png;base64,%s' % b64,
            )
        return rendered

    def action_das_preview_rendered(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/das_email/preview/mailing/%s' % self.id,
            'target': 'new',
        }
