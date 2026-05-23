# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SurveyUserInputInherit(models.Model):
    _inherit = "survey.user_input"

    channel_id = fields.Many2one(
        "slide.channel", string="Curso", compute="_compute_channel_id", store=True
    )

    is_satisfaction = fields.Boolean(
        string="Es Encuesta de Satisfacción", compute="_compute_channel_id", store=True
    )

    @api.depends("survey_id")
    def _compute_channel_id(self):
        for rec in self:
            slide = (
                self.env["slide.slide"]
                .sudo()
                .search([("survey_id", "=", rec.survey_id.id)], limit=1)
            )

            if slide:
                rec.channel_id = slide.channel_id.id
                rec.is_satisfaction = slide.das_is_satisfaction_survey
            else:
                rec.channel_id = False
                rec.is_satisfaction = False
