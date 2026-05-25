# -*- coding: utf-8 -*-
from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase, new_test_user


@tagged('post_install', '-at_install')
class TestDasEmailCampaigns(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.interest = cls.env.ref('das_email_preferences.das_email_interest_technology')
        cls.interest_dev = cls.env.ref('das_email_preferences.das_email_interest_development')
        cls.category = cls.env.ref('das_email_preferences.das_email_course_category_lms')
        cls.config_birthday = cls.env.ref(
            'das_email_campaigns.das_email_campaign_config_birthday'
        )
        cls.config_upcoming = cls.env.ref(
            'das_email_campaigns.das_email_campaign_config_upcoming'
        )
        cls.config_new = cls.env.ref(
            'das_email_campaigns.das_email_campaign_config_new_courses'
        )
        cls.config_experience = cls.env.ref(
            'das_email_campaigns.das_email_campaign_config_experience'
        )
        cls.config_newsletter = cls.env.ref(
            'das_email_campaigns.das_email_campaign_config_newsletter_weekly'
        )

    def _create_portal_partner_with_prefs(self, login, birthday=None, **extra):
        user = new_test_user(
            self.env,
            login,
            email=f'{login}@test.example.com',
            groups='base.group_portal',
        )
        today = fields.Date.context_today(self.env.user)
        birthday = birthday or fields.Date.add(today, years=-30)
        values = {
            'interest_ids': [self.interest.id],
            'birthday': birthday,
            'course_category_ids': [self.category.id],
            'experience_level': 'intermediate',
            'communication_frequency': 'weekly',
            'terms_accepted': True,
            'privacy_accepted': True,
        }
        values.update(extra)
        self.env['das.email.preference'].sudo().submit_from_portal(
            user.partner_id,
            values,
        )
        return user.partner_id

    def test_birthday_campaign_idempotent(self):
        today = fields.Date.context_today(self.env.user)
        birthday = today.replace(year=1990)
        partner = self._create_portal_partner_with_prefs(
            'campaign_bday_user', birthday=birthday,
        )
        self.assertEqual(partner.das_birthday.month, today.month)
        self.assertEqual(partner.das_birthday.day, today.day)
        Runner = self.env['das.email.campaign.runner']
        count1 = Runner._run_birthday(self.config_birthday)
        self.assertGreaterEqual(count1, 1)
        count2 = Runner._run_birthday(self.config_birthday)
        self.assertEqual(count2, 0)
        logs = self.env['das.email.campaign.log'].search([
            ('partner_id', '=', partner.id),
            ('config_id', '=', self.config_birthday.id),
        ])
        self.assertEqual(len(logs), 1)
        self.assertTrue(logs.mailing_id)

    def test_preference_completion_syncs_all_segment_lists(self):
        partner = self._create_portal_partner_with_prefs(
            'campaign_sync_user',
            interest_ids=[self.interest.id, self.interest_dev.id],
        )
        contact = self.env['mailing.contact'].sudo().search([
            ('email', '=', partner.email),
        ], limit=1)
        self.assertTrue(contact)
        expected_lists = [
            'das_email_campaigns.mailing_list_das_opted_in',
            'das_email_campaigns.mailing_list_das_interest_technology',
            'das_email_campaigns.mailing_list_das_interest_development',
            'das_email_campaigns.mailing_list_das_category_lms',
            'das_email_campaigns.mailing_list_das_level_intermediate',
        ]
        for xml_id in expected_lists:
            lst = self.env.ref(xml_id)
            sub = self.env['mailing.subscription'].sudo().search([
                ('contact_id', '=', contact.id),
                ('list_id', '=', lst.id),
            ])
            self.assertTrue(sub, 'Falta suscripción a %s' % xml_id)

    def test_frequency_blocks_monthly_user_on_weekly_newsletter(self):
        partner = self._create_portal_partner_with_prefs('campaign_freq_user')
        partner.write({'das_communication_frequency': 'monthly'})
        Runner = self.env['das.email.campaign.runner']
        allowed = Runner._partner_matches_frequency(
            partner, 'newsletter', 'weekly',
        )
        self.assertFalse(allowed)

    def test_cron_daily_executes_birthday_and_upcoming(self):
        today = fields.Date.context_today(self.env.user)
        partner = self._create_portal_partner_with_prefs(
            'campaign_cron_daily',
            birthday=today.replace(year=1988),
        )
        channel = self.env['slide.channel'].sudo().create({
            'name': 'Curso Cron DAS Test',
            'website_published': True,
            'das_start_date': fields.Date.add(today, days=2),
            'das_email_category_ids': [(6, 0, [self.category.id])],
            'das_email_interest_ids': [(6, 0, [self.interest.id])],
        })
        self.assertTrue(channel.das_email_marketing_configured)
        Config = self.env['das.email.campaign.config']
        total = Config.cron_run_daily_campaigns()
        self.assertGreaterEqual(total, 1)
        logs = self.env['das.email.campaign.log'].search([
            ('partner_id', '=', partner.id),
        ])
        self.assertTrue(logs)

    def test_new_courses_weekly_idempotent(self):
        today = fields.Date.context_today(self.env.user)
        partner = self._create_portal_partner_with_prefs('campaign_new_course')
        channel = self.env['slide.channel'].sudo().create({
            'name': 'Curso Nuevo DAS Marketing',
            'website_published': True,
            'das_email_category_ids': [(6, 0, [self.category.id])],
            'das_email_interest_ids': [(6, 0, [self.interest.id])],
        })
        Runner = self.env['das.email.campaign.runner']
        count1 = Runner._run_new_courses(self.config_new)
        self.assertGreaterEqual(count1, 1)
        count2 = Runner._run_new_courses(self.config_new)
        self.assertEqual(count2, 0)

    def test_experience_campaign_respects_level(self):
        partner = self._create_portal_partner_with_prefs(
            'campaign_experience',
            experience_level='intermediate',
        )
        Runner = self.env['das.email.campaign.runner']
        count = Runner._run_experience(self.config_experience)
        self.assertGreaterEqual(count, 1)
        log = self.env['das.email.campaign.log'].search([
            ('partner_id', '=', partner.id),
            ('config_id', '=', self.config_experience.id),
        ], limit=1)
        self.assertTrue(log.mailing_id)

    def test_channel_auto_configures_email_marketing(self):
        channel = self.env['slide.channel'].sudo().create({
            'name': 'Desarrollo de Software Avanzado',
            'website_published': True,
            'das_modality': 'grabado',
        })
        self.assertTrue(channel.das_email_interest_ids)
        self.assertTrue(channel.das_email_category_ids)

    def test_birthday_requires_comm_email(self):
        today = fields.Date.context_today(self.env.user)
        partner = self._create_portal_partner_with_prefs(
            'campaign_no_email',
            birthday=today.replace(year=1985),
        )
        pref = self.env['das.email.preference'].sudo().search([
            ('partner_id', '=', partner.id),
        ], limit=1)
        pref.write({'comm_email': False})
        partner.invalidate_recordset()
        Runner = self.env['das.email.campaign.runner']
        count = Runner._run_birthday(self.config_birthday)
        logs = self.env['das.email.campaign.log'].search([
            ('partner_id', '=', partner.id),
            ('config_id', '=', self.config_birthday.id),
        ])
        self.assertFalse(logs)
