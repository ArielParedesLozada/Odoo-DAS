# -*- coding: utf-8 -*-
import logging

from odoo import Command, models
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
        """PayPal + cursos LMS: pedido confirmado, factura publicada y pagada, inscripción (idempotente).

        Secuencia:
        1. Confirmar la orden de venta (``sale``).
        2. Crear y publicar la factura cliente.
        3. Registrar el pago contable (factura en estado pagado).
        4. Inscribir al estudiante en los cursos del pedido.

        Cada transacción se procesa en un savepoint para no abortar la petición HTTP
        si falla un paso contable (p. ej. diario PayPal mal configurado).
        """
        for tx in self:
            try:
                with tx.env.cr.savepoint():
                    tx._das_lms_finalize_paypal_lms_order()
            except Exception:
                _logger.exception(
                    'DAS LMS PayPal finalize falló tx=%s reference=%s',
                    tx.id,
                    tx.reference,
                )

    def _das_lms_finalize_paypal_lms_order(self):
        """Finaliza un único pago PayPal LMS (llamar dentro de savepoint)."""
        self.ensure_one()
        lms_orders = self.sale_order_ids.filtered(lambda o: o._das_lms_get_lms_sale_lines())
        if not lms_orders:
            return

        self._das_lms_confirm_paypal_sale_orders()

        confirmed_lms = self.sale_order_ids.filtered(
            lambda o: o.state == 'sale' and o._das_lms_get_lms_sale_lines()
        )
        if not confirmed_lms:
            _logger.warning(
                'DAS LMS PayPal finalize: pedido LMS sin confirmar tx=%s orders=%s states=%s',
                self.id,
                lms_orders.ids,
                lms_orders.mapped('state'),
            )
            return

        posted_invoices = self._das_lms_paypal_ensure_posted_invoices(confirmed_lms)
        self._das_lms_paypal_register_payment(posted_invoices)

        partner = self.partner_id or confirmed_lms[:1].partner_id
        if partner:
            confirmed_lms._das_lms_enroll_partner_from_order(partner)

        _logger.info(
            'DAS LMS PayPal finalize tx=%s state=%s orders=%s invoices=%s paid=%s partner=%s',
            self.id,
            self.state,
            confirmed_lms.ids,
            posted_invoices.ids,
            posted_invoices.mapped('payment_state'),
            partner.id if partner else None,
        )

    def _das_lms_paypal_ensure_posted_invoices(self, orders):
        """Crea factura cliente si falta, la publica y la vincula a la transacción (idempotente)."""
        self.ensure_one()
        auto_invoice = str2bool(
            self.env['ir.config_parameter'].sudo().get_param('sale.automatic_invoice')
        )
        invoices = self.invoice_ids | orders.invoice_ids
        customer_invoices = invoices.filtered(lambda m: m.move_type == 'out_invoice')
        if not customer_invoices and not auto_invoice:
            self._invoice_sale_orders()
            customer_invoices = self.invoice_ids.filtered(lambda m: m.move_type == 'out_invoice')
        missing_on_tx = customer_invoices - self.invoice_ids
        if missing_on_tx:
            self.invoice_ids = [Command.link(inv_id) for inv_id in missing_on_tx.ids]
        drafts = customer_invoices.filtered(lambda m: m.state == 'draft')
        if drafts:
            drafts.action_post()
        return customer_invoices.filtered(lambda m: m.state == 'posted')

    def _das_lms_paypal_register_payment(self, invoices):
        """Registra ``account.payment`` y concilia facturas (idempotente; también en tx ``pending``)."""
        self.ensure_one()
        if self.payment_id:
            return self.payment_id
        if self.operation == 'validation':
            return self.env['account.payment']
        if any(child.state in ('done', 'cancel') for child in self.child_transaction_ids):
            return self.env['account.payment']
        payable = invoices.filtered(
            lambda inv: inv.state == 'posted' and inv.payment_state in ('not_paid', 'partial')
        )
        if not payable:
            return self.env['account.payment']
        if payable and not self.invoice_ids:
            self.invoice_ids = [Command.set(payable.ids)]
        elif payable:
            self.invoice_ids = [Command.link(inv_id) for inv_id in (payable - self.invoice_ids).ids]
        payment_method_line = self.provider_id.journal_id.inbound_payment_method_line_ids.filtered(
            lambda line: line.payment_provider_id == self.provider_id
        )
        if not payment_method_line:
            _logger.warning(
                'DAS LMS PayPal: sin línea de método de pago provider=%s tx=%s; '
                'se omite account.payment.',
                self.provider_id.id,
                self.id,
            )
            return self.env['account.payment']
        payment = self.with_company(self.company_id)._create_payment()
        return payment

    def _das_lms_confirm_paypal_sale_orders(self):
        """Confirma cotizaciones vinculadas al pago PayPal (idempotente: solo draft/sent)."""
        self.ensure_one()
        for order in self.sale_order_ids.filtered(lambda o: o.state in ('draft', 'sent')):
            if self.currency_id.compare_amounts(self.amount, order.amount_total) < 0:
                continue
            order.with_context(
                send_email=True,
                das_lms_skip_slide_channel_auto_enroll=True,
                das_lms_paypal_post_payment_confirm=True,
            ).action_confirm()
