# -*- coding: utf-8 -*-
import logging

from odoo import Command, models

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
        """Orquesta la finalización PayPal LMS; cada transacción en su propio bloque."""
        for tx in self:
            try:
                tx._das_lms_finalize_paypal_lms_order()
            except Exception:
                _logger.exception(
                    'DAS LMS PayPal finalize falló tx=%s reference=%s',
                    tx.id,
                    tx.reference,
                )

    def _das_lms_finalize_paypal_lms_order(self):
        """Finaliza un pago PayPal LMS en pasos secuenciales e idempotentes.

        1. Confirmar pedido (``sale``) y persistir.
        2. Crear factura final desde las líneas del pedido (no anticipo) y publicarla.
        3. Registrar pago contable (factura pagada).
        4. Inscribir al estudiante en los cursos.
        """
        self.ensure_one()
        lms_orders = self.sale_order_ids.filtered(lambda o: o._das_lms_get_lms_sale_lines())
        if not lms_orders:
            return

        # --- Paso 1: confirmar pedido ---
        self._das_lms_confirm_paypal_sale_orders()
        self.env.flush_all()

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

        # --- Paso 2: factura final (con importe real del pedido) ---
        posted_invoices = self.env['account.move']
        try:
            with self.env.cr.savepoint():
                posted_invoices = self._das_lms_paypal_ensure_posted_invoices(confirmed_lms)
                self.env.flush_all()
        except Exception:
            _logger.exception(
                'DAS LMS PayPal: fallo al facturar tx=%s orders=%s',
                self.id,
                confirmed_lms.ids,
            )

        if not posted_invoices:
            _logger.warning(
                'DAS LMS PayPal finalize: sin factura publicada tx=%s orders=%s',
                self.id,
                confirmed_lms.ids,
            )
            return

        # --- Paso 3: pago contable (aislado; no revierte confirmación ni factura) ---
        try:
            with self.env.cr.savepoint():
                self._das_lms_paypal_register_payment(posted_invoices)
        except Exception:
            _logger.exception(
                'DAS LMS PayPal: fallo al registrar pago tx=%s invoices=%s',
                self.id,
                posted_invoices.ids,
            )

        # --- Paso 4: inscripción eLearning ---
        partner = self.partner_id or confirmed_lms[:1].partner_id
        if partner:
            try:
                with self.env.cr.savepoint():
                    confirmed_lms._das_lms_enroll_partner_from_order(partner)
            except Exception:
                _logger.exception(
                    'DAS LMS PayPal: fallo al inscribir tx=%s partner=%s',
                    self.id,
                    partner.id,
                )

        _logger.info(
            'DAS LMS PayPal finalize tx=%s state=%s orders=%s invoice_status=%s '
            'invoices=%s paid=%s partner=%s',
            self.id,
            self.state,
            confirmed_lms.ids,
            confirmed_lms.mapped('invoice_status'),
            posted_invoices.ids,
            posted_invoices.mapped('payment_state'),
            partner.id if partner else None,
        )

    def _das_lms_paypal_ensure_posted_invoices(self, orders):
        """Crea la factura final del pedido confirmado y la publica (no anticipos en cero)."""
        self.ensure_one()
        invoices = self.invoice_ids | orders.invoice_ids
        customer_invoices = invoices.filtered(
            lambda m: m.move_type == 'out_invoice' and m.state != 'cancel'
        )

        invalid_zero = customer_invoices.filtered(
            lambda m: m.currency_id.is_zero(m.amount_total)
        )
        if invalid_zero:
            _logger.info(
                'DAS LMS PayPal: limpiando facturas inválidas (importe cero) tx=%s moves=%s',
                self.id,
                invalid_zero.ids,
            )
            removed = self._das_lms_paypal_cancel_invalid_invoices(invalid_zero)
            customer_invoices -= removed

        valid_invoices = customer_invoices.filtered(
            lambda m: not m.currency_id.is_zero(m.amount_total)
        )
        if not valid_invoices:
            orders._force_lines_to_invoice_policy_order()
            new_invoices = orders.with_context(
                raise_if_nothing_to_invoice=False,
            )._create_invoices(final=True)
            for invoice in new_invoices:
                invoice._portal_ensure_token()
            if new_invoices:
                self.invoice_ids = [Command.link(inv_id) for inv_id in new_invoices.ids]
            valid_invoices = new_invoices

        missing_on_tx = valid_invoices - self.invoice_ids
        if missing_on_tx:
            self.invoice_ids = [Command.link(inv_id) for inv_id in missing_on_tx.ids]

        drafts = valid_invoices.filtered(lambda m: m.state == 'draft')
        if drafts:
            drafts.action_post()

        return valid_invoices.filtered(lambda m: m.state == 'posted')

    def _das_lms_paypal_cancel_invalid_invoices(self, invoices):
        """Cancela facturas cliente erróneas; devuelve las retiradas del flujo (canceladas o ignoradas)."""
        removed = self.env['account.move']
        for invoice in invoices:
            if invoice.payment_state in ('paid', 'in_payment', 'reversed'):
                _logger.warning(
                    'DAS LMS PayPal: factura cero ya pagada, no se cancela move=%s tx=%s',
                    invoice.id,
                    self.id,
                )
                removed |= invoice
                continue
            try:
                with self.env.cr.savepoint():
                    if invoice.state == 'posted':
                        invoice.button_draft()
                    if invoice.state == 'draft':
                        invoice.button_cancel()
            except Exception:
                _logger.warning(
                    'DAS LMS PayPal: no se pudo cancelar factura inválida move=%s tx=%s',
                    invoice.id,
                    self.id,
                    exc_info=True,
                )
                continue
            if invoice.state == 'cancel':
                removed |= invoice
        stale_links = removed.filtered(lambda m: m.state == 'cancel')
        if stale_links:
            self.invoice_ids = [Command.unlink(inv_id) for inv_id in stale_links.ids]
        return removed

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
            lambda inv: inv.state == 'posted'
            and not inv.currency_id.is_zero(inv.amount_total)
            and inv.payment_state in ('not_paid', 'partial')
        )
        if not payable:
            return self.env['account.payment']
        if not self.invoice_ids:
            self.invoice_ids = [Command.set(payable.ids)]
        else:
            self.invoice_ids = [
                Command.link(inv_id) for inv_id in (payable - self.invoice_ids).ids
            ]
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
        self.env.flush_all()
        self._das_lms_paypal_reconcile_payment_invoices(payment, payable)
        return payment

    def _das_lms_paypal_reconcile_payment_invoices(self, payment, invoices):
        """Concilia el pago con las facturas si el flujo estándar no lo hizo (p. ej. tx ``pending``)."""
        self.ensure_one()
        if not payment or not invoices:
            return
        invoices = invoices.filtered(lambda inv: inv.state == 'posted')
        if not invoices:
            return
        if not payment.move_id:
            payment._generate_journal_entry()
            if payment.move_id.state == 'draft':
                payment.move_id.action_post()
        unpaid = invoices.filtered(lambda inv: inv.payment_state in ('not_paid', 'partial'))
        if not unpaid:
            return
        receivable_lines = (payment.move_id.line_ids + unpaid.line_ids).filtered(
            lambda line: line.account_id.account_type == 'asset_receivable'
            and line.partner_id == payment.partner_id.commercial_partner_id
            and not line.reconciled
        )
        if receivable_lines:
            receivable_lines.reconcile()
        if payment.state not in ('paid', 'in_process'):
            payment.action_post()
        if unpaid.filtered(lambda inv: inv.payment_state in ('not_paid', 'partial')):
            _logger.warning(
                'DAS LMS PayPal: factura sin conciliar tras pago tx=%s payment=%s invoices=%s',
                self.id,
                payment.id,
                unpaid.ids,
            )

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
