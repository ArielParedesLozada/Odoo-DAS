# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


class SurveyUserInputInherit(models.Model):
    _inherit = "survey.user_input"

    channel_id = fields.Many2one(
        "slide.channel", string="Curso", compute="_compute_channel_id", store=True
    )

    is_satisfaction = fields.Boolean(
        string="Es Encuesta de Satisfacción", compute="_compute_channel_id", store=True
    )

    is_final_exam = fields.Boolean(compute="_compute_channel_id", store=True)
    survey_redirect_url = fields.Char(compute="_compute_redirect_url")

    def _compute_redirect_url(self):
        for rec in self:
            slide = self.env["slide.slide"].search(
                [
                    ("channel_id", "=", rec.channel_id.id),
                    ("das_is_satisfaction_survey", "=", True),
                ],
                limit=1,
            )

            rec.survey_redirect_url = (
                f"/slides/slide/{slide.id}?fullscreen=1" if slide else "/slides"
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
                rec.is_final_exam = slide.das_is_final_exam
            else:
                rec.channel_id = False
                rec.is_satisfaction = False

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)

        for rec in records:
            if not rec.partner_id or not rec.survey_id:
                continue

            slide = (
                self.env["slide.slide"]
                .sudo()
                .search([("survey_id", "=", rec.survey_id.id)], limit=1)
            )

            if not slide:
                continue

            enrollment = (
                self.env["course.enrollment"]
                .sudo()
                .search(
                    [
                        ("course_id", "=", slide.channel_id.id),
                        ("student_id", "=", rec.partner_id.id),
                    ],
                    limit=1,
                )
            )

            # 🔒 BLOQUEO REAL (NO CONTROLLER)
            if slide.das_is_satisfaction_survey:
                if not enrollment or enrollment.das_lms_final_status == "pending":
                    raise UserError(
                        "Debes completar el examen antes de iniciar la encuesta."
                    )

            if slide.das_is_final_exam:
                if not enrollment:
                    raise UserError("Debes estar inscrito en el curso.")

            # 🔥 EVITAR DUPLICADOS (CLAVE)
            # 🔒 BLOQUEO POR ENROLLMENT (RECOMENDADO)
            if slide.das_is_final_exam:
                if enrollment.das_lms_final_status != "pending":
                    raise UserError("Solo puedes realizar el examen final una vez.")

            if slide.das_is_satisfaction_survey:
                if enrollment.das_lms_survey_completed:
                    raise UserError("Ya has completado la encuesta de satisfacción.")
        return records
