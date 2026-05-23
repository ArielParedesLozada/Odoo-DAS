# -*- coding: utf-8 -*-
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    das_lms_channel_id = fields.Many2one(
        'slide.channel',
        string='Curso eLearning relacionado',
        index=True,
        copy=False,
        help=(
            'Enlace explícito al curso vendido por este producto. '
            'Si se deja vacío, se usa la relación nativa de website_sale_slides: '
            'un canal cuyo campo «Producto» sea una variante de esta plantilla. '
            'Los productos de curso deben tener siempre vínculo explícito O el producto variante '
            'correcto en el canal.'
        ),
    )

    das_lms_slide_channel_id = fields.Many2one(
        'slide.channel',
        string='Curso eLearning (resuelto)',
        compute='_compute_das_lms_slide_channel',
        store=False,
    )

    @api.depends('das_lms_channel_id', 'product_variant_ids')
    def _compute_das_lms_slide_channel(self):
        for template in self:
            try:
                template.das_lms_slide_channel_id = template._das_lms_get_related_channel(product_product=None)
            except Exception:
                _logger.exception(
                    'DAS LMS: error al resolver curso para plantilla id=%s; campo calculado vacío.',
                    template.id,
                )
                template.das_lms_slide_channel_id = False

    @api.constrains('das_lms_channel_id', 'product_variant_ids')
    def _check_das_lms_channel_matches_variants(self):
        """Si el canal tiene producto Odoo, debe ser una variante de esta plantilla."""
        for rec in self:
            ch = rec.das_lms_channel_id
            if not ch or not ch.product_id:
                continue
            if ch.product_id.id not in rec.product_variant_ids.ids:
                raise ValidationError(
                    _('El curso «%s» está ligado a un producto que no pertenece a esta plantilla de producto.')
                    % (ch.display_name,)
                )

    def _das_lms_get_related_channel(self, product_product=None):
        """Curso asociado: A) das_lms_channel_id, B) canal con product_id = variante, C) cualquier variante.

        Sin coincidencias por nombre. ``product_product`` refina la búsqueda desde líneas de factura/pedido.
        """
        self.ensure_one()
        try:
            tmpl = self.sudo()
            Channel = self.env['slide.channel'].sudo()
            cid = tmpl.das_lms_channel_id.id
            if cid:
                ch = Channel.browse(cid).exists()
                if not ch:
                    _logger.warning(
                        'DAS LMS: plantilla id=%s tiene das_lms_channel_id=%s inexistente.',
                        self.id,
                        cid,
                    )
                    return Channel.browse()
                return ch
            variant_ids = tmpl.product_variant_ids.ids
            if not variant_ids:
                return Channel.browse()
            pp = product_product.sudo() if product_product else None
            if pp:
                ch_exact = Channel.search([('product_id', '=', pp.id)], limit=1)
                if ch_exact:
                    return ch_exact
            return Channel.search([('product_id', 'in', variant_ids)], order='id asc', limit=1)
        except Exception:
            _logger.exception(
                'DAS LMS: fallo _das_lms_get_related_channel para product.template id=%s.',
                self.id,
            )
            return self.env['slide.channel'].browse()

    def _das_lms_shop_should_hide_add_to_cart(self, partner=None):
        """Ocultar agregar al carrito en tienda (usuario actual o partner explícito)."""
        self.ensure_one()
        try:
            if self._das_lms_course_sale_blocked():
                return True
            if not partner:
                return False
            return bool(self._das_lms_user_is_enrolled(partner=partner))
        except Exception:
            _logger.exception(
                'DAS LMS: _das_lms_shop_should_hide_add_to_cart plantilla id=%s.',
                self.id,
            )
            return False

    def _das_lms_fallback_hide_shop_cart(self):
        """Fallback QWeb cuando no existan valores del controlador DAS LMS."""
        self.ensure_one()
        try:
            from odoo.http import request

            if request and getattr(request, 'env', None):
                user = request.env.user
                if user and not user._is_public():
                    return self._das_lms_shop_should_hide_add_to_cart(partner=user.partner_id)
        except RuntimeError:
            pass
        except Exception:
            _logger.exception(
                'DAS LMS: _das_lms_fallback_hide_shop_cart plantilla id=%s.',
                self.id,
            )
            return False
        try:
            return self._das_lms_course_sale_blocked()
        except Exception:
            _logger.exception(
                'DAS LMS: _das_lms_course_sale_blocked en fallback plantilla id=%s.',
                self.id,
            )
            return False

    def _das_lms_user_is_enrolled(self, partner=None):
        self.ensure_one()
        try:
            channel = self._das_lms_get_related_channel()
            if not channel:
                return False
            return bool(channel._das_lms_user_is_enrolled(partner=partner))
        except Exception:
            _logger.exception(
                'DAS LMS: _das_lms_user_is_enrolled plantilla id=%s.',
                self.id,
            )
            return False

    def _das_lms_can_sell_to_partner(self, partner=None):
        self.ensure_one()
        try:
            channel = self._das_lms_get_related_channel()
            if not channel:
                return True
            return bool(channel._das_lms_can_sell_to_partner(partner=partner))
        except Exception:
            _logger.exception(
                'DAS LMS: _das_lms_can_sell_to_partner plantilla id=%s.',
                self.id,
            )
            return True

    def _das_lms_cart_validation_message(self, partner, new_qty=1, product_product=None):
        """Mensaje de bloqueo carrito/checkout, o False si está permitido.

        :param product_product: variante concreta (opcional) para resolver ``slide.channel``.
        """
        self.ensure_one()
        try:
            if new_qty <= 0:
                return False
            channel = self._das_lms_get_related_channel(product_product=product_product)
            if not channel:
                return False
            if new_qty > 1:
                return _('Solo puedes comprar 1 unidad por cada curso.')
            if not partner:
                return False
            if channel._das_lms_user_is_enrolled(partner):
                return _('Ya estás inscrito en el curso «%s».') % channel.display_name
            if not channel.das_registration_open:
                return channel._das_lms_registration_notice_message(partner=partner)
            return False
        except Exception:
            _logger.exception(
                'DAS LMS: _das_lms_cart_validation_message plantilla id=%s.',
                self.id,
            )
            return False

    def _das_lms_is_enrolled_in_course(self):
        """Tienda / QWeb: inscripción por slide.channel.partner en el canal relacionado."""
        self.ensure_one()
        try:
            if self.env.user._is_public():
                return False
            return self._das_lms_user_is_enrolled(partner=self.env.user.partner_id)
        except Exception:
            _logger.exception(
                'DAS LMS: _das_lms_is_enrolled_in_course plantilla id=%s.',
                self.id,
            )
            return False

    def _das_lms_shop_enrolled_banner_alert_classes(self):
        """Clases del bloque único de estado (inscrito) en ficha de tienda."""
        self.ensure_one()
        try:
            channel = self._das_lms_get_related_channel()
            status = getattr(channel, 'das_academic_status', None) if channel else None
            shell = (
                'o_das_lms_shop_enrollment_banner mb-3 py-3 px-3 shadow-sm '
                'd-flex align-items-start rounded border'
            )
            if status == 'finalizado':
                return shell + ' alert alert-secondary border-secondary-subtle'
            if status == 'proximo':
                return shell + ' alert alert-info border-info-subtle'
            return shell + ' alert alert-success border-success-subtle'
        except Exception:
            _logger.exception(
                'DAS LMS: _das_lms_shop_enrolled_banner_alert_classes plantilla id=%s.',
                self.id,
            )
            return (
                'o_das_lms_shop_enrollment_banner mb-3 py-3 px-3 shadow-sm '
                'd-flex align-items-start rounded border alert alert-success border-success-subtle'
            )

    def _das_lms_shop_enrolled_banner_icon_classes(self):
        """Icono del bloque inscrito (misma familia FA, color según estado)."""
        self.ensure_one()
        try:
            channel = self._das_lms_get_related_channel()
            status = getattr(channel, 'das_academic_status', None) if channel else None
            if status == 'finalizado':
                return 'fa fa-check-circle text-secondary'
            if status == 'proximo':
                return 'fa fa-info-circle text-info'
            return 'fa fa-check-circle text-success'
        except Exception:
            _logger.exception(
                'DAS LMS: _das_lms_shop_enrolled_banner_icon_classes plantilla id=%s.',
                self.id,
            )
            return 'fa fa-check-circle text-success'

    def _das_lms_shop_enrolled_banner_btn_icon_classes(self):
        """Icono del botón dentro del bloque inscrito."""
        self.ensure_one()
        try:
            channel = self._das_lms_get_related_channel()
            status = getattr(channel, 'das_academic_status', None) if channel else None
            if status == 'proximo':
                return 'fa fa-info-circle me-2'
            return 'fa fa-play-circle me-2'
        except Exception:
            _logger.exception(
                'DAS LMS: _das_lms_shop_enrolled_banner_btn_icon_classes plantilla id=%s.',
                self.id,
            )
            return 'fa fa-play-circle me-2'

    def _das_lms_shop_enrolled_banner_title(self):
        self.ensure_one()
        return _('Ya estás inscrito en este curso.')

    def _das_lms_shop_enrolled_banner_body(self):
        """Descripción del bloque único inscrito (según ciclo académico)."""
        self.ensure_one()
        try:
            channel = self._das_lms_get_related_channel()
            if not channel:
                return _('Puedes continuar tu aprendizaje desde tu sección de cursos.')
            status = getattr(channel, 'das_academic_status', None)
            if status == 'finalizado':
                return _(
                    'Este ciclo académico ya finalizó. Puedes revisar el curso desde tu sección de cursos.'
                )
            if status == 'proximo' and channel.das_start_date:
                ds = channel.das_start_date.strftime('%d/%m/%Y')
                return _('El curso inicia el %s. Podrás acceder al contenido desde esa fecha.') % ds
            return _('Puedes continuar tu aprendizaje desde tu sección de cursos.')
        except Exception:
            _logger.exception(
                'DAS LMS: _das_lms_shop_enrolled_banner_body plantilla id=%s.',
                self.id,
            )
            return _('Puedes continuar tu aprendizaje desde tu sección de cursos.')

    def _das_lms_course_portal_cta_label(self):
        """Etiqueta del botón del bloque inscrito en tienda."""
        self.ensure_one()
        try:
            channel = self._das_lms_get_related_channel()
            status = getattr(channel, 'das_academic_status', None) if channel else None
            if status == 'proximo':
                return _('Ver información del curso')
            return _('Acceder al curso')
        except Exception:
            _logger.exception(
                'DAS LMS: _das_lms_course_portal_cta_label plantilla id=%s.',
                self.id,
            )
            return _('Acceder al curso')

    def _das_lms_course_website_url(self):
        self.ensure_one()
        try:
            channel = self._das_lms_get_related_channel()
            if not channel:
                return '#'
            return channel._das_lms_public_course_href()
        except Exception:
            _logger.exception(
                'DAS LMS: _das_lms_course_website_url plantilla id=%s.',
                self.id,
            )
            return '#'

    def _das_lms_course_sale_blocked(self):
        """Bloquear venta a nuevos alumnos si el corte de inscripción cerró o el curso finalizó."""
        self.ensure_one()
        try:
            channel = self._das_lms_get_related_channel()
            return bool(channel and not channel.das_registration_open)
        except Exception:
            _logger.exception(
                'DAS LMS: _das_lms_course_sale_blocked plantilla id=%s.',
                self.id,
            )
            return False

    def _das_lms_course_sale_notice_kind(self):
        """closed | before_start | open | none — para clases CSS en tienda."""
        self.ensure_one()
        try:
            if self._das_lms_is_enrolled_in_course():
                return 'none'
            channel = self._das_lms_get_related_channel()
            if not channel:
                return 'none'
            partner = self.env.user.partner_id if not self.env.user._is_public() else None
            return channel._das_lms_registration_notice_kind(partner=partner)
        except Exception:
            _logger.exception(
                'DAS LMS: _das_lms_course_sale_notice_kind plantilla id=%s.',
                self.id,
            )
            return 'none'

    def _das_lms_course_sale_notice_html(self):
        """Texto informativo en ficha de producto (solo visitantes / no inscritos)."""
        self.ensure_one()
        try:
            if self._das_lms_is_enrolled_in_course():
                return ''
            channel = self._das_lms_get_related_channel()
            if not channel:
                return ''
            partner = self.env.user.partner_id if not self.env.user._is_public() else None
            return channel._das_lms_registration_notice_message(partner=partner)
        except Exception:
            _logger.exception(
                'DAS LMS: _das_lms_course_sale_notice_html plantilla id=%s.',
                self.id,
            )
            return ''

    def _das_lms_course_sale_notice_alert_classes(self):
        """Clases Bootstrap del aviso de inscripción (amarillo / gris)."""
        self.ensure_one()
        kind = self._das_lms_course_sale_notice_kind()
        shell = (
            'alert border shadow-sm mb-3 py-3 px-3 rounded d-flex align-items-start '
            'o_das_lms_product_academic_notice'
        )
        if kind == 'closed':
            return shell + ' alert-secondary border-secondary-subtle'
        if kind in ('before_start', 'open'):
            return shell + ' alert-warning border-warning-subtle'
        return shell + ' alert-info border-info-subtle'

    def _get_additionnal_combination_info(self, product_or_template, quantity, date, website):
        """Añade bandera para el mixin de variantes: ocultar carrito LMS sin depender solo del DOM inicial."""
        try:
            data = super()._get_additionnal_combination_info(
                product_or_template, quantity, date, website
            )
        except Exception:
            raise
        hide = False
        try:
            if website is not None and getattr(website, 'env', None) is not None:
                user = website.env.user
            else:
                user = self.env.user
            partner = user.partner_id if user and not user._is_public() else False
            hide = bool(self._das_lms_shop_should_hide_add_to_cart(partner=partner))
        except Exception:
            _logger.exception(
                'DAS LMS: _get_additionnal_combination_info (flags LMS) plantilla id=%s.',
                self.id,
            )
            hide = False
        data.setdefault('das_lms_hide_add_to_cart', hide)
        data['das_lms_hide_add_to_cart'] = hide

        pp = product_or_template if getattr(product_or_template, '_name', None) == 'product.product' else None
        try:
            data['das_lms_course_qty_fixed'] = bool(self._das_lms_get_related_channel(product_product=pp))
        except Exception:
            data['das_lms_course_qty_fixed'] = False
        return data
