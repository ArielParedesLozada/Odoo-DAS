# -*- coding: utf-8 -*-
from odoo import _, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _cart_update(self, product_id, line_id=None, add_qty=0, set_qty=0, **kwargs):
        """Propaga avisos del carrito (p. ej. cantidad LMS forzada a 1) a ``shop_warning`` en la página."""
        res = super()._cart_update(
            product_id=product_id,
            line_id=line_id,
            add_qty=add_qty,
            set_qty=set_qty,
            **kwargs,
        )
        warn = res.get('warning')
        if warn:
            prev = (self.shop_warning or '').strip()
            merged = '\n'.join(x for x in (prev, warn) if x)
            self.write({'shop_warning': merged})
        return res

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

    def _das_lms_enroll_partner_from_order(self, partner=None):
        """Inscribe al partner en cada curso LMS del pedido (idempotente)."""
        for order in self:
            partner = partner or order.partner_id
            if not partner:
                continue
            channels_done = set()
            for line in order._das_lms_get_lms_sale_lines():
                channel = line.product_id.product_tmpl_id._das_lms_get_related_channel(
                    product_product=line.product_id
                )
                if not channel or channel.id in channels_done:
                    continue
                channels_done.add(channel.id)
                channel._das_lms_enroll_partner(partner)

    def _das_lms_payment_confirmation_enrollment_data(self, partner=None):
        """Datos QWeb confirmación de pago: cursos LMS ya inscritos tras el checkout."""
        self.ensure_one()
        partner = partner or self.partner_id
        channels = []
        for line in self._das_lms_get_lms_sale_lines():
            channel = line.product_id.product_tmpl_id._das_lms_get_related_channel(
                product_product=line.product_id
            )
            if not channel or not channel._das_lms_user_is_enrolled(partner):
                continue
            channels.append({
                'channel': channel,
                'name': channel.display_name,
                'url': channel._das_lms_public_course_href(),
                'cta_label': line.product_id.product_tmpl_id._das_lms_course_portal_cta_label(),
            })
        return {
            'show_success': bool(channels),
            'channels': channels,
        }

    def _das_lms_validate_course_cart_rules(self):
        """Reglas LMS por línea: cantidad 1, sin repetir curso, sin recompra ni curso cerrado."""
        for order in self:
            if order.state not in ('draft', 'sent'):
                continue
            partner = order.partner_id
            lms_lines = order._das_lms_get_lms_sale_lines()
            seen_channel_ids = set()
            for line in lms_lines:
                tmpl = line.product_id.product_tmpl_id
                channel = tmpl._das_lms_get_related_channel(product_product=line.product_id)
                if not channel:
                    continue
                qty = line.product_uom_qty or 0.0
                if qty > 1:
                    raise UserError(_('Solo puedes comprar 1 unidad por cada curso.'))
                cid = channel.id
                if cid in seen_channel_ids:
                    raise UserError(_('El curso «%s» ya está agregado en el pedido.') % channel.display_name)
                seen_channel_ids.add(cid)
                if partner:
                    msg = tmpl._das_lms_cart_validation_message(
                        partner,
                        new_qty=max(1, int(line.product_uom_qty or 1)),
                        product_product=line.product_id,
                    )
                    if msg:
                        raise UserError(msg)

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
                        product_product=line.product_id,
                    )
                )
            )
            if bad:
                bad.unlink()

    def _verify_updated_quantity(self, order_line, product_id, new_qty, **kwargs):
        """Cantidad LMS: forzar 1 en tienda con aviso amistoso (sin UserError por solo cantidad > 1)."""
        product = self.env['product.product'].browse(product_id).exists()
        qty_warning = ''
        if product:
            channel = product.product_tmpl_id._das_lms_get_related_channel(product_product=product)
            if channel and int(new_qty) > 1:
                new_qty = 1
                qty_warning = _('Solo puedes comprar 1 unidad por cada curso.')

        new_qty, warning = super()._verify_updated_quantity(order_line, product_id, new_qty, **kwargs)
        if qty_warning:
            warning = '\n'.join(x for x in (warning, qty_warning) if x)

        if new_qty <= 0 or not product:
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

        msg = product.product_tmpl_id._das_lms_cart_validation_message(
            partner,
            new_qty=int(new_qty),
            product_product=product,
        )
        if msg:
            raise UserError(msg)
        self._das_lms_validate_course_cart_rules()
        return new_qty, warning

    def action_confirm(self):
        if self.env.context.get('das_lms_paypal_post_payment_confirm'):
            return super().action_confirm()
        for order in self:
            order._das_lms_validate_course_cart_rules()
            partner = order.partner_id
            if not partner:
                continue
            for line in order.order_line:
                if line.display_type or not line.product_id:
                    continue
                msg = line.product_template_id._das_lms_cart_validation_message(
                    partner,
                    new_qty=max(1, int(line.product_uom_qty or 1)),
                    product_product=line.product_id,
                )
                if msg:
                    raise UserError(msg)
        return super().action_confirm()
