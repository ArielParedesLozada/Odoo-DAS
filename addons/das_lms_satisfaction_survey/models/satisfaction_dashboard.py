# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SatisfactionDashboard(models.Model):
    _name = "lms.satisfaction.dashboard"
    _description = "Dashboard de Satisfacción"
    _auto = False  # No tabla real

    course_id = fields.Many2one("slide.channel", string="Curso")
    total_responses = fields.Integer(string="Total Respuestas")
    recommendation_yes = fields.Integer(string="Recomiendan")
    recommendation_no = fields.Integer(string="No Recomiendan")
    avg_score = fields.Float(string="Promedio Satisfacción")

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW lms_satisfaction_dashboard AS (
                SELECT
                    MIN(sui.id) as id,
                    ss.channel_id as course_id,
                    COUNT(sui.id) as total_responses,

                    SUM(CASE 
                        WHEN qa.value->>'es_ES' = 'Sí' THEN 1 
                        ELSE 0 
                    END) as recommendation_yes,

                    SUM(CASE 
                        WHEN qa.value->>'es_ES' = 'No' THEN 1 
                        ELSE 0 
                    END) as recommendation_no,

                    AVG(CASE 
                        WHEN qa.value->>'es_ES' = 'Excelente' THEN 4
                        WHEN qa.value->>'es_ES' = 'Bueno' THEN 3
                        WHEN qa.value->>'es_ES' = 'Regular' THEN 2
                        WHEN qa.value->>'es_ES' = 'Malo' THEN 1
                        ELSE NULL
                    END) as avg_score

                FROM survey_user_input sui
                LEFT JOIN survey_user_input_line suil ON suil.user_input_id = sui.id
                LEFT JOIN survey_question_answer qa ON qa.id = suil.suggested_answer_id
                LEFT JOIN slide_slide ss ON ss.survey_id = sui.survey_id

                WHERE sui.state = 'done'
                AND ss.das_is_satisfaction_survey = TRUE

                GROUP BY ss.channel_id
            )
        """)
