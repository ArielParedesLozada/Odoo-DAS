# -*- coding: utf-8 -*-
from odoo import api, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _das_email_preference_exempt_user(self, user=None):
        """Usuarios que no deben completar el formulario de preferencias."""
        user = user or self.env.user
        if not user or user._is_public():
            return True
        if user._is_admin():
            return True
        return False

    def _das_must_complete_email_preferences(self):
        """True si el usuario debe completar el formulario antes de continuar."""
        if not self:
            return False
        self.ensure_one()
        if self._das_email_preference_exempt_user(self):
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
            if user._das_email_preference_exempt_user(user):
                continue
            if user.partner_id:
                Preference._get_or_create_for_partner(user.partner_id)
        return users
