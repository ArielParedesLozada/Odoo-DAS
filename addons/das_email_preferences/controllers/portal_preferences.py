# -*- coding: utf-8 -*-
import logging

from odoo import _, http
from odoo.exceptions import UserError, ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)

# Niveles expuestos en el portal (sin selector de frecuencia: solo email).
PORTAL_EXPERIENCE_CODES = ('beginner', 'intermediate', 'advanced', 'expert')


class DasEmailPreferencesPortal(http.Controller):

    def _get_client_ip(self):
        httprequest = request.httprequest
        forwarded = httprequest.headers.get('X-Forwarded-For')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return httprequest.remote_addr

    def _form_getlist(self, key):
        """Lista de valores POST (checkboxes múltiples). Compatible dict Odoo y Werkzeug."""
        form = getattr(request.httprequest, 'form', None)
        if form is not None and hasattr(form, 'getlist'):
            return form.getlist(key) or []
        params = request.params
        if hasattr(params, 'getlist'):
            return params.getlist(key) or []
        raw = params.get(key)
        if raw is None:
            return []
        if isinstance(raw, (list, tuple)):
            return list(raw)
        return [raw]

    def _form_get(self, key, default=None):
        form = getattr(request.httprequest, 'form', None)
        if form is not None and key in form:
            return form.get(key, default)
        return request.params.get(key, default)

    def _form_bool(self, key):
        val = self._form_get(key)
        return val in ('1', 'on', 'true', 'True', True, 1)

    def _parse_int_list(self, key):
        result = []
        for raw in self._form_getlist(key):
            try:
                result.append(int(raw))
            except (TypeError, ValueError):
                continue
        return result

    def _parse_form_values(self):
        return {
            'interest_ids': self._parse_int_list('interest_ids'),
            'course_category_ids': self._parse_int_list('course_category_ids'),
            'birthday': self._form_get('birthday') or False,
            'experience_level': self._form_get('experience_level') or False,
            'terms_accepted': self._form_bool('terms_accepted'),
            'privacy_accepted': self._form_bool('privacy_accepted'),
        }

    def _selection_subset(self, field, allowed_codes):
        return [(code, label) for code, label in field.selection if code in allowed_codes]

    def _preferences_form_values(self, partner, *, onboarding=False, error=None, form_values=None):
        Preference = request.env['das.email.preference'].sudo()
        pref = Preference._get_or_create_for_partner(partner, force_create=True)
        form_values = form_values or {}
        return {
            'page_name': 'email_preferences',
            'partner': partner,
            'preference': pref,
            'interests': request.env['das.email.interest'].sudo().search(
                [('active', '=', True)], order='sequence, name',
            ),
            'course_categories': request.env['das.email.course.category'].sudo().search(
                [('active', '=', True)], order='sequence, name',
            ),
            'experience_levels': self._selection_subset(
                pref._fields['experience_level'], PORTAL_EXPERIENCE_CODES,
            ),
            'onboarding': onboarding,
            'error_message': error,
            'redirect_url': self._form_get('redirect') or request.params.get('redirect') or '/my',
            'form_values': form_values,
        }

    @http.route(
        ['/my/email-preferences', '/my/email-preferences/edit'],
        type='http',
        auth='user',
        website=True,
        sitemap=False,
    )
    def portal_email_preferences(self, **post):
        user = request.env.user
        if not user._das_is_portal_student_user():
            if user.has_group('base.group_portal'):
                return request.redirect('/my')
            return request.redirect('/web')
        partner = user.partner_id
        onboarding = user._das_must_complete_email_preferences()
        return request.render(
            'das_email_preferences.portal_email_preferences_form',
            self._preferences_form_values(partner, onboarding=onboarding),
        )

    @http.route(
        '/my/email-preferences/submit',
        type='http',
        auth='user',
        website=True,
        methods=['POST'],
        csrf=True,
        sitemap=False,
    )
    def portal_email_preferences_submit(self, **post):
        user = request.env.user
        if not user._das_is_portal_student_user():
            if user.has_group('base.group_portal'):
                return request.redirect('/my')
            return request.redirect('/web')
        partner = user.partner_id
        Preference = request.env['das.email.preference'].sudo()
        redirect_url = self._form_get('redirect') or '/my'
        if (
            redirect_url.startswith('/web')
            and request.env.user.has_group('base.group_portal')
        ):
            redirect_url = '/my'
        form_values = self._parse_form_values()
        try:
            Preference.submit_from_portal(
                partner,
                form_values,
                ip_address=self._get_client_ip(),
            )
        except (ValidationError, UserError) as err:
            message = err.args[0] if err.args else str(err)
            return request.render(
                'das_email_preferences.portal_email_preferences_form',
                self._preferences_form_values(
                    partner,
                    onboarding=request.env.user._das_must_complete_email_preferences(),
                    error=message,
                    form_values=form_values,
                ),
            )
        except Exception:
            _logger.exception('DAS email preferences: error al guardar preferencias.')
            return request.render(
                'das_email_preferences.portal_email_preferences_form',
                self._preferences_form_values(
                    partner,
                    onboarding=request.env.user._das_must_complete_email_preferences(),
                    error=_('No se pudieron guardar las preferencias. Inténtalo de nuevo.'),
                    form_values=form_values,
                ),
            )
        return request.redirect(redirect_url)
