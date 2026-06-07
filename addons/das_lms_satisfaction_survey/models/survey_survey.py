# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SurveySurvey(models.Model):
    _inherit = "survey.survey"

    is_satisfaction = fields.Boolean(string="Es plantilla de satisfacción")
