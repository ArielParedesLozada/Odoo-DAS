# -*- coding: utf-8 -*-
from odoo import models


class DasEmailPreference(models.Model):
    _inherit = 'das.email.preference'

    def action_mark_completed(self, ip_address=None):
        res = super().action_mark_completed(ip_address=ip_address)
        for pref in self:
            if pref.partner_id:
                pref.partner_id._das_sync_email_marketing_segments()
        return res
