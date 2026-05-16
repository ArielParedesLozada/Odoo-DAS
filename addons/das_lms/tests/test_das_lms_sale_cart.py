# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestDasLmsSaleCart(TransactionCase):
    """Carrito y checkout: bloqueo por inscripción real y curso finalizado (sin heurísticas por nombre)."""

    def test_cart_blocks_when_already_enrolled(self):
        from odoo.tests.common import new_test_user

        portal = new_test_user(
            self.env,
            'lms_cart_enrolled',
            email='lms_cart_enrolled@test.example.com',
            groups='base.group_portal',
        )
        tmpl = self.env['product.template'].create({
            'name': 'Curso venta LMS',
            'list_price': 10.0,
            'sale_ok': True,
        })
        variant = tmpl.product_variant_ids[:1]
        ch = self.env['slide.channel'].create({'name': 'Canal LMS cart', 'product_id': variant.id})
        self.env['slide.channel.partner'].create({
            'channel_id': ch.id,
            'partner_id': portal.partner_id.id,
            'member_status': 'joined',
        })
        self.assertTrue(tmpl._das_lms_user_is_enrolled(partner=portal.partner_id))
        so = self.env['sale.order'].create({'partner_id': portal.partner_id.id})
        empty_line = self.env['sale.order.line']
        with self.assertRaises(UserError):
            so._verify_updated_quantity(empty_line, variant.id, 1)

    def test_cart_blocks_finished_course_new_user(self):
        from odoo.tests.common import new_test_user

        portal = new_test_user(
            self.env,
            'lms_cart_finished',
            email='lms_cart_finished@test.example.com',
            groups='base.group_portal',
        )
        today = fields.Date.context_today(self.env.user)
        tmpl = self.env['product.template'].create({
            'name': 'Curso cerrado LMS',
            'list_price': 10.0,
            'sale_ok': True,
        })
        variant = tmpl.product_variant_ids[:1]
        self.env['slide.channel'].create({
            'name': 'Canal fin LMS',
            'product_id': variant.id,
            'das_start_date': fields.Date.add(today, days=-60),
            'das_end_date': fields.Date.add(today, days=-2),
        })
        self.assertFalse(tmpl._das_lms_user_is_enrolled(partner=portal.partner_id))
        so = self.env['sale.order'].create({'partner_id': portal.partner_id.id})
        with self.assertRaises(UserError):
            so._verify_updated_quantity(self.env['sale.order.line'], variant.id, 1)

    def test_explicit_channel_must_match_product_variants(self):
        tmpl = self.env['product.template'].create({'name': 'Plantilla A', 'sale_ok': True})
        other = self.env['product.template'].create({'name': 'Plantilla B', 'sale_ok': True})
        vo = other.product_variant_ids[:1]
        ch = self.env['slide.channel'].create({'name': 'Canal otro producto', 'product_id': vo.id})
        with self.assertRaises(ValidationError):
            tmpl.write({'das_lms_channel_id': ch.id})

    def test_partner_cleanup_removes_invalid_line_on_partner_assign(self):
        """Al asignar partner al pedido, se eliminan líneas LMS inválidas."""
        from odoo.tests.common import new_test_user

        portal = new_test_user(
            self.env,
            'lms_cart_cleanup',
            email='lms_cart_cleanup@test.example.com',
            groups='base.group_portal',
        )
        tmpl = self.env['product.template'].create({
            'name': 'Curso cleanup',
            'list_price': 5.0,
            'sale_ok': True,
        })
        variant = tmpl.product_variant_ids[:1]
        ch = self.env['slide.channel'].create({'name': 'Canal cleanup', 'product_id': variant.id})
        self.env['slide.channel.partner'].create({
            'channel_id': ch.id,
            'partner_id': portal.partner_id.id,
            'member_status': 'joined',
        })
        so = self.env['sale.order'].create({})
        self.env['sale.order.line'].create({
            'order_id': so.id,
            'product_id': variant.id,
            'product_uom_qty': 1,
        })
        self.assertEqual(len(so.order_line), 1)
        so.write({'partner_id': portal.partner_id.id})
        self.assertFalse(so.order_line)
