# -*- coding: utf-8 -*-
import logging

from markupsafe import Markup

from odoo import _, api, models

from .das_email_template_layout import das_email_render_course_cards_html

_logger = logging.getLogger(__name__)

_INTEREST_LIST_XMLIDS = {
    'das_email_preferences.das_email_interest_technology': 'das_email_campaigns.mailing_list_das_interest_technology',
    'das_email_preferences.das_email_interest_development': 'das_email_campaigns.mailing_list_das_interest_development',
    'das_email_preferences.das_email_interest_design': 'das_email_campaigns.mailing_list_das_interest_design',
    'das_email_preferences.das_email_interest_marketing': 'das_email_campaigns.mailing_list_das_interest_marketing',
    'das_email_preferences.das_email_interest_quality': 'das_email_campaigns.mailing_list_das_interest_quality',
}

_CATEGORY_LIST_XMLIDS = {
    'das_email_preferences.das_email_course_category_lms': 'das_email_campaigns.mailing_list_das_category_lms',
    'das_email_preferences.das_email_course_category_cert': 'das_email_campaigns.mailing_list_das_category_cert',
    'das_email_preferences.das_email_course_category_workshops': 'das_email_campaigns.mailing_list_das_category_workshops',
}

_LEVEL_LIST_XMLIDS = {
    'beginner': 'das_email_campaigns.mailing_list_das_level_beginner',
    'intermediate': 'das_email_campaigns.mailing_list_das_level_intermediate',
    'advanced': 'das_email_campaigns.mailing_list_das_level_advanced',
    'expert': 'das_email_campaigns.mailing_list_das_level_expert',
}


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _das_email_campaign_course_block(self, variant='newsletter', courses_title='Cursos destacados', limit=5):
        """HTML de cursos relevantes para este contacto (renderizado por QWeb al enviar)."""
        self.ensure_one()
        Runner = self.env['das.email.campaign.runner'].sudo()
        level = self.das_experience_level if variant == 'experience' else None
        channels = Runner._channels_for_partner(
            self, limit=int(limit) or 5, level_filter=level,
        )
        if not channels and variant == 'experience' and level:
            Channel = self.env['slide.channel'].sudo()
            channels = Channel.search([
                ('website_published', '=', True),
                ('das_experience_level', '=', level),
            ], limit=int(limit) or 5, order='das_email_published_date desc, create_date desc')
        html = das_email_render_course_cards_html(
            channels, self.env, title=courses_title or _('Cursos destacados'),
        )
        return Markup(html or '')

    def _das_is_ready_for_auto_campaigns(self):
        self.ensure_one()
        return bool(
            self.email
            and self.das_comm_email
            and self.das_preference_completed
        )

    @api.model
    def _das_reference_mailing_list_ids(self):
        """Listas DAS solo para referencia / envío manual (no usadas por el runner)."""
        return set(self.env['mailing.list'].sudo().search([
            ('name', '=like', 'DAS ·%'),
        ]).ids)

    def _das_target_mailing_list_ids(self):
        """Listas en las que debe estar el contacto según preferencias actuales."""
        self.ensure_one()
        if not self._das_is_ready_for_auto_campaigns():
            return set()
        list_ids = set()
        base_list = self.env.ref(
            'das_email_campaigns.mailing_list_das_opted_in',
            raise_if_not_found=False,
        )
        if base_list:
            list_ids.add(base_list.id)
        for interest in self.das_interest_ids:
            lst = self._das_mailing_list_for_interest(interest)
            if lst:
                list_ids.add(lst.id)
        for category in self.das_course_category_ids:
            lst = self._das_mailing_list_for_category(category)
            if lst:
                list_ids.add(lst.id)
        if self.das_experience_level:
            level_xml = _LEVEL_LIST_XMLIDS.get(self.das_experience_level)
            if level_xml:
                level_list = self.env.ref(level_xml, raise_if_not_found=False)
                if level_list:
                    list_ids.add(level_list.id)
        return list_ids

    def _das_mailing_list_for_interest(self, interest):
        for interest_xml, list_xml in _INTEREST_LIST_XMLIDS.items():
            rec = self.env.ref(interest_xml, raise_if_not_found=False)
            if rec and rec.id == interest.id:
                return self.env.ref(list_xml, raise_if_not_found=False)
        return self.env['mailing.list'].sudo().search([
            ('name', '=', _('DAS · Interés: %s') % interest.name),
        ], limit=1)

    def _das_mailing_list_for_category(self, category):
        for cat_xml, list_xml in _CATEGORY_LIST_XMLIDS.items():
            rec = self.env.ref(cat_xml, raise_if_not_found=False)
            if rec and rec.id == category.id:
                return self.env.ref(list_xml, raise_if_not_found=False)
        return self.env['mailing.list'].sudo().search([
            ('name', '=', _('DAS · Categoría: %s') % category.name),
        ], limit=1)

    def _das_sync_email_marketing_segments(self):
        """Suscribe a listas de referencia (manual). No afecta campañas automáticas."""
        Contact = self.env['mailing.contact'].sudo()
        Subscription = self.env['mailing.subscription'].sudo()
        das_list_ids = self._das_reference_mailing_list_ids()

        for partner in self:
            contact = Contact.search([('email', '=', partner.email)], limit=1) if partner.email else False

            if not partner._das_is_ready_for_auto_campaigns():
                if contact and das_list_ids:
                    Subscription.search([
                        ('contact_id', '=', contact.id),
                        ('list_id', 'in', list(das_list_ids)),
                    ]).unlink()
                continue

            if not contact:
                contact = Contact.create({
                    'name': partner.name or partner.email,
                    'email': partner.email,
                })
            elif contact.name != partner.name and partner.name:
                contact.write({'name': partner.name})

            target_list_ids = partner._das_target_mailing_list_ids()

            Subscription.search([
                ('contact_id', '=', contact.id),
                ('list_id', 'in', list(das_list_ids)),
                ('list_id', 'not in', list(target_list_ids)),
            ]).unlink()

            existing = set(Subscription.search([
                ('contact_id', '=', contact.id),
                ('list_id', 'in', list(target_list_ids)),
            ]).mapped('list_id').ids)

            for list_id in target_list_ids - existing:
                Subscription.create({
                    'contact_id': contact.id,
                    'list_id': list_id,
                })

            partner.message_post(
                body=_(
                    'Listas de referencia Email Marketing: %(count)s segmentos '
                    '(solo envío manual; campañas automáticas usan preferencias en contacto).',
                    count=len(target_list_ids),
                ),
                subtype_xmlid='mail.mt_note',
            )

    def _das_ensure_campaign_ready(self):
        """Tras completar preferencias: listas de referencia + elegibilidad automática."""
        for partner in self:
            partner._das_sync_email_marketing_segments()

    @api.model
    def _das_reconcile_all_marketing_segments(self):
        """Sincroniza segmentos para contactos con preferencias completadas."""
        partners = self.search([
            ('das_preference_completed', '=', True),
            ('email', '!=', False),
        ])
        for partner in partners:
            try:
                partner._das_sync_email_marketing_segments()
            except Exception:
                _logger.exception(
                    'DAS campaigns: error sincronizando segmentos partner id=%s.',
                    partner.id,
                )
