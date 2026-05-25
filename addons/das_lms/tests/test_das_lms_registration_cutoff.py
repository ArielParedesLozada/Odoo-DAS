# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase, new_test_user


@tagged('post_install', '-at_install')
class TestDasLmsRegistrationCutoff(TransactionCase):
    """Corte de inscripción: das_start_date − registration_cutoff_days."""

    def _create_course_product(self, channel_vals=None):
        tmpl = self.env['product.template'].create({
            'name': 'Curso cutoff test',
            'list_price': 50.0,
            'sale_ok': True,
            'website_published': True,
        })
        variant = tmpl.product_variant_ids[:1]
        vals = {'name': 'Canal cutoff', 'product_id': variant.id}
        if channel_vals:
            vals.update(channel_vals)
        channel = self.env['slide.channel'].create(vals)
        return tmpl, variant, channel

    def test_registration_open_before_cutoff(self):
        today = fields.Date.context_today(self.env.user)
        _, _, channel = self._create_course_product({
            'das_start_date': fields.Date.add(today, days=10),
            'das_end_date': fields.Date.add(today, days=40),
            'registration_cutoff_days': 2,
        })
        self.assertTrue(channel.das_registration_open)
        self.assertEqual(
            channel._das_lms_registration_deadline_date(),
            fields.Date.add(today, days=8),
        )

    def test_registration_blocked_after_cutoff_before_start(self):
        today = fields.Date.context_today(self.env.user)
        _, _, channel = self._create_course_product({
            'das_start_date': fields.Date.add(today, days=1),
            'registration_cutoff_days': 2,
        })
        self.assertEqual(channel.das_academic_status, 'proximo')
        self.assertFalse(channel.das_registration_open)
        self.assertFalse(channel.das_can_sell)

    def test_enrollment_before_cutoff_succeeds(self):
        today = fields.Date.context_today(self.env.user)
        partner = self.env['res.partner'].create({'name': 'Alumno antes corte'})
        _, _, channel = self._create_course_product({
            'das_start_date': fields.Date.add(today, days=15),
            'registration_cutoff_days': 2,
        })
        membership = channel._das_lms_enroll_partner(partner)
        self.assertTrue(membership)

    def test_enrollment_after_cutoff_blocked(self):
        today = fields.Date.context_today(self.env.user)
        partner = self.env['res.partner'].create({'name': 'Alumno post corte'})
        _, _, channel = self._create_course_product({
            'das_start_date': fields.Date.add(today, days=1),
            'registration_cutoff_days': 2,
        })
        with self.assertRaises(ValidationError) as cm:
            channel._das_lms_enroll_partner(partner)
        self.assertIn('ha cerrado', cm.exception.args[0])

    def test_cart_blocks_after_registration_cutoff(self):
        today = fields.Date.context_today(self.env.user)
        portal = new_test_user(
            self.env,
            'lms_cutoff_blocked',
            email='lms_cutoff_blocked@test.example.com',
            groups='base.group_portal',
        )
        tmpl, variant, _channel = self._create_course_product({
            'das_start_date': fields.Date.add(today, days=1),
            'registration_cutoff_days': 2,
        })
        so = self.env['sale.order'].create({'partner_id': portal.partner_id.id})
        with self.assertRaises(UserError) as cm:
            so._verify_updated_quantity(self.env['sale.order.line'], variant.id, 1)
        self.assertIn('ha cerrado', cm.exception.args[0])

    def test_shop_hidden_after_course_start(self):
        today = fields.Date.context_today(self.env.user)
        tmpl, _variant, _channel = self._create_course_product({
            'das_start_date': fields.Date.add(today, days=-1),
            'das_end_date': fields.Date.add(today, days=30),
        })
        hidden_ids = self.env['product.template']._das_lms_shop_hidden_product_template_ids()
        self.assertIn(tmpl.id, hidden_ids)
        self.assertFalse(tmpl._das_lms_shop_catalog_visible())

    def test_enrolled_student_keeps_access_after_start(self):
        today = fields.Date.context_today(self.env.user)
        portal = new_test_user(
            self.env,
            'lms_cutoff_enrolled',
            email='lms_cutoff_enrolled@test.example.com',
            groups='base.group_portal',
        )
        tmpl, variant, channel = self._create_course_product({
            'das_start_date': fields.Date.add(today, days=-2),
            'das_end_date': fields.Date.add(today, days=30),
            'registration_cutoff_days': 2,
        })
        self.env['slide.channel.partner'].create({
            'channel_id': channel.id,
            'partner_id': portal.partner_id.id,
        })
        tmpl_portal = tmpl.with_user(portal)
        hidden_ids = self.env['product.template']._das_lms_shop_hidden_product_template_ids(
            partner=portal.partner_id,
        )
        self.assertNotIn(tmpl.id, hidden_ids)
        self.assertTrue(tmpl_portal._das_lms_shop_catalog_visible(partner=portal.partner_id))
        self.assertTrue(tmpl_portal._das_lms_is_enrolled_in_course())
        self.assertTrue(tmpl_portal._das_lms_shop_should_hide_add_to_cart())
        self.assertEqual(tmpl_portal._das_lms_course_portal_cta_label(), 'Acceder al curso')

    def test_visitor_messages_by_date(self):
        today = fields.Date.context_today(self.env.user)
        _, _, before = self._create_course_product({
            'das_start_date': fields.Date.add(today, days=10),
            'registration_cutoff_days': 2,
        })
        self.assertEqual(before._das_lms_registration_notice_kind(), 'before_start')
        self.assertIn('aún no ha comenzado', before._das_lms_registration_notice_message())

        _, _, closed = self._create_course_product({
            'das_start_date': fields.Date.add(today, days=1),
            'registration_cutoff_days': 2,
        })
        self.assertEqual(closed._das_lms_registration_notice_kind(), 'closed')
        self.assertIn('ha cerrado', closed._das_lms_registration_notice_message())

        _, _, started = self._create_course_product({
            'das_start_date': fields.Date.add(today, days=-1),
            'das_end_date': fields.Date.add(today, days=20),
        })
        self.assertEqual(started._das_lms_registration_notice_kind(), 'closed')
        self.assertIn('ha cerrado', started._das_lms_registration_notice_message())

    def test_enroll_partner_idempotent_after_invoice(self):
        today = fields.Date.context_today(self.env.user)
        partner = self.env['res.partner'].create({'name': 'Alumno idempotente cutoff'})
        _, _, channel = self._create_course_product({
            'das_start_date': fields.Date.add(today, days=20),
            'das_end_date': fields.Date.add(today, days=60),
            'registration_cutoff_days': 2,
        })
        first = channel._das_lms_enroll_partner(partner)
        second = channel._das_lms_enroll_partner(partner)
        self.assertTrue(first)
        self.assertEqual(first, second)
        self.assertEqual(
            self.env['slide.channel.partner'].search_count([
                ('channel_id', '=', channel.id),
                ('partner_id', 'child_of', partner.commercial_partner_id.id),
            ]),
            1,
        )

    def test_negative_cutoff_days_raises(self):
        with self.assertRaises(ValidationError):
            self.env['slide.channel'].create({
                'name': 'Curso cutoff negativo',
                'registration_cutoff_days': -1,
            })
