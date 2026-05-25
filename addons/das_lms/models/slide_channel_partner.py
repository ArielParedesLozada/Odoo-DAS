# -*- coding: utf-8 -*-
from odoo import _, api, models
from odoo.exceptions import UserError


class SlideChannelPartner(models.Model):
    _inherit = 'slide.channel.partner'

    @api.model_create_multi
    def create(self, vals_list):
        if (
            not self.env.context.get('das_lms_bypass_academic_close')
            and self.env.context.get('das_lms_allow_structured_enroll')
        ):
            for vals in vals_list:
                    cid = vals.get('channel_id')
                    if not cid:
                        continue
                    channel = self.env['slide.channel'].browse(cid).exists()
                    if not channel:
                        continue
                    if channel.das_academic_status == 'finalizado':
                        raise UserError(channel._das_lms_registration_closed_message())
                    if not channel._das_lms_is_registration_open():
                        raise UserError(channel._das_lms_registration_closed_message())
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
            if not scp.partner_id._das_lms_is_academic_student_partner():
                if existing:
                    existing.unlink()
                continue
            if existing:
                existing._sync_fields_from_channel_partner()
            else:
                Enrollment.create(
                    self.env['course.enrollment']._prepare_vals_from_channel_partner(scp)
                )
