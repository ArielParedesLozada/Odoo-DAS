# -*- coding: utf-8 -*-
from odoo import models, api

class SurveyUserInputInherit(models.Model):
    _inherit = 'survey.user_input'

    def write(self, vals):
        res = super(SurveyUserInputInherit, self).write(vals)
        if 'state' in vals and vals['state'] == 'done':
            for record in self:
                if record.partner_id:
                    # Find the corresponding slide for this survey
                    slide = self.env['slide.slide'].sudo().search([
                        ('survey_id', '=', record.survey_id.id)
                    ], limit=1)
                    
                    if slide:
                        # Asegurar que solo procesa slides válidos del flujo
                        if not (slide.das_is_final_exam or slide.das_is_satisfaction_survey):
                            continue

                        # Find enrollment
                        enrollment = self.env['course.enrollment'].sudo().search([
                            ('course_id', '=', slide.channel_id.id),
                            ('student_id', '=', record.partner_id.id)
                        ], limit=1)
                        
                        if enrollment:
                            # Check if it's the final exam
                            if slide.das_is_final_exam:
                                if record.scoring_success:
                                    enrollment.das_lms_final_status = 'approved'
                                else:
                                    enrollment.das_lms_final_status = 'failed'
                            
                            # Check if it's the satisfaction survey
                            if slide.das_is_satisfaction_survey:
                                enrollment.das_lms_survey_completed = True
        return res
