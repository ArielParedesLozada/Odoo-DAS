# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    das_lms_enrollment_ids = fields.One2many(
        'course.enrollment',
        'course_id',
        string='Seguimiento DAS LMS',
        readonly=True,
    )

    @api.model
    def _das_lms_portal_can_study_channel(self, channel):
        """Acceso a contenido eLearning para el usuario actual (inscrito o invitación pendiente)."""
        if not channel:
            return False
        channel.ensure_one()
        user = channel.env.user
        if user._is_public():
            return False
        return bool(channel.is_member or channel.is_member_invited)
