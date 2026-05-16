# -*- coding: utf-8 -*-
import logging

from markupsafe import Markup

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request

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
