# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    try:
        from odoo.addons.das_email_campaigns.models.das_email_assets import (
            das_email_ensure_logo_attachment,
        )
        from odoo.addons.das_email_campaigns.hooks import _sync_mail_templates
        das_email_ensure_logo_attachment(env)
        _sync_mail_templates(env)
        _logger.info('DAS: logo y plantillas actualizados (18.0.1.4.2).')
    except Exception:
        _logger.exception('DAS: migración 18.0.1.4.2 — error actualizando logo/plantillas.')
