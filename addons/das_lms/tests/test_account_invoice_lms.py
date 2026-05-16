# -*- coding: utf-8 -*-
from odoo import fields
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestDasLmsAccountInvoiceEnrollment(AccountTestInvoicingCommon):
    """Factura cliente publicada → slide.channel.partner + bloqueo recompra."""

    def test_customer_invoice_post_enrolls_and_blocks_repurchase(self):
        partner = self.partner_a
        product = self.env['product.product'].create({
            'name': 'Curso LMS factura test',
            'lst_price': 100.0,
            'sale_ok': True,
            'type': 'service',
            'invoice_policy': 'order',
        })
        self.env['slide.channel'].create({
            'name': 'Canal LMS factura test',
            'product_id': product.id,
            'enroll': 'payment',
        })
        tmpl = product.product_tmpl_id
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': fields.Date.context_today(self.env.user),
            'journal_id': self.company_data['default_journal_sale'].id,
            'invoice_line_ids': [(0, 0, {
                'product_id': product.id,
                'quantity': 1,
                'price_unit': 100.0,
            })],
        })
        invoice.action_post()
        self.assertTrue(tmpl._das_lms_user_is_enrolled(partner=partner))
        msg = tmpl._das_lms_cart_validation_message(partner, new_qty=1)
        self.assertTrue(msg)

    def test_invoice_line_without_product_id_uses_sale_line_link(self):
        """Simula línea de factura sin product_id pero enlazada al pedido vía sale_line_ids."""
        partner = self.partner_a
        product = self.env['product.product'].create({
            'name': 'Curso LMS sin product en aml',
            'lst_price': 50.0,
            'sale_ok': True,
            'type': 'service',
            'invoice_policy': 'order',
        })
        self.env['slide.channel'].create({
            'name': 'Canal LMS sin aml product',
            'product_id': product.id,
            'enroll': 'payment',
        })
        tmpl = product.product_tmpl_id
        order = self.env['sale.order'].create({'partner_id': partner.id})
        sol = self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': product.id,
            'product_uom_qty': 1,
            'price_unit': 50.0,
        })
        order.action_confirm()
        invoice = self.env['account.move'].sudo().create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': fields.Date.context_today(self.env.user),
            'invoice_origin': order.name,
            'journal_id': self.company_data['default_journal_sale'].id,
            'invoice_line_ids': [(0, 0, {
                'name': product.display_name,
                'quantity': 1,
                'price_unit': 50.0,
                'account_id': self.company_data['default_account_revenue'].id,
                'sale_line_ids': [(6, 0, sol.ids)],
            })],
        })
        aml = invoice.invoice_line_ids.filtered(lambda l: not l.display_type)[:1]
        self.assertTrue(aml.sale_line_ids)
        aml.sudo().write({'product_id': False})
        self.assertFalse(aml.product_id)
        invoice.action_post()
        self.assertTrue(tmpl._das_lms_user_is_enrolled(partner=partner))
        self.assertTrue(tmpl._das_lms_cart_validation_message(partner, new_qty=1))
