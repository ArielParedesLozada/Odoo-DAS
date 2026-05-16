# -*- coding: utf-8 -*-
import logging

from odoo import _, api, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _post(self, soft=True):
        """Publicación contable: inscribir en eLearning solo para documentos realmente publicados aquí."""
        posted_subset = super()._post(soft=soft)
        enroll_moves = posted_subset.filtered(
            lambda m: m.is_sale_document(include_receipts=True)
            and m.move_type == 'out_invoice'
            and m.partner_id
        )
        if enroll_moves:
            _logger.info(
                'DAS LMS invoice post detected moves=%s ids=%s',
                len(enroll_moves),
                enroll_moves.ids,
            )
            enroll_moves._das_lms_enroll_from_posted_customer_invoice()
        return posted_subset

    def _das_lms_log_invoice_lines_snapshot(self):
        self.ensure_one()
        lines_info = []
        for line in self.invoice_line_ids:
            if line.display_type in ('line_section', 'line_note'):
                lines_info.append(
                    {
                        'line_id': line.id,
                        'display_type': line.display_type,
                        'product_id': None,
                        'sale_line_ids': [],
                    }
                )
                continue
            pid = line.product_id.id if line.product_id else None
            sol_ids = line.sale_line_ids.ids if line.sale_line_ids else []
            lines_info.append(
                {
                    'line_id': line.id,
                    'display_type': line.display_type or 'product',
                    'product_id': pid,
                    'sale_line_ids': sol_ids,
                }
            )
        _logger.info(
            'DAS LMS invoice post detected id=%s name=%s move_type=%s state=%s partner_id=%s lines=%s',
            self.id,
            self.name,
            self.move_type,
            self.state,
            self.partner_id.id if self.partner_id else None,
            lines_info,
        )

    def _das_lms_get_invoice_course_products(self):
        """Productos ``product.product`` que tienen curso eLearning resoluble por vínculo estructurado DAS.

        Considera ``product_id`` en líneas de factura, ``sale_line_ids.product_id``, líneas del pedido
        relacionado y pedidos localizados por ``invoice_origin``. Sin nombres ni búsquedas textuales.
        """
        self.ensure_one()
        SaleOrder = self.env['sale.order'].sudo()
        Product = self.env['product.product'].sudo()

        direct_ids = []
        sale_line_product_ids = []
        order_line_product_ids = []
        origin_order_product_ids = []

        def uappend(bucket, pid):
            if pid and pid not in bucket:
                bucket.append(pid)

        aml_products = self.invoice_line_ids.filtered(
            lambda l: l.display_type not in ('line_section', 'line_note')
        )

        orders_from_aml_links = set()
        for line in aml_products:
            if line.product_id:
                uappend(direct_ids, line.product_id.id)
            for sol in line.sale_line_ids:
                if sol.product_id:
                    uappend(sale_line_product_ids, sol.product_id.id)
                if sol.order_id:
                    orders_from_aml_links.add(sol.order_id.id)

        origin_refs = [r.strip() for r in (self.invoice_origin or '').split(',') if r.strip()]
        orders_from_origin = set()
        for ref in origin_refs:
            for so in SaleOrder.search([('name', '=', ref)]):
                orders_from_origin.add(so.id)

        orders_origin_only = orders_from_origin - orders_from_aml_links

        for oid in orders_from_aml_links:
            order = SaleOrder.browse(oid).exists()
            if not order:
                continue
            for ol in order.order_line:
                if ol.display_type or not ol.product_id:
                    continue
                uappend(order_line_product_ids, ol.product_id.id)

        for oid in orders_origin_only:
            order = SaleOrder.browse(oid).exists()
            if not order:
                continue
            for ol in order.order_line:
                if ol.display_type or not ol.product_id:
                    continue
                uappend(origin_order_product_ids, ol.product_id.id)

        merged_unique = []
        merged_seen = set()
        for pid in (
            direct_ids
            + sale_line_product_ids
            + order_line_product_ids
            + origin_order_product_ids
        ):
            if pid not in merged_seen:
                merged_seen.add(pid)
                merged_unique.append(pid)

        _logger.info(
            'DAS LMS invoice id=%s course candidate products: direct=%s sale_line_ids=%s '
            'order_lines(from_so_linked)=%s order_lines(origin_only)=%s merged_unique=%s',
            self.id,
            direct_ids,
            sale_line_product_ids,
            order_line_product_ids,
            origin_order_product_ids,
            merged_unique,
        )

        course_products = Product.browse()
        course_channel_ids = []
        for pid in merged_unique:
            product = Product.browse(pid).exists()
            if not product:
                continue
            tmpl = product.product_tmpl_id.sudo()
            channel = tmpl._das_lms_get_related_channel(product_product=product)
            if channel:
                course_products |= product
                course_channel_ids.append(channel.id)

        if not course_products:
            _logger.warning(
                'DAS LMS: no course products found for invoice id=%s name=%s',
                self.id,
                self.name or '',
            )

        _logger.info(
            'DAS LMS invoice id=%s course_products=%s resolved_channel_ids=%s partner=%s',
            self.id,
            course_products.ids,
            course_channel_ids,
            self.partner_id.id if self.partner_id else None,
        )

        return course_products

    def _das_lms_enroll_from_posted_customer_invoice(self):
        """Inscripción al validar/publicar factura cliente; vínculo product.template ↔ slide.channel."""
        for move in self:
            move._das_lms_log_invoice_lines_snapshot()
            partner = move.partner_id
            if not partner:
                continue
            course_products = move._das_lms_get_invoice_course_products()
            channels_done = set()
            for product in course_products:
                tmpl = product.product_tmpl_id.sudo()
                channel = tmpl._das_lms_get_related_channel(product_product=product.sudo())
                if not channel:
                    _logger.warning(
                        'DAS LMS: no related channel for invoice product tmpl=%s product=%s (move=%s)',
                        tmpl.id,
                        product.id,
                        move.id,
                    )
                    continue
                if channel.id in channels_done:
                    continue
                channels_done.add(channel.id)
                _logger.info(
                    'DAS LMS enrollment move=%s partner=%s commercial_partner=%s channel=%s '
                    'product=%s academic_status=%s',
                    move.id,
                    partner.id,
                    partner.commercial_partner_id.id,
                    channel.id,
                    product.id,
                    getattr(channel, 'das_academic_status', None),
                )
                try:
                    channel._das_lms_enroll_partner(partner)
                except (UserError, ValidationError):
                    raise
                except Exception:
                    _logger.exception(
                        'DAS LMS: inscripción fallida partner=%s canal=%s factura=%s.',
                        partner.id,
                        channel.id,
                        move.id,
                    )

    @api.model
    def das_lms_action_backfill_enrollments_from_posted_invoices(self):
        """Administradores: revisar facturas cliente ya publicadas y crear inscripciones faltantes."""
        self._das_lms_require_admin_backfill()
        moves = self.env['account.move'].search([
            ('state', '=', 'posted'),
            ('move_type', '=', 'out_invoice'),
            ('partner_id', '!=', False),
        ])
        moves._das_lms_enroll_from_posted_customer_invoice()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Inscripciones desde facturas'),
                'message': _('Facturas de cliente revisadas: %s.') % (len(moves),),
                'type': 'success',
                'sticky': False,
            },
        }

    @api.model
    def _das_lms_require_admin_backfill(self):
        if not (
            self.env.user.has_group('base.group_system')
            or self.env.user.has_group('base.group_erp_manager')
        ):
            raise UserError(_('Solo administradores pueden ejecutar esta acción.'))
