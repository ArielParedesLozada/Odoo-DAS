# -*- coding: utf-8 -*-
import logging

from odoo.addons.das_email_campaigns.models.das_email_assets import (
    das_email_ensure_logo_attachment,
    das_email_qwebify_body,
)
from odoo.addons.das_email_campaigns.models.das_email_template_layout import (
    das_email_render,
    das_email_subject,
)

_logger = logging.getLogger(__name__)

_LIST_TEMPLATE_MAP = {
    'das_email_campaigns.mail_template_das_list_newsletter': 'newsletter',
    'das_email_campaigns.mail_template_das_list_interest': 'interest',
    'das_email_campaigns.mail_template_das_list_category': 'category',
    'das_email_campaigns.mail_template_das_list_level': 'level',
    'das_email_campaigns.mail_template_das_list_upcoming': 'upcoming',
    'das_email_campaigns.mail_template_das_birthday': 'birthday',
    'das_email_campaigns.mail_template_das_upcoming': 'upcoming',
    'das_email_campaigns.mail_template_das_new_courses': 'new_courses',
    'das_email_campaigns.mail_template_das_experience': 'experience',
    'das_email_campaigns.mail_template_das_newsletter': 'newsletter',
}


def _sync_mail_templates(env):
    """Actualiza plantillas mail.template en BD con diseño DAS actual."""
    Template = env['mail.template'].sudo()
    for xml_name, variant in _LIST_TEMPLATE_MAP.items():
        module, name = xml_name.split('.')
        tmpl = env.ref('%s.%s' % (module, name), raise_if_not_found=False)
        if not tmpl:
            continue
        try:
            tmpl.write({
                'subject': das_email_subject(variant),
                'body_html': das_email_qwebify_body(das_email_render(variant, env)),
            })
        except Exception:
            _logger.exception('DAS: no se pudo actualizar plantilla %s.', xml_name)


def _dedupe_das_mailing_lists(env):
    """Fusiona listas DAS duplicadas (mismo nombre) en la más antigua."""
    List = env['mailing.list'].sudo()
    Subscription = env['mailing.subscription'].sudo()
    das_lists = List.search([('name', 'like', 'DAS ·%')], order='id')
    canonical_by_name = {}
    for mailing_list in das_lists:
        if mailing_list.name not in canonical_by_name:
            canonical_by_name[mailing_list.name] = mailing_list
            continue
        canonical = canonical_by_name[mailing_list.name]
        subs = Subscription.search([('list_id', '=', mailing_list.id)])
        for sub in subs:
            exists = Subscription.search([
                ('list_id', '=', canonical.id),
                ('contact_id', '=', sub.contact_id.id),
            ], limit=1)
            if not exists:
                sub.write({'list_id': canonical.id})
            else:
                sub.unlink()
        mailing_list.write({'active': False})
        _logger.info(
            'DAS campaigns: lista duplicada desactivada id=%s (%s).',
            mailing_list.id,
            mailing_list.name,
        )


def post_init_hook(env):
    """Sincroniza plantillas, listas y segmentos."""
    try:
        das_email_ensure_logo_attachment(env)
    except Exception:
        _logger.exception('DAS email campaigns: error creando adjunto del logo.')
    try:
        _sync_mail_templates(env)
    except Exception:
        _logger.exception('DAS email campaigns: error sincronizando plantillas.')
    try:
        _dedupe_das_mailing_lists(env)
    except Exception:
        _logger.exception('DAS email campaigns: error deduplicando listas.')
    try:
        env['slide.channel']._das_configure_published_channels_email_marketing()
    except Exception:
        _logger.exception('DAS email campaigns: error configurando cursos.')
    try:
        env['res.partner']._das_reconcile_all_marketing_segments()
    except Exception:
        _logger.exception('DAS email campaigns: error sincronizando segmentos de contactos.')
    try:
        env['das.email.campaign.config']._das_ensure_active_campaign_configs()
    except Exception:
        _logger.exception('DAS email campaigns: error activando configuraciones de campaña.')
