# -*- coding: utf-8 -*-
import uuid
import base64
from markupsafe import Markup
from odoo import models, fields, api

class CourseEnrollmentInherit(models.Model):
    _inherit = 'course.enrollment'

    das_lms_final_status = fields.Selection([
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('failed', 'Reprobado')
    ], string='Estado Final de Certificación', default='pending')

    das_lms_survey_completed = fields.Boolean(
        string='Encuesta de Satisfacción Completada',
        default=False
    )

    das_lms_certificate_token = fields.Char(
        string='Token de Certificado',
        default=lambda self: str(uuid.uuid4()),
        readonly=True,
        copy=False,
        index=True
    )
    
    das_lms_certificate_date = fields.Date(
        string="Fecha del Certificado",
        compute="_compute_certificate_date",
        store=True
    )
    
    das_lms_certificate_qr = fields.Binary(
        string="Código QR",
        compute="_compute_certificate_qr"
    )

    @api.depends('das_lms_certificate_token')
    def _compute_certificate_qr(self):
        for rec in self:
            if rec.das_lms_certificate_token:
                url = "%s/validar/certificado/%s" % (rec.get_base_url(), rec.das_lms_certificate_token)
                try:
                    barcode = rec.env['ir.actions.report'].barcode('QR', url, width=100, height=100)
                    rec.das_lms_certificate_qr = base64.b64encode(barcode)
                except Exception:
                    rec.das_lms_certificate_qr = False
            else:
                rec.das_lms_certificate_qr = False

    def das_lms_get_html_text(self, text_id):
        texts = {
            'aprobacion': Markup('Aprobaci&oacute;n'),
            'participacion': Markup('Participaci&oacute;n'),
            'capacitacion': Markup('capacitaci&oacute;n'),
            'duracion': Markup('duraci&oacute;n'),
            'academico': Markup('Acad&eacute;mico'),
            'codigo': Markup('C&oacute;digo:'),
        }
        return texts.get(text_id, '')

    @api.depends('das_lms_final_status')
    def _compute_certificate_date(self):
        for rec in self:
            if rec.das_lms_final_status in ['approved', 'failed'] and not rec.das_lms_certificate_date:
                rec.das_lms_certificate_date = fields.Date.today()
            elif rec.das_lms_final_status == 'pending':
                rec.das_lms_certificate_date = False

    def action_generate_certificate(self):
        self.ensure_one()
        if self.das_lms_final_status == 'pending':
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Atención',
                    'message': 'El curso debe estar Aprobado o Reprobado para generar un certificado.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        if not self.das_lms_certificate_token:
            self.das_lms_certificate_token = str(uuid.uuid4())

        return self.env.ref('das_lms_certificates.action_report_course_certificate').report_action(self)
