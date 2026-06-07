# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SlideChannelInherit(models.Model):
    _inherit = "slide.channel"

    def action_generate_certification_flow(self):
        for record in self:
            # Check if exams already exist
            existing_exam = self.env["slide.slide"].search(
                [("channel_id", "=", record.id), ("das_is_final_exam", "=", True)],
                limit=1,
            )

            existing_survey = self.env["slide.slide"].search(
                [
                    ("channel_id", "=", record.id),
                    ("das_is_satisfaction_survey", "=", True),
                ],
                limit=1,
            )

            if existing_exam and existing_survey:
                raise UserError(
                    _("El flujo de certificación ya ha sido generado para este curso.")
                )

            # Create Final Exam Survey
            if not existing_exam:
                exam_survey = self.env["survey.survey"].create(
                    {
                        "title": f"Examen Final - {record.name}",
                        "scoring_type": "scoring_with_answers",
                        "certification": True,
                    }
                )

                # Question 1
                q1 = self.env["survey.question"].create(
                    {
                        "title": "¿Qué es Odoo?",
                        "survey_id": exam_survey.id,
                        "question_type": "simple_choice",
                    }
                )
                self.env["survey.question.answer"].create(
                    {
                        "value": "Un ERP",
                        "question_id": q1.id,
                        "is_correct": True,
                        "answer_score": 10,
                    }
                )
                self.env["survey.question.answer"].create(
                    {
                        "value": "Un CRM",
                        "question_id": q1.id,
                        "is_correct": False,
                        "answer_score": 0,
                    }
                )
                self.env["survey.question.answer"].create(
                    {
                        "value": "Una Base de Datos",
                        "question_id": q1.id,
                        "is_correct": False,
                        "answer_score": 0,
                    }
                )
                self.env["survey.question.answer"].create(
                    {
                        "value": "Un Sistema Operativo",
                        "question_id": q1.id,
                        "is_correct": False,
                        "answer_score": 0,
                    }
                )

                # Question 2
                q2 = self.env["survey.question"].create(
                    {
                        "title": "¿Qué módulo gestiona cursos?",
                        "survey_id": exam_survey.id,
                        "question_type": "simple_choice",
                    }
                )
                self.env["survey.question.answer"].create(
                    {
                        "value": "website_slides",
                        "question_id": q2.id,
                        "is_correct": True,
                        "answer_score": 10,
                    }
                )
                self.env["survey.question.answer"].create(
                    {
                        "value": "hr_recruitment",
                        "question_id": q2.id,
                        "is_correct": False,
                        "answer_score": 0,
                    }
                )
                self.env["survey.question.answer"].create(
                    {
                        "value": "sale_management",
                        "question_id": q2.id,
                        "is_correct": False,
                        "answer_score": 0,
                    }
                )
                self.env["survey.question.answer"].create(
                    {
                        "value": "website_blog",
                        "question_id": q2.id,
                        "is_correct": False,
                        "answer_score": 0,
                    }
                )

                # Question 3
                q3 = self.env["survey.question"].create(
                    {
                        "title": "¿Qué hace website_slides?",
                        "survey_id": exam_survey.id,
                        "question_type": "simple_choice",
                    }
                )
                self.env["survey.question.answer"].create(
                    {
                        "value": "Permite crear y gestionar eLearning",
                        "question_id": q3.id,
                        "is_correct": True,
                        "answer_score": 10,
                    }
                )
                self.env["survey.question.answer"].create(
                    {
                        "value": "Contabilidad avanzada",
                        "question_id": q3.id,
                        "is_correct": False,
                        "answer_score": 0,
                    }
                )
                self.env["survey.question.answer"].create(
                    {
                        "value": "Diseño de páginas web",
                        "question_id": q3.id,
                        "is_correct": False,
                        "answer_score": 0,
                    }
                )
                self.env["survey.question.answer"].create(
                    {
                        "value": "Gestión de inventario",
                        "question_id": q3.id,
                        "is_correct": False,
                        "answer_score": 0,
                    }
                )

                # Create Slide for Final Exam
                self.env["slide.slide"].create(
                    {
                        "name": f"Prueba Final - {record.name}",
                        "channel_id": record.id,
                        "slide_category": "certification",
                        "survey_id": exam_survey.id,
                        "is_published": True,
                        "das_is_final_exam": True,
                        "sequence": 100,
                    }
                )

            # Create Satisfaction Survey
            if not existing_survey:
                forced_survey_id = self.env.context.get("forced_survey_id")
                if forced_survey_id:
                    satisfaction_survey = self.env["survey.survey"].browse(
                        forced_survey_id
                    )
                else:
                    config = self.env["lms.satisfaction.survey"].search(
                        [("channel_id", "=", record.id)], limit=1
                    )
                    if config and config.template_id:
                        # 🔥 USAR PLANTILLA
                        template = config.template_id
                        satisfaction_survey = template.copy(
                            {
                                "title": f"{template.title} - {record.name}",
                            }
                        )

                    else:
                        # ⚠️ FALLBACK (tu lógica actual)
                        satisfaction_survey = self.env["survey.survey"].create(
                            {
                                "title": f"Encuesta de Satisfacción - {record.name}",
                                "scoring_type": "scoring_without_answers",
                                "scoring_success_min": 0.0,
                                "certification": True,
                            }
                        )

                        # Preguntas default
                        self.env["survey.question"].create(
                            {
                                "title": "¿Qué te pareció el curso?",
                                "survey_id": satisfaction_survey.id,
                                "question_type": "text_box",
                            }
                        )

                        qs2 = self.env["survey.question"].create(
                            {
                                "title": "¿Recomendarías este curso?",
                                "survey_id": satisfaction_survey.id,
                                "question_type": "simple_choice",
                            }
                        )
                        self.env["survey.question.answer"].create(
                            {"value": "Sí", "question_id": qs2.id}
                        )
                        self.env["survey.question.answer"].create(
                            {"value": "No", "question_id": qs2.id}
                        )

                # Create Slide for Satisfaction Survey
                self.env["slide.slide"].create(
                    {
                        "name": f"Encuesta de Satisfacción - {record.name}",
                        "channel_id": record.id,
                        "slide_category": "certification",
                        "survey_id": satisfaction_survey.id,
                        "is_published": True,
                        "das_is_satisfaction_survey": True,
                        "sequence": 200,
                    }
                )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Éxito",
                "message": "El flujo de certificación ha sido generado exitosamente. Revisa la pestaña de contenido del curso.",
                "type": "success",
                "sticky": False,
            },
        }
