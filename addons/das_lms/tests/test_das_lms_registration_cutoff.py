# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase, new_test_user


@tagged('post_install', '-at_install')
class TestDasLmsRegistrationCutoff(TransactionCase):
    """Corte de inscripción: das_end_date − registration_cutoff_days."""

    def _create_course_product(self, channel_vals=None):
        tmpl = self.env['product.template'].create({
            'name': 'Curso cutoff test',
            'list_price': 50.0,
            'sale_ok': True,
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
            'das_start_date': fields.Date.add(today, days=-10),
            'das_end_date': fields.Date.add(today, days=10),
            'registration_cutoff_days': 2,
        })
        self.assertTrue(channel.das_registration_open)
        self.assertEqual(
            channel._das_lms_registration_deadline_date(),
            fields.Date.add(today, days=8),
        )

    def test_registration_blocked_after_cutoff_while_course_running(self):
        today = fields.Date.context_today(self.env.user)
        _, _, channel = self._create_course_product({
            'das_start_date': fields.Date.add(today, days=-10),
            'das_end_date': fields.Date.add(today, days=1),
            'registration_cutoff_days': 2,
        })
        self.assertEqual(channel.das_academic_status, 'en_curso')
        self.assertFalse(channel.das_registration_open)
        self.assertFalse(channel.das_can_sell)

    def test_cart_blocks_after_registration_cutoff(self):
        today = fields.Date.context_today(self.env.user)
        portal = new_test_user(
            self.env,
            'lms_cutoff_blocked',
            email='lms_cutoff_blocked@test.example.com',
            groups='base.group_portal',
        )
        tmpl, variant, _channel = self._create_course_product({
            'das_start_date': fields.Date.add(today, days=-5),
            'das_end_date': fields.Date.add(today, days=1),
            'registration_cutoff_days': 2,
        })
        so = self.env['sale.order'].create({'partner_id': portal.partner_id.id})
        with self.assertRaises(UserError):
            so._verify_updated_quantity(self.env['sale.order.line'], variant.id, 1)

    def test_enrolled_student_sees_access_course_cta(self):
        today = fields.Date.context_today(self.env.user)
        portal = new_test_user(
            self.env,
            'lms_cutoff_enrolled',
            email='lms_cutoff_enrolled@test.example.com',
            groups='base.group_portal',
        )
        tmpl, variant, channel = self._create_course_product({
            'das_start_date': fields.Date.add(today, days=-5),
            'das_end_date': fields.Date.add(today, days=1),
            'registration_cutoff_days': 2,
        })
        self.env['slide.channel.partner'].create({
            'channel_id': channel.id,
            'partner_id': portal.partner_id.id,
        })
        tmpl_portal = tmpl.with_user(portal)
        self.assertTrue(tmpl_portal._das_lms_is_enrolled_in_course())
        self.assertTrue(tmpl_portal._das_lms_shop_should_hide_add_to_cart())
        self.assertEqual(tmpl_portal._das_lms_course_portal_cta_label(), 'Acceder al curso')

    def test_visitor_messages_by_date(self):
        today = fields.Date.context_today(self.env.user)
        _, _, before = self._create_course_product({
            'das_start_date': fields.Date.add(today, days=5),
            'das_end_date': fields.Date.add(today, days=30),
            'registration_cutoff_days': 2,
        })
        self.assertEqual(before._das_lms_registration_notice_kind(), 'before_start')
        self.assertIn('aún no ha comenzado', before._das_lms_registration_notice_message())

        _, _, during = self._create_course_product({
            'das_start_date': fields.Date.add(today, days=-5),
            'das_end_date': fields.Date.add(today, days=20),
            'registration_cutoff_days': 2,
        })
        self.assertEqual(during._das_lms_registration_notice_kind(), 'open')
        self.assertIn('está en curso', during._das_lms_registration_notice_message())

        _, _, closed = self._create_course_product({
            'das_start_date': fields.Date.add(today, days=-10),
            'das_end_date': fields.Date.add(today, days=1),
            'registration_cutoff_days': 2,
        })
        self.assertEqual(closed._das_lms_registration_notice_kind(), 'closed')
        self.assertIn('ya no está disponible', closed._das_lms_registration_notice_message())

    def test_enroll_partner_idempotent_after_invoice(self):
        today = fields.Date.context_today(self.env.user)
        partner = self.env['res.partner'].create({'name': 'Alumno idempotente cutoff'})
        _, _, channel = self._create_course_product({
            'das_start_date': fields.Date.add(today, days=-3),
            'das_end_date': fields.Date.add(today, days=30),
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
