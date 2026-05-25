# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    try:
        from odoo.addons.das_email_campaigns.hooks import _sync_mail_templates
        from odoo.addons.das_email_campaigns.models.das_email_assets import (
            das_email_ensure_logo_attachment,
        )
        das_email_ensure_logo_attachment(env)
        _sync_mail_templates(env)
        Mailing = env['mailing.mailing'].sudo()
        for mailing in Mailing.search([('body_html', 'ilike', 'Academia Virtual DAS')]):
            body = Mailing._das_finalize_body_html(mailing.body_html)
            if body != mailing.body_html:
                mailing.with_context(das_keep_inline_logo=True).write({'body_html': body})
        _logger.info('DAS: logo CID en campañas (18.0.1.4.4).')
    except Exception:
        _logger.exception('DAS: migración 18.0.1.4.4 fallida.')
