# -*- coding: utf-8 -*-
from odoo.tests import tagged
from odoo.tests.common import TransactionCase, new_test_user


@tagged('post_install', '-at_install')
class TestCourseEnrollmentStudentsOnly(TransactionCase):
    """Inscripciones DAS: solo alumnos reales, no usuarios internos."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.channel = cls.env['slide.channel'].create({'name': 'Curso filtro alumnos'})
        cls.student_partner = cls.env['res.partner'].create({
            'name': 'Alumno Portal',
            'email': 'alumno.filtro@test.example.com',
        })
        cls.instructor_user = new_test_user(
            cls.env,
            'instructor_filtro_enrollment',
            email='instructor.filtro@test.example.com',
            groups='base.group_user,website_slides.group_website_slides_officer',
        )

    def test_portal_student_is_das_student(self):
        portal_user = new_test_user(
            self.env,
            'portal_filtro_enrollment',
            email='portal.filtro@test.example.com',
            groups='base.group_portal',
        )
        self.assertTrue(portal_user.partner_id._das_lms_is_academic_student_partner())

    def test_internal_instructor_is_not_das_student(self):
        self.assertFalse(
            self.instructor_user.partner_id._das_lms_is_academic_student_partner()
        )

    def test_instructor_channel_member_not_in_enrollments(self):
        self.env['slide.channel.partner'].create({
            'channel_id': self.channel.id,
            'partner_id': self.instructor_user.partner_id.id,
        })
        self.env['slide.channel.partner'].create({
            'channel_id': self.channel.id,
            'partner_id': self.student_partner.id,
        })
        self.env['course.enrollment'].action_sync_from_elearning()

        instructor_rows = self.env['course.enrollment'].search([
            ('course_id', '=', self.channel.id),
            ('student_id', '=', self.instructor_user.partner_id.id),
        ])
        self.assertFalse(instructor_rows)

        student_rows = self.env['course.enrollment'].search([
            ('course_id', '=', self.channel.id),
            ('student_id', '=', self.student_partner.id),
        ])
        self.assertEqual(len(student_rows), 1)
        self.assertTrue(student_rows.is_das_student)

    def test_course_website_url_uses_relative_path(self):
        channel = self.env['slide.channel'].create({
            'name': 'Curso URL',
            'website_url': 'http://forward-funeral-functional-percent.trycloudflare.com/slides/legacy-slug',
        })
        scp = self.env['slide.channel.partner'].create({
            'channel_id': channel.id,
            'partner_id': self.student_partner.id,
        })
        enrollment = self.env['course.enrollment'].search([
            ('channel_partner_id', '=', scp.id),
        ], limit=1)
        self.assertTrue(enrollment.course_website_url.startswith('/slides/'))
        self.assertNotIn('trycloudflare', enrollment.course_website_url or '')

    def test_dashboard_ignores_instructor_members(self):
        self.env['slide.channel.partner'].create({
            'channel_id': self.channel.id,
            'partner_id': self.instructor_user.partner_id.id,
        })
        self.env['slide.channel.partner'].create({
            'channel_id': self.channel.id,
            'partner_id': self.student_partner.id,
        })
        self.env['course.enrollment'].action_sync_from_elearning()
        dash = self.env['das.lms.academic.dashboard'].create({})
        channel_line = dash.line_ids.filtered(lambda l: l.course_id == self.channel)
        self.assertEqual(channel_line.total_enrolled, 1)
