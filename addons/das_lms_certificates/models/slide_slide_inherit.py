# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


class SlideSlideInherit(models.Model):
    _inherit = "slide.slide"

    das_is_final_exam = fields.Boolean(
        string="Es Prueba Final",
        help="Si se marca, el resultado de esta certificación determinará si el estudiante aprueba o reprueba el curso para su certificado.",
        default=False,
    )

    das_is_satisfaction_survey = fields.Boolean(
        string="Es Encuesta de Satisfacción",
        help="Si se marca, completar esta encuesta desbloqueará la opción de descargar el certificado.",
        default=False,
    )

    def unlink(self):
        for slide in self:
            if slide.das_is_final_exam or slide.das_is_satisfaction_survey:
                enrollments = (
                    self.env["course.enrollment"]
                    .sudo()
                    .search([("course_id", "=", slide.channel_id.id)])
                )

                if slide.das_is_final_exam:
                    enrollments.write({"das_lms_final_status": "pending"})

                if slide.das_is_satisfaction_survey:
                    enrollments.write({"das_lms_survey_completed": False})

        return super().unlink()

    @api.constrains("channel_id", "das_is_final_exam", "das_is_satisfaction_survey")
    def _check_unique_academic_slides(self):
        for rec in self:
            if rec.das_is_final_exam:
                existing = self.search(
                    [
                        ("channel_id", "=", rec.channel_id.id),
                        ("das_is_final_exam", "=", True),
                        ("id", "!=", rec.id),
                    ],
                    limit=1,
                )
                if existing:
                    raise UserError("Ya existe un examen final en este curso.")

            if rec.das_is_satisfaction_survey:
                existing = self.search(
                    [
                        ("channel_id", "=", rec.channel_id.id),
                        ("das_is_satisfaction_survey", "=", True),
                        ("id", "!=", rec.id),
                    ],
                    limit=1,
                )
                if existing:
                    raise UserError(
                        "Ya existe una encuesta de satisfacción en este curso."
                    )
