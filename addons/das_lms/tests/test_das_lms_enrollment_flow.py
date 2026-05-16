# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestDasLmsEnrollmentFlow(TransactionCase):
    """Inscripción por factura y reglas de carrito sin automatizaciones Studio."""

    def test_skip_context_prevents_channel_partner_creation(self):
        channel = self.env['slide.channel'].create({'name': 'Curso público test', 'enroll': 'public'})
        partner = self.env['res.partner'].create({'name': 'Alumno skip'})
        channel.with_context(das_lms_skip_slide_channel_auto_enroll=True)._action_add_members(partner)
        self.assertFalse(
            self.env['slide.channel.partner'].search([
                ('channel_id', '=', channel.id),
                ('partner_id', '=', partner.id),
            ])
        )

    def test_das_lms_enroll_partner_idempotent(self):
        tmpl = self.env['product.template'].create({'name': 'Prod LMS enroll', 'sale_ok': True})
        variant = tmpl.product_variant_ids[:1]
        channel = self.env['slide.channel'].create({'name': 'Canal LMS enroll', 'product_id': variant.id})
        partner = self.env['res.partner'].create({'name': 'Alumno enroll'})
        scp1 = channel._das_lms_enroll_partner(partner)
        self.assertTrue(scp1)
        scp2 = channel._das_lms_enroll_partner(partner)
        self.assertEqual(scp1, scp2)
        self.assertEqual(
            self.env['slide.channel.partner'].search_count([
                ('channel_id', '=', channel.id),
                ('partner_id', 'child_of', partner.commercial_partner_id.id),
                ('active', '=', True),
            ]),
            1,
        )

    def test_sale_order_blocks_two_lms_products(self):
        partner = self.env.ref('base.res_partner_1')
        tmpl_a = self.env['product.template'].create({'name': 'Curso A struct', 'sale_ok': True})
        tmpl_b = self.env['product.template'].create({'name': 'Curso B struct', 'sale_ok': True})
        va, vb = tmpl_a.product_variant_ids[:1], tmpl_b.product_variant_ids[:1]
        self.env['slide.channel'].create({'name': 'CA struct', 'product_id': va.id})
        self.env['slide.channel'].create({'name': 'CB struct', 'product_id': vb.id})
        so = self.env['sale.order'].create({'partner_id': partner.id})
        self.env['sale.order.line'].create({
            'order_id': so.id,
            'product_id': va.id,
            'product_uom_qty': 1,
        })
        with self.assertRaises(UserError):
            self.env['sale.order.line'].create({
                'order_id': so.id,
                'product_id': vb.id,
                'product_uom_qty': 1,
            })

    def test_sale_order_blocks_qty_gt_one_on_lms_line(self):
        partner = self.env.ref('base.res_partner_1')
        tmpl = self.env['product.template'].create({'name': 'Curso qty struct', 'sale_ok': True})
        v = tmpl.product_variant_ids[:1]
        self.env['slide.channel'].create({'name': 'Cqty struct', 'product_id': v.id})
        so = self.env['sale.order'].create({'partner_id': partner.id})
        line = self.env['sale.order.line'].create({
            'order_id': so.id,
            'product_id': v.id,
            'product_uom_qty': 1,
        })
        with self.assertRaises(UserError):
            line.write({'product_uom_qty': 2})
