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
        with self.assertRaises(UserError) as cm:
            so._verify_updated_quantity(empty_line, variant.id, 1)
        self.assertIn('Canal LMS cart', cm.exception.args[0])

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
        with self.assertRaises(UserError) as cm:
            so._verify_updated_quantity(self.env['sale.order.line'], variant.id, 1)
        self.assertIn('ya no está disponible', cm.exception.args[0])

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

    def test_order_allows_two_distinct_lms_courses(self):
        """Varios cursos distintos x1 en el mismo pedido."""
        from odoo.tests.common import new_test_user

        portal = new_test_user(
            self.env,
            'lms_cart_two_courses',
            email='lms_cart_two_courses@test.example.com',
            groups='base.group_portal',
        )
        tmpl_a = self.env['product.template'].create({
            'name': 'Curso A multi',
            'list_price': 10.0,
            'sale_ok': True,
        })
        tmpl_b = self.env['product.template'].create({
            'name': 'Curso B multi',
            'list_price': 20.0,
            'sale_ok': True,
        })
        va = tmpl_a.product_variant_ids[:1]
        vb = tmpl_b.product_variant_ids[:1]
        self.env['slide.channel'].create({'name': 'Canal A multi', 'product_id': va.id})
        self.env['slide.channel'].create({'name': 'Canal B multi', 'product_id': vb.id})
        so = self.env['sale.order'].create({'partner_id': portal.partner_id.id})
        self.env['sale.order.line'].create({
            'order_id': so.id,
            'product_id': va.id,
            'product_uom_qty': 1,
        })
        self.env['sale.order.line'].create({
            'order_id': so.id,
            'product_id': vb.id,
            'product_uom_qty': 1,
        })
        self.assertEqual(len(so.order_line), 2)

    def test_order_blocks_quantity_two_same_course(self):
        from odoo.tests.common import new_test_user

        portal = new_test_user(
            self.env,
            'lms_cart_qty2',
            email='lms_cart_qty2@test.example.com',
            groups='base.group_portal',
        )
        tmpl = self.env['product.template'].create({
            'name': 'Curso qty2 LMS',
            'list_price': 10.0,
            'sale_ok': True,
        })
        variant = tmpl.product_variant_ids[:1]
        self.env['slide.channel'].create({'name': 'Canal qty2 LMS', 'product_id': variant.id})
        so = self.env['sale.order'].create({'partner_id': portal.partner_id.id})
        with self.assertRaises(UserError):
            self.env['sale.order.line'].create({
                'order_id': so.id,
                'product_id': variant.id,
                'product_uom_qty': 2,
            })

    def test_order_blocks_duplicate_line_same_course(self):
        from odoo.tests.common import new_test_user

        portal = new_test_user(
            self.env,
            'lms_cart_dup_line',
            email='lms_cart_dup_line@test.example.com',
            groups='base.group_portal',
        )
        tmpl = self.env['product.template'].create({
            'name': 'Curso dup LMS',
            'list_price': 10.0,
            'sale_ok': True,
        })
        variant = tmpl.product_variant_ids[:1]
        self.env['slide.channel'].create({'name': 'Canal dup LMS', 'product_id': variant.id})
        so = self.env['sale.order'].create({'partner_id': portal.partner_id.id})
        self.env['sale.order.line'].create({
            'order_id': so.id,
            'product_id': variant.id,
            'product_uom_qty': 1,
        })
        with self.assertRaises(UserError) as cm:
            self.env['sale.order.line'].create({
                'order_id': so.id,
                'product_id': variant.id,
                'product_uom_qty': 1,
            })
        self.assertIn('Canal dup LMS', cm.exception.args[0])

    def test_shop_academic_info_visible_with_course_dates(self):
        today = fields.Date.context_today(self.env.user)
        tmpl = self.env['product.template'].create({
            'name': 'Curso fechas tienda',
            'list_price': 75.0,
            'sale_ok': True,
        })
        variant = tmpl.product_variant_ids[:1]
        self.env['slide.channel'].create({
            'name': 'Canal fechas tienda',
            'product_id': variant.id,
            'das_start_date': fields.Date.add(today, days=-10),
            'das_end_date': fields.Date.add(today, days=20),
            'das_modality': 'grabado',
            'das_total_hours': 40,
        })
        self.assertTrue(tmpl._das_lms_shop_show_academic_info())

    def test_shop_academic_info_hidden_without_course(self):
        tmpl = self.env['product.template'].create({
            'name': 'Producto sin curso',
            'list_price': 10.0,
            'sale_ok': True,
        })
        self.assertFalse(tmpl._das_lms_shop_show_academic_info())
