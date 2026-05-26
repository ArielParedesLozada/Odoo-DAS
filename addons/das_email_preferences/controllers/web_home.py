# -*- coding: utf-8 -*-
import werkzeug

from odoo.addons.web.controllers.home import Home
from odoo.http import request


class DasEmailPreferencesHome(Home):

    def _login_redirect(self, uid, redirect=None):
        user = request.env['res.users'].sudo().browse(uid)
        if user.exists() and user._das_must_complete_email_preferences():
            target = redirect if redirect and not redirect.startswith('/web') else '/my'
            return '/my/email-preferences?redirect=' + werkzeug.urls.url_quote(target)
        return super()._login_redirect(uid, redirect=redirect)
