# -*- coding: utf-8 -*-
from odoo import Command
from odoo.tests import tagged
from odoo.addons.account_payment.tests.common import AccountPaymentCommon


@tagged('post_install', '-at_install')
class TestDasLmsSalePaypal(AccountPaymentCommon):
    """PayPal: factura publicada e inscripción inmediata; otros métodos sin atajo LMS."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.enable_post_process_patcher = False

        cls.lms_product = cls.env['product.product'].create({
            'name': 'Curso LMS PayPal test',
            'lst_price': 120.0,
            'sale_ok': True,
            'type': 'service',
            'invoice_policy': 'order',
        })
        cls.lms_channel = cls.env['slide.channel'].create({
            'name': 'Canal LMS PayPal test',
            'product_id': cls.lms_product.id,
            'enroll': 'payment',
        })
        cls.lms_tmpl = cls.lms_product.product_tmpl_id

        cls.paypal_provider = cls._das_lms_get_test_provider('paypal')
        cls.custom_provider = cls._das_lms_get_test_provider('custom')
        cls._das_lms_configure_provider_journal(cls.paypal_provider)
        cls._das_lms_configure_provider_journal(cls.custom_provider)
        cls._das_lms_configure_provider_journal(cls.provider)

    @classmethod
    def _das_lms_get_test_provider(cls, code):
        provider = cls.env['payment.provider'].sudo().search([
            ('code', '=', code),
            ('company_id', '=', cls.company.id),
        ], limit=1)
        if provider:
            return provider
        method = cls.env['payment.method'].search([('code', '=', 'unknown')], limit=1)
        if not method:
            method = cls.payment_method
        values = {
            'name': 'DAS LMS %s test' % code,
            'code': code,
            'state': 'test',
            'is_published': True,
            'payment_method_ids': [Command.set([method.id])],
        }
        if code == 'paypal':
            values.update({
                'paypal_email_account': 'das-lms-paypal-test@example.com',
                'paypal_client_id': 'das_lms_paypal_test_client_id',
                'paypal_client_secret': 'das_lms_paypal_test_secret',
            })
        if code == 'custom':
            values['custom_mode'] = 'wire_transfer'
        return cls.env['payment.provider'].sudo().create(values)

    @classmethod
    def _das_lms_configure_provider_journal(cls, provider):
        if not provider.journal_id:
            return
        lines = provider.journal_id.inbound_payment_method_line_ids.filtered(
            lambda line: line.payment_provider_id == provider
        )
        if lines and hasattr(cls, 'inbound_payment_method_line'):
            lines.payment_account_id = cls.inbound_payment_method_line.payment_account_id

    def setUp(self):
        self.enable_post_process_patcher = False
        super().setUp()

    def _create_lms_sale_order(self, partner=None):
        partner = partner or self.partner_a
        return self.env['sale.order'].create({
            'partner_id': partner.id,
            'order_line': [Command.create({
                'product_id': self.lms_product.id,
                'product_uom_qty': 1,
            })],
        })

    def _create_payment_tx(self, order, provider):
        return self.env['payment.transaction'].sudo().create({
            'provider_id': provider.id,
            'payment_method_id': provider.payment_method_ids[:1].id,
            'amount': order.amount_total,
            'currency_id': order.currency_id.id,
            'partner_id': order.partner_id.id,
            'reference': order.name,
            'sale_order_ids': [Command.set([order.id])],
        })

    def test_paypal_pending_confirms_posts_invoice_and_enrolls(self):
        """Captura PayPal en revisión (tx pending): mismo circuito LMS que done."""
        self.env['ir.config_parameter'].sudo().set_param('sale.automatic_invoice', 'False')
        order = self._create_lms_sale_order()
        tx = self._create_payment_tx(order, self.paypal_provider)
        tx._set_pending()
        tx._post_process()

        self.assertEqual(order.state, 'sale')
        invoices = order.invoice_ids.filtered(lambda m: m.move_type == 'out_invoice')
        self.assertTrue(invoices)
        self.assertEqual(invoices[:1].state, 'posted')
        self.assertTrue(self.lms_tmpl._das_lms_user_is_enrolled(partner=order.partner_id))

    def test_paypal_done_posts_invoice_and_enrolls_without_automatic_invoice(self):
        self.env['ir.config_parameter'].sudo().set_param('sale.automatic_invoice', 'False')
        order = self._create_lms_sale_order()
        tx = self._create_payment_tx(order, self.paypal_provider)
        tx._set_done()
        tx._post_process()

        self.assertEqual(order.state, 'sale')
        invoices = order.invoice_ids.filtered(lambda m: m.move_type == 'out_invoice')
        self.assertTrue(invoices, 'PayPal LMS debe generar factura aunque sale.automatic_invoice sea False')
        self.assertEqual(invoices[:1].state, 'posted')
        self.assertTrue(self.lms_tmpl._das_lms_user_is_enrolled(partner=order.partner_id))
        self.assertTrue(
            self.env['slide.channel.partner'].search_count([
                ('channel_id', '=', self.lms_channel.id),
                ('partner_id', 'child_of', order.partner_id.commercial_partner_id.id),
                ('active', '=', True),
            ])
        )

    def test_paypal_enroll_is_idempotent_when_already_enrolled(self):
        self.env['ir.config_parameter'].sudo().set_param('sale.automatic_invoice', 'False')
        order = self._create_lms_sale_order()
        order.action_confirm()
        self.lms_channel._das_lms_enroll_partner(order.partner_id)
        tx = self._create_payment_tx(order, self.paypal_provider)
        tx._set_done()
        tx._post_process()

        self.assertEqual(
            self.env['slide.channel.partner'].search_count([
                ('channel_id', '=', self.lms_channel.id),
                ('partner_id', 'child_of', order.partner_id.commercial_partner_id.id),
                ('active', '=', True),
            ]),
            1,
        )

    def test_custom_provider_pending_keeps_traditional_flow(self):
        """Transferencia / custom pendiente: sin factura ni inscripción automática."""
        self.env['ir.config_parameter'].sudo().set_param('sale.automatic_invoice', 'False')
        order = self._create_lms_sale_order()
        tx = self._create_payment_tx(order, self.custom_provider)
        tx._set_pending()
        tx._post_process()

        self.assertIn(order.state, ('draft', 'sent'))
        self.assertFalse(order.invoice_ids)
        self.assertFalse(self.lms_tmpl._das_lms_user_is_enrolled(partner=order.partner_id))

    def test_non_paypal_done_without_automatic_invoice_does_not_force_lms_invoice(self):
        """Demo/otros proveedores: sin atajo PayPal no se factura ni inscribe automáticamente."""
        self.env['ir.config_parameter'].sudo().set_param('sale.automatic_invoice', 'False')
        order = self._create_lms_sale_order()
        tx = self._create_payment_tx(order, self.provider)
        tx._set_done()
        tx._post_process()

        self.assertEqual(order.state, 'sale')
        self.assertFalse(order.invoice_ids.filtered(lambda m: m.move_type == 'out_invoice'))
        self.assertFalse(self.lms_tmpl._das_lms_user_is_enrolled(partner=order.partner_id))

    def test_payment_confirmation_enrollment_data_after_paypal(self):
        self.env['ir.config_parameter'].sudo().set_param('sale.automatic_invoice', 'False')
        order = self._create_lms_sale_order()
        tx = self._create_payment_tx(order, self.paypal_provider)
        tx._set_done()
        tx._post_process()

        data = order._das_lms_payment_confirmation_enrollment_data()
        self.assertTrue(data['show_success'])
        self.assertEqual(len(data['channels']), 1)
        self.assertEqual(data['channels'][0]['name'], self.lms_channel.display_name)
        self.assertTrue(data['channels'][0]['url'])
