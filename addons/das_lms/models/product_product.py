# -*- coding: utf-8 -*-
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _is_add_to_cart_allowed(self):
        try:
            res = super()._is_add_to_cart_allowed()
        except Exception:
            raise
        try:
            if not res:
                return False
            if self.env.context.get('das_lms_bypass_cart_lms_check'):
                return True
            tmpl = self.product_tmpl_id
            if not tmpl:
                return res
            if not tmpl._das_lms_get_related_channel(product_product=self):
                return res
            user = self.env.user
            if user._is_public():
                return tmpl._das_lms_course_sale_blocked() is False
            partner = user.partner_id
            if not partner:
                return res
            msg = tmpl._das_lms_cart_validation_message(partner, new_qty=1, product_product=self)
            return not bool(msg)
        except Exception:
            _logger.exception(
                'DAS LMS: _is_add_to_cart_allowed variante id=%s; se permite comportamiento estándar previo.',
                self.id,
            )
            return res
