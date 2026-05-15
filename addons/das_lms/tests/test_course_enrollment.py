# -*- coding: utf-8 -*-
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestDasLmsEnrollment(TransactionCase):
    """Seguimiento DAS vinculado a slide.channel.partner."""

    def test_channel_partner_creates_enrollment_mirror(self):
        partner = self.env['res.partner'].create({'name': 'Alumno DAS'})
        channel = self.env['slide.channel'].create({'name': 'Curso DAS'})
        scp = self.env['slide.channel.partner'].create({
            'channel_id': channel.id,
            'partner_id': partner.id,
        })
        enrollment = self.env['course.enrollment'].search([
            ('channel_partner_id', '=', scp.id),
        ], limit=1)
        self.assertTrue(enrollment)
        self.assertEqual(enrollment.student_id, partner)
        self.assertEqual(enrollment.course_id, channel)
        self.assertTrue(enrollment.last_sync_at)

    def test_sync_from_elearning_counts_and_action(self):
        partner = self.env['res.partner'].create({'name': 'Alumno Sync'})
        channel = self.env['slide.channel'].create({'name': 'Curso Sync'})
        self.env['slide.channel.partner'].create({
            'channel_id': channel.id,
            'partner_id': partner.id,
        })
        action = self.env['course.enrollment'].action_sync_from_elearning()
        self.assertEqual(action.get('type'), 'ir.actions.client')
        self.assertEqual(action.get('tag'), 'display_notification')
        n = self.env['course.enrollment'].search_count([
            ('student_id', '=', partner.id),
            ('course_id', '=', channel.id),
        ])
        self.assertEqual(n, 1)

    def test_unique_channel_partner(self):
        from psycopg2 import IntegrityError

        partner = self.env['res.partner'].create({'name': 'Alumno U'})
        channel = self.env['slide.channel'].create({'name': 'Curso U'})
        scp = self.env['slide.channel.partner'].create({
            'channel_id': channel.id,
            'partner_id': partner.id,
        })
        self.assertEqual(
            self.env['course.enrollment'].search_count([('channel_partner_id', '=', scp.id)]),
            1,
            'El hook debe crear exactamente un espejo DAS.',
        )
        with self.assertRaises(IntegrityError):
            with self.env.cr.savepoint():
                self.env['course.enrollment'].create({
                    'channel_partner_id': scp.id,
                    'modality': 'en_vivo',
                })

    def test_portal_can_study_channel_gate(self):
        from odoo.tests.common import new_test_user

        channel = self.env['slide.channel'].create({
            'name': 'Curso Portal Gate',
            'website_published': True,
            'visibility': 'connected',
        })
        portal_user = new_test_user(
            self.env,
            'portal_gate_user',
            email='portal_gate@test.example.com',
            groups='base.group_portal',
        )
        ch_portal = channel.with_user(portal_user)
        self.assertFalse(
            self.env['slide.channel']._das_lms_portal_can_study_channel(ch_portal),
        )
        self.env['slide.channel.partner'].create({
            'channel_id': channel.id,
            'partner_id': portal_user.partner_id.id,
            'member_status': 'joined',
        })
        ch_portal = channel.with_user(portal_user)
        self.assertTrue(
            self.env['slide.channel']._das_lms_portal_can_study_channel(ch_portal),
        )

    def test_dashboard_default_get(self):
        partner = self.env['res.partner'].create({'name': 'Dash Alumno'})
        channel = self.env['slide.channel'].create({'name': 'Dash Curso'})
        self.env['slide.channel.partner'].create({
            'channel_id': channel.id,
            'partner_id': partner.id,
        })
        self.env['course.enrollment'].action_sync_from_elearning()
        dash = self.env['das.lms.academic.dashboard'].create({})
        self.assertGreaterEqual(dash.total_enrollments, 1)
        self.assertTrue(dash.line_ids)

    def test_advanced_analytics_panel(self):
        partner = self.env['res.partner'].create({'name': 'Ana Panel'})
        channel = self.env['slide.channel'].create({'name': 'Curso Panel'})
        self.env['slide.channel.partner'].create({
            'channel_id': channel.id,
            'partner_id': partner.id,
        })
        self.env['course.enrollment'].action_sync_from_elearning()
        panel = self.env['das.lms.advanced.analytics'].create({})
        self.assertGreaterEqual(panel.total_enrollments, 1)
        self.assertTrue(panel.line_ids)
        self.assertTrue(panel.header_date_display)
        self.assertTrue(panel.line_ids[0].course_health)
        tech = self.env.ref('das_lms.action_course_enrollment_analytics_technical').read()[0]
        self.assertEqual(tech.get('res_model'), 'course.enrollment')
        self.assertIn('list', tech.get('view_mode', ''))
