# -*- coding: utf-8 -*-
from odoo import api, models


class SlideChannelPartner(models.Model):
    _inherit = 'slide.channel.partner'

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._das_lms_sync_enrollment_mirror()
        return records

    def write(self, vals):
        res = super().write(vals)
        if any(
            k in vals
            for k in ('completion', 'partner_id', 'channel_id', 'active', 'member_status')
        ):
            self._das_lms_sync_enrollment_mirror()
        return res

    def _das_lms_sync_enrollment_mirror(self):
        Enrollment = self.env['course.enrollment'].sudo()
        for scp in self:
            if not scp.partner_id or not scp.channel_id:
                continue
            existing = Enrollment.search([('channel_partner_id', '=', scp.id)], limit=1)
            if existing:
                existing._sync_fields_from_channel_partner()
            else:
                Enrollment.create(
                    self.env['course.enrollment']._prepare_vals_from_channel_partner(scp)
                )
