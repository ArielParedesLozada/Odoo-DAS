# -*- coding: utf-8 -*-
import werkzeug

from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    # Rutas exentas del bloqueo de onboarding (prefijos).
    _DAS_PREF_ALLOWED_PREFIXES = (
        '/my/email-preferences',
        '/web/login',
        '/web/session',
        '/web/database',
        '/website/translations',
        '/web/content',
        '/web/assets',
        '/web/static',
        '/bus/',
        '/longpolling',
        '/mail/',
        '/json/',
        '/websocket',
    )

    @classmethod
    def _das_is_preferences_allowed_path(cls, path):
        if not path:
            return True
        for prefix in cls._DAS_PREF_ALLOWED_PREFIXES:
            if path.startswith(prefix):
                return True
        return False

    @classmethod
    def _dispatch(cls, endpoint):
        if (
            request
            and request.session.uid
            and request.httprequest.method == 'GET'
        ):
            path = request.httprequest.path or ''
            if not cls._das_is_preferences_allowed_path(path):
                user = request.env.user
                if not user or len(user) != 1 or user._is_public():
                    return super()._dispatch(endpoint)
                if user._das_must_complete_email_preferences():
                    redirect_url = '/my/email-preferences'
                    if path and path not in ('/', '/my', '/my/home'):
                        redirect_url += '?redirect=' + werkzeug.urls.url_quote(path)
                    return request.redirect(redirect_url)
        return super()._dispatch(endpoint)
