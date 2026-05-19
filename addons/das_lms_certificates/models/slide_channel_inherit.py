# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SlideChannelInherit(models.Model):
    _inherit = 'slide.channel'

    def action_generate_certification_flow(self):
        for record in self:
            # Check if exams already exist
            existing_exam = self.env['slide.slide'].search([
                ('channel_id', '=', record.id),
                ('das_is_final_exam', '=', True)
            ], limit=1)
            
            existing_survey = self.env['slide.slide'].search([
                ('channel_id', '=', record.id),
                ('das_is_satisfaction_survey', '=', True)
            ], limit=1)
            
            if existing_exam and existing_survey:
                raise UserError(_('El flujo de certificación ya ha sido generado para este curso.'))

            # Create Final Exam Survey
            if not existing_exam:
                exam_survey = self.env['survey.survey'].create({
                    'title': f'Examen Final - {record.name}',
                    'scoring_type': 'scoring_with_answers',
                })
                # Add a dummy question so it can be scored
                self.env['survey.question'].create({
                    'title': 'Pregunta de Prueba (Reemplazar con la pregunta real)',
                    'survey_id': exam_survey.id,
                    'question_type': 'simple_choice',
                })
                
                # Create Slide for Final Exam
                self.env['slide.slide'].create({
                    'name': f'Prueba Final - {record.name}',
                    'channel_id': record.id,
                    'slide_category': 'certification',
                    'survey_id': exam_survey.id,
                    'is_published': True,
                    'das_is_final_exam': True,
                })

            # Create Satisfaction Survey
            if not existing_survey:
                satisfaction_survey = self.env['survey.survey'].create({
                    'title': f'Encuesta de Satisfacción - {record.name}',
                    'scoring_type': 'scoring_without_answers',
                    'scoring_success_min': 0.0,
                    'certification': True,
                })
                # Add a dummy question
                self.env['survey.question'].create({
                    'title': '¿Qué te pareció el curso? (Reemplazar con la pregunta real)',
                    'survey_id': satisfaction_survey.id,
                    'question_type': 'text_box',
                })
                
                # Create Slide for Satisfaction Survey
                self.env['slide.slide'].create({
                    'name': f'Encuesta de Satisfacción - {record.name}',
                    'channel_id': record.id,
                    'slide_category': 'certification',
                    'survey_id': satisfaction_survey.id,
                    'is_published': True,
                    'das_is_satisfaction_survey': True,
                })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Éxito',
                    'message': 'El flujo de certificación ha sido generado exitosamente. Revisa la pestaña de contenido del curso.',
                    'type': 'success',
                    'sticky': False,
                }
            }
