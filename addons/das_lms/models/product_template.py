# -*- coding: utf-8 -*-
from odoo import api, fields, models


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
