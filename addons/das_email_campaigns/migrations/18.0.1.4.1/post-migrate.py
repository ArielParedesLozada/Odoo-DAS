# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    try:
        from odoo.addons.das_email_campaigns.hooks import _sync_mail_templates
        _sync_mail_templates(env)
        _logger.info('DAS: plantillas de email actualizadas (18.0.1.4.1).')
    except Exception:
        _logger.exception('DAS: migración 18.0.1.4.1 — error actualizando plantillas.')
