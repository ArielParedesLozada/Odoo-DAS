# -*- coding: utf-8 -*-
from odoo import fields, models


class DasEmailCourseCategory(models.Model):
    _name = 'das.email.course.category'
    _description = 'Categoría de curso preferida (Email Marketing)'
    _order = 'sequence, name'

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
