# -*- coding: utf-8 -*-
from odoo import fields, models


class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    das_lms_enrollment_ids = fields.One2many(
        'course.enrollment',
        'course_id',
        string='Seguimiento DAS LMS',
        readonly=True,
    )
