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
        cls.interest_mkt = cls.env.ref('das_email_preferences.das_email_interest_marketing')
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
        cls.config_newsletter_monthly = cls.env.ref(
            'das_email_campaigns.das_email_campaign_config_newsletter_monthly'
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

    def _create_channel(self, name, **extra):
        vals = {
            'name': name,
            'website_published': True,
            'das_email_category_ids': [(6, 0, [self.category.id])],
            'das_email_interest_ids': [(6, 0, [self.interest.id])],
        }
        vals.update(extra)
        return self.env['slide.channel'].sudo().create(vals)

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
        pref = self.env['das.email.preference'].sudo().search([
            ('partner_id', '=', partner.id),
        ], limit=1)
        pref.write({'communication_frequency': 'monthly'})
        partner.invalidate_recordset()
        Runner = self.env['das.email.campaign.runner']
        allowed = Runner._partner_matches_frequency(
            partner, 'newsletter', 'weekly',
        )
        self.assertFalse(allowed)

    def test_monthly_user_receives_monthly_newsletter_only(self):
        partner = self._create_portal_partner_with_prefs('campaign_monthly_user')
        pref = self.env['das.email.preference'].sudo().search([
            ('partner_id', '=', partner.id),
        ], limit=1)
        pref.write({'communication_frequency': 'monthly'})
        partner.invalidate_recordset()
        Runner = self.env['das.email.campaign.runner']
        self.assertTrue(Runner._partner_matches_frequency(
            partner, 'newsletter', 'monthly',
        ))
        count_weekly = Runner._run_newsletter(self.config_newsletter)
        logs_weekly = self.env['das.email.campaign.log'].search([
            ('partner_id', '=', partner.id),
            ('config_id', '=', self.config_newsletter.id),
        ])
        self.assertEqual(logs_weekly, self.env['das.email.campaign.log'])
        count_monthly = Runner._run_newsletter(self.config_newsletter_monthly)
        self.assertGreaterEqual(count_monthly, 1)

    def test_cron_daily_executes_birthday_and_upcoming(self):
        today = fields.Date.context_today(self.env.user)
        partner = self._create_portal_partner_with_prefs(
            'campaign_cron_daily',
            birthday=today.replace(year=1988),
        )
        self._create_channel(
            'Curso Cron DAS Test',
            das_start_date=fields.Date.add(today, days=2),
        )
        Config = self.env['das.email.campaign.config']
        total = Config.cron_run_daily_campaigns()
        self.assertGreaterEqual(total, 1)
        logs = self.env['das.email.campaign.log'].search([
            ('partner_id', '=', partner.id),
        ])
        self.assertTrue(logs)

    def test_upcoming_idempotent_per_course(self):
        today = fields.Date.context_today(self.env.user)
        partner = self._create_portal_partner_with_prefs('campaign_upcoming_idem')
        ch1 = self._create_channel(
            'Curso Próximo A',
            das_start_date=fields.Date.add(today, days=2),
        )
        ch2 = self._create_channel(
            'Curso Próximo B',
            das_start_date=fields.Date.add(today, days=3),
        )
        Runner = self.env['das.email.campaign.runner']
        count1 = Runner._run_upcoming(self.config_upcoming)
        self.assertGreaterEqual(count1, 2)
        count2 = Runner._run_upcoming(self.config_upcoming)
        self.assertEqual(count2, 0)
        logs = self.env['das.email.campaign.log'].search([
            ('partner_id', '=', partner.id),
            ('config_id', '=', self.config_upcoming.id),
        ])
        self.assertEqual(len(logs), 2)
        channel_refs = set(logs.mapped('channel_ref_id'))
        self.assertEqual(channel_refs, {ch1.id, ch2.id})

    def test_upcoming_skips_partner_without_matching_interest(self):
        today = fields.Date.context_today(self.env.user)
        workshops = self.env.ref(
            'das_email_preferences.das_email_course_category_workshops'
        )
        partner = self._create_portal_partner_with_prefs(
            'campaign_upcoming_nomatch',
            interest_ids=[self.interest_mkt.id],
            course_category_ids=[workshops.id],
        )
        channel = self._create_channel(
            'Curso Solo Tecnología',
            das_start_date=fields.Date.add(today, days=2),
            das_email_category_ids=[(6, 0, [self.category.id])],
            das_email_interest_ids=[(6, 0, [self.interest.id])],
        )
        Runner = self.env['das.email.campaign.runner']
        Runner._run_upcoming(self.config_upcoming)
        logs = self.env['das.email.campaign.log'].search([
            ('partner_id', '=', partner.id),
            ('channel_ref_id', '=', channel.id),
        ])
        self.assertFalse(logs)

    def test_new_courses_weekly_idempotent(self):
        partner = self._create_portal_partner_with_prefs('campaign_new_course')
        self._create_channel('Curso Nuevo DAS Marketing')
        Runner = self.env['das.email.campaign.runner']
        count1 = Runner._run_new_courses(self.config_new)
        self.assertGreaterEqual(count1, 1)
        count2 = Runner._run_new_courses(self.config_new)
        self.assertEqual(count2, 0)

    def test_new_courses_uses_published_date(self):
        today = fields.Date.context_today(self.env.user)
        old_date = fields.Date.add(today, days=-60)
        partner = self._create_portal_partner_with_prefs('campaign_old_publish')
        channel = self._create_channel(
            'Curso Antiguo No Nuevo',
            das_email_published_date=old_date,
        )
        Runner = self.env['das.email.campaign.runner']
        Runner._run_new_courses(self.config_new)
        logs = self.env['das.email.campaign.log'].search([
            ('partner_id', '=', partner.id),
            ('channel_ref_id', '=', channel.id),
            ('config_id', '=', self.config_new.id),
        ])
        self.assertFalse(logs)

    def test_experience_campaign_respects_level_and_interest(self):
        partner = self._create_portal_partner_with_prefs(
            'campaign_experience',
            experience_level='intermediate',
        )
        self._create_channel(
            'Curso Intermedio Tecnología',
            das_experience_level='intermediate',
        )
        Runner = self.env['das.email.campaign.runner']
        count = Runner._run_experience(self.config_experience)
        self.assertGreaterEqual(count, 1)
        log = self.env['das.email.campaign.log'].search([
            ('partner_id', '=', partner.id),
            ('config_id', '=', self.config_experience.id),
        ], limit=1)
        self.assertTrue(log.mailing_id)
        self.assertIn('_das_email_campaign_course_block', log.mailing_id.body_html)

    def test_experience_body_has_per_partner_course_block(self):
        partner = self._create_portal_partner_with_prefs(
            'campaign_exp_dynamic',
            interest_ids=[self.interest.id],
            experience_level='beginner',
        )
        self._create_channel(
            'Curso Básico Tech Dinámico',
            das_experience_level='beginner',
            das_email_interest_ids=[(6, 0, [self.interest.id])],
        )
        Runner = self.env['das.email.campaign.runner']
        Runner._run_experience(self.config_experience)
        log = self.env['das.email.campaign.log'].search([
            ('partner_id', '=', partner.id),
            ('config_id', '=', self.config_experience.id),
        ], limit=1)
        self.assertIn('_das_email_campaign_course_block', log.mailing_id.body_html)
        block = partner._das_email_campaign_course_block('experience', 'Test', 5)
        self.assertIn('Curso Básico Tech Dinámico', block)

    def test_partners_with_different_interests_get_different_course_blocks(self):
        workshops = self.env.ref(
            'das_email_preferences.das_email_course_category_workshops'
        )
        p_tech = self._create_portal_partner_with_prefs(
            'campaign_block_tech',
            interest_ids=[self.interest.id],
            course_category_ids=[self.category.id],
        )
        p_dev = self._create_portal_partner_with_prefs(
            'campaign_block_dev',
            interest_ids=[self.interest_dev.id],
            course_category_ids=[workshops.id],
        )
        self._create_channel(
            'Solo Tech Block',
            das_email_category_ids=[(6, 0, [self.category.id])],
            das_email_interest_ids=[(6, 0, [self.interest.id])],
        )
        self._create_channel(
            'Solo Dev Block',
            das_email_category_ids=[(6, 0, [workshops.id])],
            das_email_interest_ids=[(6, 0, [self.interest_dev.id])],
        )
        tech_block = p_tech._das_email_campaign_course_block('newsletter', 'T', 5)
        dev_block = p_dev._das_email_campaign_course_block('newsletter', 'T', 5)
        self.assertIn('Solo Tech Block', tech_block)
        self.assertNotIn('Solo Dev Block', tech_block)
        self.assertIn('Solo Dev Block', dev_block)

    def test_sync_removes_stale_list_subscriptions(self):
        partner = self._create_portal_partner_with_prefs(
            'campaign_stale_list',
            interest_ids=[self.interest.id],
        )
        contact = self.env['mailing.contact'].sudo().search([
            ('email', '=', partner.email),
        ], limit=1)
        design_list = self.env.ref(
            'das_email_campaigns.mailing_list_das_interest_design'
        )
        self.env['mailing.subscription'].sudo().create({
            'contact_id': contact.id,
            'list_id': design_list.id,
        })
        partner._das_sync_email_marketing_segments()
        stale = self.env['mailing.subscription'].sudo().search([
            ('contact_id', '=', contact.id),
            ('list_id', '=', design_list.id),
        ])
        self.assertFalse(stale)

    def test_five_auto_campaign_configs_active(self):
        Config = self.env['das.email.campaign.config']
        active = Config._das_ensure_active_campaign_configs()
        codes = set(active.mapped('code'))
        self.assertTrue({'birthday', 'upcoming', 'new_courses', 'experience', 'newsletter'} <= codes)

    def test_channel_auto_configures_email_marketing(self):
        channel = self.env['slide.channel'].sudo().create({
            'name': 'Desarrollo de Software Avanzado',
            'website_published': True,
            'das_modality': 'grabado',
        })
        self.assertTrue(channel.das_email_interest_ids)
        self.assertTrue(channel.das_email_category_ids)
        self.assertEqual(channel.das_experience_level, 'advanced')

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
        Runner._run_birthday(self.config_birthday)
        logs = self.env['das.email.campaign.log'].search([
            ('partner_id', '=', partner.id),
            ('config_id', '=', self.config_birthday.id),
        ])
        self.assertFalse(logs)

    def test_failed_log_allows_retry(self):
        today = fields.Date.context_today(self.env.user)
        partner = self._create_portal_partner_with_prefs(
            'campaign_retry',
            birthday=today.replace(year=1992),
        )
        period_key = self.env['das.email.campaign.runner']._period_key_daily(today)
        self.env['das.email.campaign.log'].sudo().create({
            'config_id': self.config_birthday.id,
            'partner_id': partner.id,
            'period_key': period_key,
            'channel_ref_id': 0,
            'state': 'failed',
        })
        Runner = self.env['das.email.campaign.runner']
        count = Runner._run_birthday(self.config_birthday)
        self.assertGreaterEqual(count, 1)
        logs = self.env['das.email.campaign.log'].search([
            ('partner_id', '=', partner.id),
            ('config_id', '=', self.config_birthday.id),
            ('state', 'in', ('queued', 'sent')),
        ])
        self.assertTrue(logs)

    def test_trace_sync_updates_log_from_mailing_trace(self):
        partner = self._create_portal_partner_with_prefs('campaign_trace')
        Runner = self.env['das.email.campaign.runner']
        Runner._run_newsletter(self.config_newsletter)
        log = self.env['das.email.campaign.log'].search([
            ('partner_id', '=', partner.id),
            ('config_id', '=', self.config_newsletter.id),
        ], limit=1)
        self.assertTrue(log.mailing_id)
        self.env['mailing.trace'].sudo().create({
            'mass_mailing_id': log.mailing_id.id,
            'model': 'res.partner',
            'res_id': partner.id,
            'email': partner.email,
            'trace_status': 'open',
        })
        self.env['das.email.campaign.log']._sync_trace_status_from_mailing(log.mailing_id)
        log.invalidate_recordset()
        self.assertEqual(log.trace_status, 'open')
        self.assertEqual(log.state, 'sent')
