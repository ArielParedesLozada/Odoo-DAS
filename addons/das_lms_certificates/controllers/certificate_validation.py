# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

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
            
        pdf, _ = request.env.ref('das_lms_certificates.action_report_course_certificate').sudo()._render_qweb_pdf([enrollment.id])
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
            ('Content-Disposition', 'attachment; filename="Certificado_%s.pdf"' % channel_id),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)

