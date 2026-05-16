# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    das_lms_slide_channel_id = fields.Many2one(
        'slide.channel',
        string='Curso eLearning',
        compute='_compute_das_lms_slide_channel',
        store=False,
    )

    @api.depends('product_variant_ids')
    def _compute_das_lms_slide_channel(self):
        SlideChannel = self.env['slide.channel'].sudo()
        for template in self:
            channel = SlideChannel.search([
                ('product_id', 'in', template.product_variant_ids.ids),
            ], limit=1)
            template.das_lms_slide_channel_id = channel

    def _das_lms_linked_slide_channel(self):
        self.ensure_one()
        return self.env['slide.channel'].sudo().search([
            ('product_id', 'in', self.product_variant_ids.ids),
        ], limit=1)

    def _das_lms_is_enrolled_in_course(self):
        self.ensure_one()
        channel = self._das_lms_linked_slide_channel()
        if not channel or self.env.user._is_public():
            return False
        partner = self.env.user.partner_id
        return bool(self.env['slide.channel.partner'].sudo().search([
            ('channel_id', '=', channel.id),
            ('partner_id', '=', partner.id),
            ('active', '=', True),
        ], limit=1))

    def _das_lms_course_website_url(self):
        self.ensure_one()
        channel = self._das_lms_linked_slide_channel()
        return channel.website_url if channel else '#'

    def _das_lms_course_sale_blocked(self):
        """True si el curso vinculado está finalizado académicamente (no nuevas inscripciones)."""
        self.ensure_one()
        channel = self._das_lms_linked_slide_channel()
        return bool(channel and channel.das_academic_status == 'finalizado')

    def _das_lms_course_sale_notice_html(self):
        """Texto informativo para la ficha del producto (venta / anticipo)."""
        self.ensure_one()
        channel = self._das_lms_linked_slide_channel()
        if not channel:
            return ''
        if channel.das_academic_status == 'finalizado':
            return _('Este curso ya finalizó y no acepta nuevas inscripciones.')
        if channel.das_academic_status == 'proximo' and channel.das_start_date:
            ds = channel.das_start_date.strftime('%d/%m/%Y')
            return _('El curso inicia el %s. Puede inscribirse anticipadamente.') % ds
        return ''
