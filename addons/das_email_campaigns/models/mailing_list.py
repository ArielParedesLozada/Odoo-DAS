# -*- coding: utf-8 -*-
from odoo import Command, _, fields, models
from odoo.exceptions import UserError

from .das_email_template_layout import das_email_render, das_email_subject


class MailingList(models.Model):
    _inherit = 'mailing.list'

    das_is_reference_segment = fields.Boolean(
        string='Segmento de referencia DAS',
        compute='_compute_das_is_reference_segment',
        help='Las listas DAS · … no disparan campañas automáticas; solo envío manual y estadísticas.',
    )

    def _compute_das_is_reference_segment(self):
        for lst in self:
            lst.das_is_reference_segment = bool(
                lst.name and lst.name.startswith('DAS ·')
            )

    def _das_list_variant(self):
        """Tipo de plantilla según el nombre de la lista."""
        self.ensure_one()
        name = (self.name or '').lower()
        if 'interés' in name or 'interes' in name:
            return 'interest'
        if 'categoría' in name or 'categoria' in name:
            return 'category'
        if 'nivel' in name:
            return 'level'
        return 'newsletter'

    def _das_render_body_html(self):
        self.ensure_one()
        return das_email_render(self._das_list_variant(), self.env)

    def _das_render_subject(self):
        self.ensure_one()
        return das_email_subject(self._das_list_variant())

    def _das_sample_contact(self, contact=None):
        """Primer contacto de la lista para vista previa renderizada."""
        self.ensure_one()
        if contact:
            return contact
        Subscription = self.env['mailing.subscription'].sudo()
        sub = Subscription.search([
            ('list_id', '=', self.id),
            ('opt_out', '=', False),
        ], limit=1)
        return sub.contact_id if sub else self.env['mailing.contact']

    def _das_render_preview_html(self, contact=None):
        """HTML con nombre y logo reales (para vista previa en navegador)."""
        self.ensure_one()
        body = self.env['mailing.mailing']._das_finalize_body_html(self._das_render_body_html())
        sample = self._das_sample_contact(contact)
        if not sample:
            return body
        return self.env['mail.render.mixin']._render_template(
            body,
            'mailing.contact',
            sample.ids,
            engine='qweb',
            options={'post_process': True},
        )[sample.id]

    def action_das_preview_campaign(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/das_email/preview/list/%s' % self.id,
            'target': 'new',
        }

    def _das_prepare_mailing_vals(self):
        """Valores para crear un mailing.mailing listo para enviar."""
        self.ensure_one()
        if not self.contact_count:
            raise UserError(_(
                'La lista «%s» no tiene contactos. Importa o completa preferencias antes de enviar.',
                self.name,
            ))
        list_model = self.env['ir.model']._get('mailing.list')
        vals = {
            'name': '[DAS] %s' % self.name,
            'subject': self._das_render_subject(),
            'body_html': self._das_render_body_html(),
            'mailing_model_id': list_model.id,
            'contact_list_ids': [Command.set(self.ids)],
            'mailing_type': 'mail',
            'reply_to_mode': 'new',
        }
        vals.update(self.env['mailing.mailing']._das_default_outgoing_mail_values())
        return vals

    def _das_mailing_form_action(self, *, launch_now=False):
        self.ensure_one()
        if launch_now:
            mailing = self.env['mailing.mailing'].create(self._das_prepare_mailing_vals())
            mailing.action_launch()
            return {
                'type': 'ir.actions.act_window',
                'name': _('Correo enviado'),
                'res_model': 'mailing.mailing',
                'view_mode': 'form',
                'res_id': mailing.id,
                'target': 'current',
            }
        list_model = self.env['ir.model']._get('mailing.list')
        mail_defaults = self.env['mailing.mailing']._das_default_outgoing_mail_values()
        ctx = {
            **self.env.context,
            'default_name': '[DAS] %s' % self.name,
            'default_subject': self._das_render_subject(),
            'default_body_html': self._das_render_body_html(),
            'default_contact_list_ids': [Command.set(self.ids)],
            'default_mailing_type': 'mail',
            'default_mailing_model_id': list_model.id,
        }
        if mail_defaults.get('mail_server_id'):
            ctx['default_mail_server_id'] = mail_defaults['mail_server_id']
        if mail_defaults.get('email_from'):
            ctx['default_email_from'] = mail_defaults['email_from']
        return {
            'name': _('Enviar · %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'mailing.mailing',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'current',
            'context': ctx,
        }

    def action_send_mailing(self):
        """Abre formulario con plantilla DAS ya cargada."""
        if len(self) > 1:
            return self[0]._das_mailing_form_action(launch_now=False)
        return self._das_mailing_form_action(launch_now=False)

    def action_send_mailing_now(self):
        """Crea el correo con plantilla DAS y lo encola de inmediato."""
        self.ensure_one()
        return self._das_mailing_form_action(launch_now=True)
