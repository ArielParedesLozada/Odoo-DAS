# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError
import odoo.addons.survey.controllers.main as survey_main

class CertificateValidationController(http.Controller):

    @http.route(['/validar/certificado/<string:token>'], type='http', auth="public", website=True)
    def validate_certificate(self, token, **kwargs):
        enrollment = request.env['course.enrollment'].sudo().search([('das_lms_certificate_token', '=', token)], limit=1)
        
        if not enrollment:
            return request.render('das_lms_certificates.certificate_invalid_page', {})
            
        return request.render('das_lms_certificates.certificate_valid_page', {
            'enrollment': enrollment,
        })

    @http.route(['/my/certificate/<int:channel_id>'], type='http', auth="user", website=True)
    def download_certificate(self, channel_id, **kwargs):
        enrollment = request.env['course.enrollment'].sudo().search([
            ('course_id', '=', channel_id),
            ('student_id', '=', request.env.user.partner_id.id)
        ], limit=1)
        
        if not enrollment or enrollment.das_lms_final_status == 'pending':
            return request.redirect('/slides')
            
        pdf, _ = request.env['ir.actions.report'].sudo()._render_qweb_pdf('das_lms_certificates.action_report_course_certificate', [enrollment.id])
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
            ('Content-Disposition', 'attachment; filename="Certificado_%s.pdf"' % channel_id),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)


class SurveyInherit(survey_main.Survey):
    
    @http.route(['/survey/<int:survey_id>/get_certification'], type='http', auth='user', methods=['GET'], website=True)
    def survey_get_certification(self, survey_id, **kwargs):
        survey = request.env['survey.survey'].sudo().search([
            ('id', '=', int(survey_id)),
            ('certification', '=', True)
        ])
        if not survey:
            return request.redirect("/")

        # Grab the latest attempt for this survey by the current user
        attempt = request.env['survey.user_input'].sudo().search([
            ('partner_id', '=', request.env.user.partner_id.id),
            ('survey_id', '=', int(survey_id)),
            ('state', '=', 'done')
        ], order='create_date desc', limit=1)
        
        # Reliably find the slide associated with this survey
        slide = request.env['slide.slide'].sudo().search([
            ('survey_id', '=', int(survey_id))
        ], limit=1)

        # If we have an attempt and it's either our "Examen Final" or "Encuesta de Satisfacción" slide
        if attempt and slide and (slide.das_is_final_exam or slide.das_is_satisfaction_survey):
            enrollment = request.env['course.enrollment'].sudo().search([
                ('course_id', '=', slide.channel_id.id),
                ('student_id', '=', request.env.user.partner_id.id)
            ], limit=1)
            
            # Check if they have actually completed the final exam (status is not pending)
            if enrollment and enrollment.das_lms_final_status != 'pending':
                # Intercept! Generate OUR custom PDF
                pdf, _ = request.env['ir.actions.report'].sudo()._render_qweb_pdf('das_lms_certificates.action_report_course_certificate', [enrollment.id])
                pdfhttpheaders = [
                    ('Content-Type', 'application/pdf'), 
                    ('Content-Length', len(pdf)), 
                    ('Content-Disposition', 'attachment; filename="Certificado_%s.pdf"' % enrollment.course_id.name)
                ]
                return request.make_response(pdf, headers=pdfhttpheaders)

        # If it is NOT our Examen Final, let Odoo do its normal native thing
        return super(SurveyInherit, self).survey_get_certification(survey_id, **kwargs)

    @http.route(['/survey/start/<string:survey_token>'], type='http', auth='public', website=True)
    def survey_start(self, survey_token, answer_token=None, email=False, **post):
        survey = request.env['survey.survey'].sudo().search([('access_token', '=', survey_token)], limit=1)
        if survey:
            # Check if this survey is tied to a satisfaction survey slide
            slide = request.env['slide.slide'].sudo().search([
                ('survey_id', '=', survey.id),
                ('das_is_satisfaction_survey', '=', True)
            ], limit=1)
            
            if slide and not request.env.user._is_public():
                enrollment = request.env['course.enrollment'].sudo().search([
                    ('course_id', '=', slide.channel_id.id),
                    ('student_id', '=', request.env.user.partner_id.id)
                ], limit=1)
                
                if not enrollment or enrollment.das_lms_final_status != 'approved':
                    # Raise UserError or redirect with a warning (Redirection is safer for UX)
                    # Redirecting to the slide channel page with a fragment or just a simple alert page
                    return request.render('http_routing.403', {
                        'error_message': _('Acceso Denegado: Debe aprobar el examen final antes de acceder a la encuesta de satisfacción.')
                    })
        
        return super(SurveyInherit, self).survey_start(survey_token, answer_token, email, **post)
