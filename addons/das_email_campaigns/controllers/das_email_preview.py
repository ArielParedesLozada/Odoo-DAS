# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class DasEmailPreviewController(http.Controller):

    @http.route('/das_email/preview/list/<int:list_id>', type='http', auth='user', website=False)
    def preview_from_list(self, list_id, contact_id=None, **kwargs):
        mailing_list = request.env['mailing.list'].browse(list_id).exists()
        if not mailing_list:
            return request.not_found()
        contact = False
        if contact_id:
            contact = request.env['mailing.contact'].browse(int(contact_id)).exists()
        html = mailing_list._das_render_preview_html(contact=contact)
        return request.make_response(html, headers=[('Content-Type', 'text/html; charset=utf-8')])

    @http.route('/das_email/preview/mailing/<int:mailing_id>', type='http', auth='user', website=False)
    def preview_from_mailing(self, mailing_id, contact_id=None, **kwargs):
        mailing = request.env['mailing.mailing'].browse(mailing_id).exists()
        if not mailing:
            return request.not_found()
        contact = False
        if contact_id:
            contact = request.env['mailing.contact'].browse(int(contact_id)).exists()
        html = mailing._das_render_preview_html(contact=contact)
        return request.make_response(html, headers=[('Content-Type', 'text/html; charset=utf-8')])
