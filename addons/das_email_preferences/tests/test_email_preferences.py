# -*- coding: utf-8 -*-
from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase, new_test_user


@tagged('post_install', '-at_install')
class TestDasEmailPreferences(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.interest_tech = cls.env.ref('das_email_preferences.das_email_interest_technology')
        cls.interest_dev = cls.env.ref('das_email_preferences.das_email_interest_development')
        cls.category_lms = cls.env.ref('das_email_preferences.das_email_course_category_lms')

    def _create_portal_user(self, login):
        return new_test_user(
            self.env,
            login,
            email=f'{login}@test.example.com',
            groups='base.group_portal',
        )

    def test_user_creation_creates_preference_draft(self):
        user = self._create_portal_user('pref_portal_new')
        pref = self.env['das.email.preference'].sudo().search(
            [('partner_id', '=', user.partner_id.id)],
            limit=1,
        )
        self.assertTrue(pref)
        self.assertFalse(pref.completed)
        self.assertTrue(user._das_must_complete_email_preferences())

    def test_submit_preferences_success(self):
        user = self._create_portal_user('pref_portal_submit')
        today = fields.Date.context_today(self.env.user)
        birthday = fields.Date.add(today, years=-25)
        pref = self.env['das.email.preference'].sudo().submit_from_portal(
            user.partner_id,
            {
                'interest_ids': [self.interest_tech.id, self.interest_dev.id],
                'birthday': birthday,
                'comm_email': True,
                'comm_sms': False,
                'comm_push': False,
                'experience_level': 'intermediate',
                'course_category_ids': [self.category_lms.id],
                'communication_frequency': 'weekly',
                'terms_accepted': True,
                'privacy_accepted': True,
            },
            ip_address='127.0.0.1',
        )
        self.assertTrue(pref.completed)
        self.assertTrue(pref.completed_on)
        self.assertEqual(pref.completed_ip, '127.0.0.1')
        partner = user.partner_id
        self.assertTrue(partner.das_preference_completed)
        self.assertEqual(partner.das_birthday, birthday)
        self.assertIn(self.interest_tech, partner.das_interest_ids)
        self.assertFalse(user._das_must_complete_email_preferences())

    def test_submit_without_interests_raises(self):
        user = self._create_portal_user('pref_portal_fail')
        today = fields.Date.context_today(self.env.user)
        with self.assertRaises(ValidationError):
            self.env['das.email.preference'].sudo().submit_from_portal(
                user.partner_id,
                {
                    'interest_ids': [],
                    'birthday': fields.Date.add(today, years=-20),
                    'comm_email': True,
                    'terms_accepted': True,
                    'privacy_accepted': True,
                },
            )

    def test_submit_always_uses_email_channel(self):
        """Sin UI de canales: el guardado fuerza comunicación por correo."""
        user = self._create_portal_user('pref_portal_emailonly')
        today = fields.Date.context_today(self.env.user)
        pref = self.env['das.email.preference'].sudo().submit_from_portal(
            user.partner_id,
            {
                'interest_ids': [self.interest_tech.id],
                'birthday': fields.Date.add(today, years=-22),
                'terms_accepted': True,
                'privacy_accepted': True,
            },
        )
        self.assertTrue(pref.comm_email)
        self.assertFalse(pref.comm_sms)
        self.assertFalse(pref.comm_push)
        self.assertEqual(pref.communication_frequency, 'weekly')

    def test_submit_expert_experience_level(self):
        user = self._create_portal_user('pref_portal_expert')
        today = fields.Date.context_today(self.env.user)
        pref = self.env['das.email.preference'].sudo().submit_from_portal(
            user.partner_id,
            {
                'interest_ids': [self.interest_tech.id],
                'birthday': fields.Date.add(today, years=-40),
                'experience_level': 'expert',
                'terms_accepted': True,
                'privacy_accepted': True,
            },
        )
        self.assertEqual(pref.experience_level, 'expert')
        self.assertEqual(user.partner_id.das_experience_level, 'expert')

    def test_admin_user_exempt_from_onboarding(self):
        admin = self.env.ref('base.user_admin')
        self.assertFalse(admin._das_must_complete_email_preferences())
        self.assertFalse(admin._das_is_portal_student_user())

    def test_internal_user_exempt_from_onboarding(self):
        user = new_test_user(
            self.env,
            'pref_internal_user',
            email='pref_internal_user@test.example.com',
            groups='base.group_user',
        )
        self.assertFalse(user._das_is_portal_student_user())
        self.assertFalse(user._das_must_complete_email_preferences())
        pref = self.env['das.email.preference'].sudo().search([
            ('partner_id', '=', user.partner_id.id),
        ])
        self.assertFalse(pref)

    def test_portal_student_detection(self):
        portal = self._create_portal_user('pref_portal_detect')
        self.assertTrue(portal._das_is_portal_student_user())
        self.assertFalse(portal._das_email_preference_exempt_user())
