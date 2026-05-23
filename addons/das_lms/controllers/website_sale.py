# -*- coding: utf-8 -*-
import logging

from markupsafe import Markup

from odoo import fields
from odoo.addons.payment import utils as payment_utils
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.exceptions import UserError
from odoo.http import request, route
from odoo.tools.json import scriptsafe as json_scriptsafe

_logger = logging.getLogger(__name__)


class DasLmsWebsiteSale(WebsiteSale):
    def _prepare_product_values(self, product, category, search, **kwargs):
        values = super()._prepare_product_values(product, category, search, **kwargs)
        try:
            values.update(self._das_lms_prepare_product_page_extra(product))
        except Exception:
            _logger.exception(
                'DAS LMS: fallo preparando valores extra para product.template id=%s.',
                getattr(product, 'id', None),
            )
            Channel = request.env['slide.channel'].browse()
            values.update(
                {
                    'das_lms_hide_add_to_cart': False,
                    'das_lms_shop_channel': Channel,
                    'das_lms_shop_enrolled': False,
                    'das_lms_shop_can_sell': True,
                    'das_lms_debug_show': False,
                    'das_lms_debug_html': Markup(''),
                }
            )
        return values

    def _das_lms_prepare_product_page_extra(self, product_tmpl):
        """Flags coherentes para QWeb / debug (editores web o administradores)."""
        Channel = request.env['slide.channel'].browse()
        user = request.env.user
        if user._is_public():
            partner = request.env['res.partner'].browse()
        else:
            partner = user.partner_id[:1]

        channel = product_tmpl._das_lms_get_related_channel()
        hide_cart = bool(product_tmpl._das_lms_shop_should_hide_add_to_cart(partner=partner if partner else False))
        enrolled = bool(partner) and bool(product_tmpl._das_lms_user_is_enrolled(partner=partner))
        can_sell = not bool(partner) or bool(product_tmpl._das_lms_can_sell_to_partner(partner=partner))

        out = {
            'das_lms_hide_add_to_cart': hide_cart,
            'das_lms_shop_channel': channel if channel else Channel,
            'das_lms_shop_enrolled': enrolled,
            'das_lms_shop_can_sell': can_sell,
            'das_lms_debug_show': False,
            'das_lms_debug_html': Markup(''),
        }
        try:
            show_debug = user.has_group('base.group_system') or user.has_group(
                'website.group_website_restricted_editor'
            )
        except Exception:
            show_debug = False

        if show_debug:
            try:
                ch = channel[:1]
                tmpl_sudo = product_tmpl.sudo()
                parts = (
                    '<div class="alert alert-secondary border small text-start mb-3" role="note">'
                    '<div class="fw-bold mb-1">Depuración DAS LMS</div>'
                    '<ul class="small mb-0 ps-3">'
                    '<li><code>product.template</code> id: %s</li>'
                    '<li>IDs variantes: %s</li>'
                    '<li><code>das_lms_channel_id</code>: %s</li>'
                    '<li>Curso resuelto id: %s</li>'
                    '<li><code>slide.channel.product_id</code>: %s</li>'
                    '<li>Partner id: %s — comercial: %s</li>'
                    '<li><code>_das_lms_user_is_enrolled(partner)</code>: %s</li>'
                    '<li><code>_das_lms_can_sell_to_partner(partner)</code>: %s</li>'
                    '<li>Ocultar «Agregar al carrito»: %s</li>'
                    '</ul></div>'
                ) % (
                    product_tmpl.id,
                    ', '.join(str(v) for v in tmpl_sudo.product_variant_ids.ids) or '—',
                    tmpl_sudo.das_lms_channel_id.id or '—',
                    ch.id if ch else '—',
                    ch.product_id.id if ch and ch.product_id else '—',
                    partner.id if partner else '—',
                    partner.commercial_partner_id.id if partner else '—',
                    enrolled,
                    can_sell,
                    hide_cart,
                )
                out['das_lms_debug_show'] = True
                out['das_lms_debug_html'] = Markup(parts)
            except Exception:
                _logger.exception(
                    'DAS LMS: panel debug tienda product.template id=%s.',
                    product_tmpl.id,
                )

        return out

    def _prepare_shop_payment_confirmation_values(self, order):
        order_sudo = order.sudo()
        tx = order_sudo.get_portal_last_transaction()
        if (
            tx
            and tx.provider_code == 'paypal'
            and tx.state in ('pending', 'done')
            and order_sudo._das_lms_get_lms_sale_lines()
        ):
            try:
                with request.env.cr.savepoint():
                    tx._das_lms_finalize_paypal_lms_order()
            except Exception:
                _logger.exception(
                    'DAS LMS: fallo al finalizar PayPal en confirmación pedido=%s tx=%s.',
                    order_sudo.name,
                    tx.id,
                )
                # Evita InFailedSqlTransaction en el resto de la petición HTTP.
                request.env.clear()
            order_sudo.invalidate_recordset(['state', 'invoice_status', 'invoice_ids'])
        values = super()._prepare_shop_payment_confirmation_values(order)
        enrollment = order_sudo._das_lms_payment_confirmation_enrollment_data()
        values['das_lms_payment_enrollment'] = enrollment
        paypal_lms_ok = bool(
            tx
            and tx.provider_code == 'paypal'
            and tx.state in ('pending', 'done')
            and enrollment.get('show_success')
        )
        values['das_lms_paypal_instant_enrollment'] = paypal_lms_ok
        values['das_lms_paypal_hide_pending_status'] = paypal_lms_ok
        return values

    @route(['/shop/cart/update'], type='http', auth='public', methods=['POST'], website=True)
    def cart_update(
        self,
        product_id,
        add_qty=1,
        set_qty=0,
        product_custom_attribute_values=None,
        no_variant_attribute_value_ids=None,
        **kwargs,
    ):
        """Igual que Odoo, pero los UserError no redirigen a la página genérica de error."""
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)

        if product_custom_attribute_values:
            product_custom_attribute_values = json_scriptsafe.loads(product_custom_attribute_values)

        no_variant_attribute_values = kwargs.pop('no_variant_attribute_values', None)
        if no_variant_attribute_values and no_variant_attribute_value_ids is None:
            no_variants_attribute_values_data = json_scriptsafe.loads(no_variant_attribute_values)
            no_variant_attribute_value_ids = [
                int(ptav_data['value']) for ptav_data in no_variants_attribute_values_data
            ]

        try:
            sale_order._cart_update(
                product_id=int(product_id),
                add_qty=add_qty,
                set_qty=set_qty,
                product_custom_attribute_values=product_custom_attribute_values,
                no_variant_attribute_value_ids=no_variant_attribute_value_ids,
                **kwargs,
            )
        except UserError as err:
            warn = err.args[0] if err.args else str(err)
            request.env.cr.rollback()
            sale_order = request.website.sale_get_order(force_create=False)
            if sale_order:
                prev = (sale_order.shop_warning or '').strip()
                sale_order.write({'shop_warning': '\n'.join(x for x in (prev, warn) if x)})

        request.session['website_sale_cart_quantity'] = sale_order.cart_quantity if sale_order else 0
        return request.redirect('/shop/cart')

    @route(['/shop/cart/update_json'], type='json', auth='public', methods=['POST'], website=True)
    def cart_update_json(
        self,
        product_id,
        line_id=None,
        add_qty=None,
        set_qty=None,
        display=True,
        product_custom_attribute_values=None,
        no_variant_attribute_value_ids=None,
        **kwargs,
    ):
        try:
            return super().cart_update_json(
                product_id,
                line_id=line_id,
                add_qty=add_qty,
                set_qty=set_qty,
                display=display,
                product_custom_attribute_values=product_custom_attribute_values,
                no_variant_attribute_value_ids=no_variant_attribute_value_ids,
                **kwargs,
            )
        except UserError as err:
            warn = err.args[0] if err.args else str(err)
            request.env.cr.rollback()
            order = request.website.sale_get_order(force_create=False)
            quantity = 1
            if order and line_id:
                sol = order.order_line.filtered(lambda l: l.id == int(line_id))[:1]
                if sol:
                    quantity = sol.product_uom_qty
            if order:
                prev = (order.shop_warning or '').strip()
                order.write({'shop_warning': '\n'.join(x for x in (prev, warn) if x)})
            cart_qty = order.cart_quantity if order else 0
            request.session['website_sale_cart_quantity'] = cart_qty
            values = {
                'warning': warn,
                'quantity': quantity,
                'cart_quantity': cart_qty,
                'notification_info': {'warning': warn},
            }
            if not display:
                return values
            if not order:
                return values
            values['minor_amount'] = payment_utils.to_minor_currency_units(
                order._get_amount_total_excluding_delivery(),
                order.currency_id,
            )
            values['amount'] = order.amount_total
            values['cart_ready'] = order._is_cart_ready()
            values['website_sale.cart_lines'] = request.env['ir.ui.view']._render_template(
                'website_sale.cart_lines',
                {
                    'website_sale_order': order,
                    'date': fields.Date.today(),
                    'suggested_products': order._cart_accessories(),
                },
            )
            values['website_sale.total'] = request.env['ir.ui.view']._render_template(
                'website_sale.total',
                {'website_sale_order': order},
            )
            return values
