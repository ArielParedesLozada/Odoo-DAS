# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    try:
        from odoo.addons.das_email_campaigns.hooks import _sync_mail_templates

        env['das.email.campaign.config']._das_ensure_active_campaign_configs()
        _sync_mail_templates(env)
        env['res.partner']._das_reconcile_all_marketing_segments()
        _logger.info('DAS 18.0.1.5.1: campañas activas, plantillas y segmentos de referencia sincronizados.')
    except Exception:
        _logger.exception('DAS: migración 18.0.1.5.1 fallida.')
