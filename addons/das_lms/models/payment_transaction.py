# -*- coding: utf-8 -*-
import logging

from odoo import models
from odoo.tools import str2bool

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _post_process(self):
        super()._post_process()
        self._das_lms_finalize_paypal_lms_orders_batch()

    def _das_lms_finalize_paypal_lms_orders_batch(self):
        """Post-proceso PayPal LMS: ``done`` y ``pending`` (captura en revisión en PayPal)."""
        txs = self.filtered(
            lambda tx: tx.provider_code == 'paypal'
            and tx.operation != 'validation'
            and tx.state in ('done', 'pending')
        )
        if txs:
            txs._das_lms_finalize_paypal_lms_orders()

    def _das_lms_finalize_paypal_lms_orders(self):
        """PayPal + cursos LMS: confirmar pedido, factura publicada e inscripción (idempotente).

        PayPal suele dejar la transacción en ``pending`` tras la captura (mensaje «en espera de
        aprobación») aunque el alumno ya pagó. El flujo estándar de ventas solo confirma el pedido
        en ``done``; aquí se completa el circuito LMS también en ``pending``.
        """
        for tx in self:
            if tx.sale_order_ids:
                tx._das_lms_confirm_paypal_sale_orders()

            lms_orders = tx.sale_order_ids.filtered(
                lambda o: o.state == 'sale' and o._das_lms_get_lms_sale_lines()
            )
            if not lms_orders:
                continue

            auto_invoice = str2bool(
                self.env['ir.config_parameter'].sudo().get_param('sale.automatic_invoice')
            )
            invoices = tx.invoice_ids
            if not invoices and not auto_invoice:
                tx._invoice_sale_orders()
                invoices = tx.invoice_ids
            drafts = (invoices | lms_orders.invoice_ids).filtered(
                lambda m: m.move_type == 'out_invoice' and m.state == 'draft'
            )
            if drafts:
                drafts.action_post()
            partner = tx.partner_id or lms_orders[:1].partner_id
            if partner:
                lms_orders._das_lms_enroll_partner_from_order(partner)
            _logger.info(
                'DAS LMS PayPal finalize tx=%s state=%s orders=%s invoices_posted=%s partner=%s',
                tx.id,
                tx.state,
                lms_orders.ids,
                (invoices | lms_orders.invoice_ids).filtered(
                    lambda m: m.move_type == 'out_invoice' and m.state == 'posted'
                ).ids,
                partner.id if partner else None,
            )

    def _das_lms_confirm_paypal_sale_orders(self):
        """Confirma cotizaciones vinculadas al pago PayPal (pending o done).

        ``_check_amount_and_confirm_order`` solo confirma si ``amount_paid`` del pedido
        alcanza el umbral; las transacciones ``pending`` no incrementan ``amount_paid``.
        """
        self.ensure_one()
        for order in self.sale_order_ids.filtered(lambda o: o.state in ('draft', 'sent')):
            if self.currency_id.compare_amounts(self.amount, order.amount_total) < 0:
                continue
            order.with_context(
                send_email=True,
                das_lms_skip_slide_channel_auto_enroll=True,
            ).action_confirm()
