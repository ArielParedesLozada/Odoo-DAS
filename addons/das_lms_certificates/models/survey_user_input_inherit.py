# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.exceptions import UserError


class SurveyUserInputInherit(models.Model):
    _inherit = "survey.user_input"

    def write(self, vals):
        res = super(SurveyUserInputInherit, self).write(vals)
        if "state" in vals and vals["state"] == "done":
            for record in self:
                if not record.partner_id:
                    continue

                slide = (
                    self.env["slide.slide"]
                    .sudo()
                    .search([("survey_id", "=", record.survey_id.id)], limit=1)
                )

                if not slide:
                    continue

                enrollment = (
                    self.env["course.enrollment"]
                    .sudo()
                    .search(
                        [
                            ("course_id", "=", slide.channel_id.id),
                            ("student_id", "=", record.partner_id.id),
                        ],
                        limit=1,
                    )
                )

                if not enrollment:
                    continue

                # 🔒 EVITAR REPROCESAR
                if (
                    slide.das_is_final_exam
                    and enrollment.das_lms_final_status != "pending"
                ):
                    continue

                if (
                    slide.das_is_satisfaction_survey
                    and enrollment.das_lms_survey_completed
                ):
                    continue

                # ✅ PROCESAR
                if slide.das_is_final_exam:
                    enrollment.das_lms_final_status = (
                        "approved" if record.scoring_success else "failed"
                    )

                if slide.das_is_satisfaction_survey:
                    enrollment.das_lms_survey_completed = True
        return res
