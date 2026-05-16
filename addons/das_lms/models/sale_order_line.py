# -*- coding: utf-8 -*-
from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _das_lms_is_course_line(self):
        """Línea de pedido cuyo producto está ligado a un curso eLearning DAS."""
        self.ensure_one()
        if not self.product_id:
            return False
        return bool(
            self.product_id.product_tmpl_id._das_lms_get_related_channel(product_product=self.product_id)
        )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines.order_id._das_lms_validate_course_cart_rules()
        return lines

    def write(self, vals):
        res = super().write(vals)
        self.order_id._das_lms_validate_course_cart_rules()
        return res
