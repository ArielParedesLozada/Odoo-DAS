# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    try:
        from odoo.addons.das_email_campaigns.models.das_email_assets import (
            das_email_refresh_logo_data_uri,
        )
        from odoo.addons.das_email_campaigns.hooks import _sync_mail_templates
        das_email_refresh_logo_data_uri(env)
        _sync_mail_templates(env)
        _logger.info('DAS: plantillas QWeb + logo embebido (18.0.1.4.3).')
    except Exception:
        _logger.exception('DAS: migración 18.0.1.4.3 fallida.')
