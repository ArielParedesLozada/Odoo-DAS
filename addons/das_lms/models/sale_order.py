# -*- coding: utf-8 -*-
from odoo import _, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _action_confirm(self):
        """No inscribir en eLearning al confirmar (website_sale_slides); solo al validar factura."""
        return super(
            SaleOrder,
            self.with_context(das_lms_skip_slide_channel_auto_enroll=True),
        )._action_confirm()

    def _das_lms_get_lms_sale_lines(self):
        """Líneas cuyo producto resuelve un slide.channel vía vínculo estructurado DAS."""
        self.ensure_one()
        lines = self.order_line.filtered(lambda l: not l.display_type and l.product_id)
        return lines.filtered(
            lambda l: bool(
                l.product_id.product_tmpl_id._das_lms_get_related_channel(product_product=l.product_id)
            )
        )

    def _das_lms_validate_course_cart_rules(self):
        """Un solo curso por pedido y cantidad 1 (reemplaza automatización Studio archivada)."""
        for order in self:
            if order.state not in ('draft', 'sent'):
                continue
            lms_lines = order._das_lms_get_lms_sale_lines()
            if len(lms_lines) > 1:
                raise UserError(_('Solo puede incluir un curso por pedido.'))
            for line in lms_lines:
                if line.product_uom_qty > 1:
                    raise UserError(_('Solo puede comprar una unidad de este curso.'))

    def write(self, vals):
        res = super().write(vals)
        if vals.get('partner_id'):
            self.filtered(lambda o: o.state == 'draft')._das_lms_remove_invalid_lms_lines()
        return res

    def _das_lms_remove_invalid_lms_lines(self):
        """Quita líneas de cursos LMS que ya no pueden venderse al partner (inscrito o curso cerrado)."""
        for order in self:
            partner = order.partner_id
            if not partner:
                continue
            bad = order.order_line.filtered(
                lambda line: bool(
                    line.product_template_id._das_lms_cart_validation_message(
                        partner,
                        new_qty=max(1, int(line.product_uom_qty or 1)),
                    )
                )
            )
            if bad:
                bad.unlink()

    def _verify_updated_quantity(self, order_line, product_id, new_qty, **kwargs):
        new_qty, warning = super()._verify_updated_quantity(order_line, product_id, new_qty, **kwargs)
        if new_qty <= 0:
            return new_qty, warning
        product = self.env['product.product'].browse(product_id).exists()
        if not product:
            return new_qty, warning
        partner = self.partner_id
        if not partner:
            try:
                from odoo.http import request

                if request and getattr(request, 'env', None):
                    usr = request.env.user
                    if usr and not usr._is_public():
                        partner = usr.partner_id
            except RuntimeError:
                partner = False
        msg = product.product_tmpl_id._das_lms_cart_validation_message(partner, new_qty=int(new_qty))
        if msg:
            raise UserError(msg)
        self._das_lms_validate_course_cart_rules()
        return new_qty, warning

    def action_confirm(self):
        for order in self:
            order._das_lms_validate_course_cart_rules()
            partner = order.partner_id
            if not partner:
                continue
            for line in order.order_line:
                msg = line.product_template_id._das_lms_cart_validation_message(
                    partner,
                    new_qty=max(1, int(line.product_uom_qty or 1)),
                )
                if msg:
                    raise UserError(msg)
        return super().action_confirm()
