# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
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
