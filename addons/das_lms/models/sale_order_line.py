# -*- coding: utf-8 -*-
from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines.order_id._das_lms_validate_course_cart_rules()
        return lines

    def write(self, vals):
        res = super().write(vals)
        self.order_id._das_lms_validate_course_cart_rules()
        return res
