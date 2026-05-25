# -*- coding: utf-8 -*-
import logging

from odoo import _, api, models

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
        """Suscribe el contacto a listas segmentadas según preferencias."""
        Contact = self.env['mailing.contact'].sudo()
        Subscription = self.env['mailing.subscription'].sudo()
        for partner in self:
            if not partner.email or not partner.das_comm_email:
                continue
            if not partner.das_preference_completed:
                continue

            contact = Contact.search([('email', '=', partner.email)], limit=1)
            if not contact:
                contact = Contact.create({
                    'name': partner.name or partner.email,
                    'email': partner.email,
                })
            elif contact.name != partner.name and partner.name:
                contact.write({'name': partner.name})

            list_ids = set()
            base_list = self.env.ref(
                'das_email_campaigns.mailing_list_das_opted_in',
                raise_if_not_found=False,
            )
            if base_list:
                list_ids.add(base_list.id)

            for interest in partner.das_interest_ids:
                lst = partner._das_mailing_list_for_interest(interest)
                if lst:
                    list_ids.add(lst.id)

            for category in partner.das_course_category_ids:
                lst = partner._das_mailing_list_for_category(category)
                if lst:
                    list_ids.add(lst.id)

            if partner.das_experience_level:
                level_xml = _LEVEL_LIST_XMLIDS.get(partner.das_experience_level)
                if level_xml:
                    level_list = self.env.ref(level_xml, raise_if_not_found=False)
                    if level_list:
                        list_ids.add(level_list.id)

            existing = set(Subscription.search([
                ('contact_id', '=', contact.id),
                ('list_id', 'in', list(list_ids)),
            ]).mapped('list_id').ids)

            for list_id in list_ids - existing:
                Subscription.create({
                    'contact_id': contact.id,
                    'list_id': list_id,
                })

            partner.message_post(
                body=_(
                    'Suscripción automática a Email Marketing: %(count)s listas '
                    'segmentadas (intereses, categorías y nivel).',
                    count=len(list_ids),
                ),
                subtype_xmlid='mail.mt_note',
            )

    @api.model
    def _das_reconcile_all_marketing_segments(self):
        """Sincroniza segmentos para contactos con preferencias completadas."""
        partners = self.search([
            ('das_preference_completed', '=', True),
            ('das_comm_email', '=', True),
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
