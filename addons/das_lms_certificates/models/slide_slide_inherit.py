# -*- coding: utf-8 -*-
from odoo import models, fields

class SlideSlideInherit(models.Model):
    _inherit = 'slide.slide'

    das_is_final_exam = fields.Boolean(
        string='Es Prueba Final',
        help='Si se marca, el resultado de esta certificación determinará si el estudiante aprueba o reprueba el curso para su certificado.',
        default=False
    )
    
    das_is_satisfaction_survey = fields.Boolean(
        string='Es Encuesta de Satisfacción',
        help='Si se marca, completar esta encuesta desbloqueará la opción de descargar el certificado.',
        default=False
    )
