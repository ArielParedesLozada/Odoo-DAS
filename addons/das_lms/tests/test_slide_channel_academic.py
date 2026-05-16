# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestDasLmsSlideChannelAcademic(TransactionCase):
    """Campos académicos DAS en slide.channel."""

    def test_das_total_hours_compute(self):
        ch = self.env['slide.channel'].create({
            'name': 'Curso horas',
            'das_autonomous_hours': 10.5,
            'das_teacher_contact_hours': 4.25,
        })
        self.assertAlmostEqual(ch.das_total_hours, 14.75, places=2)

    def test_das_dates_constraint(self):
        with self.assertRaises(ValidationError):
            self.env['slide.channel'].create({
                'name': 'Curso fechas',
                'das_start_date': '2026-06-01',
                'das_end_date': '2026-05-01',
            })

    def test_das_hours_non_negative(self):
        with self.assertRaises(ValidationError):
            self.env['slide.channel'].create({
                'name': 'Curso neg',
                'das_autonomous_hours': -1.0,
            })

    def test_enrollment_modality_from_channel(self):
        partner = self.env['res.partner'].create({'name': 'Alumno Mod'})
        channel = self.env['slide.channel'].create({
            'name': 'Curso Mod',
            'das_modality': 'mixto',
        })
        scp = self.env['slide.channel.partner'].create({
            'channel_id': channel.id,
            'partner_id': partner.id,
        })
        enrollment = self.env['course.enrollment'].search([
            ('channel_partner_id', '=', scp.id),
        ], limit=1)
        self.assertTrue(enrollment)
        self.assertEqual(enrollment.modality, 'mixto')

    def test_das_academic_status_proximo_and_can_study(self):
        today = fields.Date.context_today(self.env.user)
        ch = self.env['slide.channel'].create({
            'name': 'Curso próximo',
            'das_start_date': fields.Date.add(today, days=5),
            'das_end_date': fields.Date.add(today, days=60),
        })
        self.assertEqual(ch.das_academic_status, 'proximo')
        self.assertTrue(ch.das_can_sell)
        self.assertFalse(ch.das_can_study)

    def test_das_academic_status_finalizado_blocks_new_member(self):
        today = fields.Date.context_today(self.env.user)
        ch = self.env['slide.channel'].create({
            'name': 'Curso fin',
            'das_start_date': fields.Date.add(today, days=-120),
            'das_end_date': fields.Date.add(today, days=-2),
        })
        self.assertEqual(ch.das_academic_status, 'finalizado')
        self.assertFalse(ch.das_can_sell)
        self.assertTrue(ch.das_can_study)
        partner = self.env['res.partner'].create({'name': 'Nuevo alumno'})
        with self.assertRaises(UserError):
            self.env['slide.channel.partner'].create({
                'channel_id': ch.id,
                'partner_id': partner.id,
            })

    def test_portal_lesson_access_proximo_member_blocked(self):
        from odoo.tests.common import new_test_user

        today = fields.Date.context_today(self.env.user)
        portal_user = new_test_user(
            self.env,
            'portal_proximo_user',
            email='portal_proximo@test.example.com',
            groups='base.group_portal',
        )
        ch = self.env['slide.channel'].create({
            'name': 'Curso portal próximo',
            'das_start_date': fields.Date.add(today, days=5),
            'das_end_date': fields.Date.add(today, days=40),
        })
        self.env['slide.channel.partner'].create({
            'channel_id': ch.id,
            'partner_id': portal_user.partner_id.id,
            'member_status': 'joined',
        })
        ch_portal = ch.with_user(portal_user)
        self.assertTrue(
            self.env['slide.channel']._das_lms_portal_can_study_channel(ch_portal),
        )
        self.assertFalse(
            self.env['slide.channel']._das_lms_portal_can_access_course_lessons(ch_portal),
        )
