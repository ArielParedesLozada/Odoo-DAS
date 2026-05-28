# -*- coding: utf-8 -*-
from odoo import api, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _das_is_portal_student_user(self):
        """Usuario portal puro (estudiante): solo group_portal, sin acceso interno."""
        self.ensure_one()
        if self._is_public():
            return False
        if not self.has_group('base.group_portal'):
            return False
        # Personal interno (ventas, finanzas, coordinación, backend…) tiene group_user.
        if self.has_group('base.group_user'):
            return False
        return True

    def _das_email_preference_exempt_user(self):
        """Usuarios que no deben completar el formulario obligatorio de preferencias."""
        self.ensure_one()
        if self._is_public():
            return True
        if self._is_admin():
            return True
        return not self._das_is_portal_student_user()

    def _das_must_complete_email_preferences(self):
        """True si el estudiante portal debe completar el onboarding antes de continuar."""
        if not self:
            return False
        self.ensure_one()
        if self._das_email_preference_exempt_user():
            return False
        partner = self.partner_id
        if not partner:
            return False
        pref = self.env['das.email.preference'].sudo().search(
            [('partner_id', '=', partner.id)],
            limit=1,
        )
        return not pref or not pref.completed

    def action_view_das_email_preference(self):
        """Abre el registro de preferencias del usuario en backend."""
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id(
            'das_email_preferences.das_email_preference_action'
        )
        pref = self.env['das.email.preference'].sudo().search(
            [('partner_id', '=', self.partner_id.id)],
            limit=1,
        )
        if pref:
            action.update({
                'views': [(False, 'form')],
                'res_id': pref.id,
                'domain': [('id', '=', pref.id)],
            })
        else:
            action['domain'] = [('partner_id', '=', self.partner_id.id)]
        return action

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        Preference = self.env['das.email.preference'].sudo()
        for user in users:
            if user._das_email_preference_exempt_user():
                continue
            if user.partner_id:
                Preference._get_or_create_for_partner(user.partner_id)
        return users
