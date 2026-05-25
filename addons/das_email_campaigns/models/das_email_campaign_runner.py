# -*- coding: utf-8 -*-
import logging
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.osv import expression

from .das_email_template_layout import (
    das_email_render,
    das_email_render_course_cards_html,
    das_email_subject,
)

_logger = logging.getLogger(__name__)

# Campañas permitidas por frecuencia de comunicación del usuario.
_FREQUENCY_ALLOWED = {
    'new_courses': {'daily', 'weekly', 'biweekly', 'monthly', 'promotions'},
    'experience': {'daily', 'weekly', 'biweekly', 'monthly', 'promotions'},
    'upcoming': {'daily', 'weekly', 'biweekly', 'monthly', 'promotions', 'minimal'},
    'newsletter': {'daily', 'weekly', 'biweekly', 'monthly'},
    'birthday': None,  # siempre permitido si comm_email
}

_EXPERIENCE_LABELS = {
    'beginner': 'Básico',
    'intermediate': 'Intermedio',
    'advanced': 'Avanzado',
    'expert': 'Experto',
}


class DasEmailCampaignRunner(models.AbstractModel):
    _name = 'das.email.campaign.runner'
    _description = 'Motor de campañas automáticas DAS Email Marketing'

    # -------------------------------------------------------------------------
    # Utilidades de periodo e idempotencia
    # -------------------------------------------------------------------------

    @api.model
    def _today(self):
        return fields.Date.context_today(self)

    @api.model
    def _period_key_daily(self, day=None):
        day = day or self._today()
        return fields.Date.to_string(day)

    @api.model
    def _period_key_weekly(self, day=None):
        day = day or self._today()
        iso = day.isocalendar()
        return '%04d-W%02d' % (iso[0], iso[1])

    @api.model
    def _period_key_monthly(self, day=None):
        day = day or self._today()
        return day.strftime('%Y-%m')

    @api.model
    def _period_key_for_config(self, config, day=None):
        day = day or self._today()
        if config.code == 'birthday':
            return self._period_key_daily(day)
        if config.cron_interval == 'monthly':
            return self._period_key_monthly(day)
        if config.cron_interval == 'weekly':
            return self._period_key_weekly(day)
        return self._period_key_daily(day)

    @api.model
    def _base_partner_domain(self):
        return [
            ('das_comm_email', '=', True),
            ('das_preference_completed', '=', True),
            ('email', '!=', False),
        ]

    @api.model
    def _partner_matches_frequency(self, partner, campaign_type, cron_interval):
        if campaign_type == 'birthday':
            return True
        freq = partner.das_communication_frequency or 'weekly'
        allowed = _FREQUENCY_ALLOWED.get(campaign_type, set())
        if allowed is None:
            return True
        if freq not in allowed:
            return False
        if freq == 'biweekly':
            week_num = self._today().isocalendar()[1]
            if week_num % 2 == 0:
                return cron_interval in ('weekly', 'daily')
            return cron_interval == 'monthly'
        if freq == 'monthly' and cron_interval == 'weekly':
            return False
        if freq == 'promotions' and campaign_type == 'newsletter':
            return False
        if freq == 'minimal' and campaign_type != 'upcoming':
            return False
        return True

    @api.model
    def _filter_partners_by_frequency(self, partners, campaign_type, cron_interval):
        return partners.filtered(
            lambda p: self._partner_matches_frequency(p, campaign_type, cron_interval)
        )

    @api.model
    def _exclude_logged_partners(self, partner_ids, config, period_key, channel_id=None):
        if not partner_ids:
            return []
        domain = [
            ('config_id', '=', config.id),
            ('period_key', '=', period_key),
            ('partner_id', 'in', partner_ids),
            ('state', 'in', ('queued', 'sent')),
        ]
        if channel_id:
            domain.append(('channel_ref_id', '=', channel_id))
        else:
            domain.append(('channel_ref_id', '=', 0))
        logs = self.env['das.email.campaign.log'].sudo().search(domain)
        sent_ids = set(logs.mapped('partner_id').ids)
        return [pid for pid in partner_ids if pid not in sent_ids]

    @api.model
    def _partners_for_channel(self, channel):
        """Contactos cuyo interés o categoría coincide con el curso."""
        Partner = self.env['res.partner'].sudo()
        domain = self._base_partner_domain()
        cat_ids = channel.das_email_category_ids.ids
        interest_ids = channel.das_email_interest_ids.ids
        if cat_ids and interest_ids:
            match_domain = expression.OR([
                [('das_course_category_ids', 'in', cat_ids)],
                [('das_interest_ids', 'in', interest_ids)],
            ])
        elif cat_ids:
            match_domain = [('das_course_category_ids', 'in', cat_ids)]
        elif interest_ids:
            match_domain = [('das_interest_ids', 'in', interest_ids)]
        else:
            return Partner.browse()
        return Partner.search(expression.AND([domain, match_domain]))

    @api.model
    def _render_partner_body(self, template, partner, extra_ctx=None):
        ctx = dict(extra_ctx or {}, object=partner)
        if template:
            return template.sudo()._render_field('body_html', [partner.id], compute_lang=True)[partner.id]
        return ''

    @api.model
    def _das_build_campaign_body(self, variant, channels=None, channels_title='Cursos destacados'):
        extra = ''
        if channels:
            ch = channels if hasattr(channels, '_name') else self.env['slide.channel'].browse(channels)
            extra = das_email_render_course_cards_html(ch, self.env, title=channels_title)
        return das_email_render(variant, self.env, extra_html=extra)

    @api.model
    def _create_mailing_and_logs(self, config, subject, body_html, partner_ids, period_key, channel=None):
        partner_ids = list(set(partner_ids))
        if not partner_ids:
            return self.env['mailing.mailing']

        partner_model = self.env['ir.model']._get('res.partner')
        mailing_domain = expression.AND([
            self._base_partner_domain(),
            [('id', 'in', partner_ids)],
        ])
        mailing_vals = {
            'name': '[DAS Auto] %s · %s' % (config.name, period_key),
            'subject': subject,
            'body_html': body_html,
            'mailing_model_id': partner_model.id,
            'mailing_domain': repr(mailing_domain),
            'reply_to_mode': 'new',
            'das_campaign_config_id': config.id,
            'das_campaign_period_key': period_key,
            'das_campaign_channel_id': channel.id if channel else False,
        }
        mailing_vals.update(self.env['mailing.mailing']._das_default_outgoing_mail_values())
        mailing = self.env['mailing.mailing'].sudo().create(mailing_vals)
        Log = self.env['das.email.campaign.log'].sudo()
        log_vals = []
        for pid in partner_ids:
            log_vals.append({
                'config_id': config.id,
                'partner_id': pid,
                'channel_id': channel.id if channel else False,
                'channel_ref_id': channel.id if channel else 0,
                'period_key': period_key,
                'mailing_id': mailing.id,
                'state': 'queued',
            })
        Log.create(log_vals)
        mailing.action_launch()
        config.sudo().write({'last_run_date': self._today()})
        return mailing

    # -------------------------------------------------------------------------
    # Campañas concretas
    # -------------------------------------------------------------------------

    @api.model
    def _run_birthday(self, config):
        today = self._today()
        period_key = self._period_key_daily(today)
        Partner = self.env['res.partner'].sudo()
        partners = Partner.search(expression.AND([
            self._base_partner_domain(),
            [('das_birthday', '!=', False)],
        ]))
        birthday_partners = partners.filtered(
            lambda p: p.das_birthday
            and p.das_birthday.month == today.month
            and p.das_birthday.day == today.day
        )
        partner_ids = self._exclude_logged_partners(
            birthday_partners.ids, config, period_key,
        )
        if not partner_ids:
            return 0
        subject = das_email_subject('birthday')
        body = self._das_build_campaign_body('birthday')
        self._create_mailing_and_logs(config, subject, body, partner_ids, period_key)
        return len(partner_ids)

    @api.model
    def _run_upcoming(self, config):
        today = self._today()
        period_key = self._period_key_daily(today)
        end = today + timedelta(days=config.days_before_start or 3)
        Channel = self.env['slide.channel'].sudo()
        channels = Channel.search([
            ('website_published', '=', True),
            ('das_start_date', '>=', today),
            ('das_start_date', '<=', end),
        ])
        channels = channels.filtered(lambda c: c.das_academic_status == 'proximo')
        total = 0
        for channel in channels:
            partners = self._partners_for_channel(channel)
            partners = self._filter_partners_by_frequency(
                partners, config.code, config.cron_interval,
            )
            partner_ids = self._exclude_logged_partners(
                partners.ids, config, period_key, channel_id=channel.id,
            )
            if not partner_ids:
                continue
            start_str = fields.Date.to_string(channel.das_start_date)
            subject = _('⏰ %(course)s inicia el %(date)s · Reserva tu cupo',
                        course=channel.name, date=start_str)
            body = self._das_build_campaign_body(
                'upcoming', channels=channel, channels_title=_('Curso próximo a iniciar'),
            )
            self._create_mailing_and_logs(
                config, subject, body, partner_ids, period_key, channel=channel,
            )
            total += len(partner_ids)
        return total

    @api.model
    def _run_new_courses(self, config):
        today = self._today()
        period_key = self._period_key_for_config(config, today)
        window = config.new_course_window_days or 14
        since = today - timedelta(days=window)
        since_dt = fields.Datetime.to_datetime(since)
        Channel = self.env['slide.channel'].sudo()
        channels = Channel.search([
            ('website_published', '=', True),
            ('create_date', '>=', fields.Datetime.to_string(since_dt)),
        ])
        total = 0
        for channel in channels:
            partners = self._partners_for_channel(channel)
            partners = self._filter_partners_by_frequency(
                partners, config.code, config.cron_interval,
            )
            partner_ids = self._exclude_logged_partners(
                partners.ids, config, period_key, channel_id=channel.id,
            )
            if not partner_ids:
                continue
            subject = _('🆕 Nuevo curso: %(course)s', course=channel.name)
            body = self._das_build_campaign_body(
                'new_courses', channels=channel, channels_title=_('Curso recién publicado'),
            )
            self._create_mailing_and_logs(
                config, subject, body, partner_ids, period_key, channel=channel,
            )
            total += len(partner_ids)
        return total

    @api.model
    def _run_experience(self, config):
        today = self._today()
        period_key = self._period_key_for_config(config, today)
        Channel = self.env['slide.channel'].sudo()
        channels = Channel.search([('website_published', '=', True)], limit=20, order='create_date desc')
        if not channels:
            return 0
        Partner = self.env['res.partner'].sudo()
        total = 0
        for level in ('beginner', 'intermediate', 'advanced', 'expert'):
            partners = Partner.search(expression.AND([
                self._base_partner_domain(),
                [('das_experience_level', '=', level)],
            ]))
            partners = self._filter_partners_by_frequency(
                partners, config.code, config.cron_interval,
            )
            partner_ids = self._exclude_logged_partners(partners.ids, config, period_key)
            if not partner_ids:
                continue
            level_label = _(_EXPERIENCE_LABELS.get(level, level))
            subject = _('💡 Cursos ideales para nivel %(level)s', level=level_label)
            body = self._das_build_campaign_body(
                'experience',
                channels=channels[:5],
                channels_title=_('Recomendados para nivel %s') % level_label,
            )
            self._create_mailing_and_logs(config, subject, body, partner_ids, period_key)
            total += len(partner_ids)
        return total

    @api.model
    def _run_newsletter(self, config):
        today = self._today()
        period_key = self._period_key_for_config(config, today)
        Partner = self.env['res.partner'].sudo()
        partners = Partner.search(self._base_partner_domain())
        partners = self._filter_partners_by_frequency(
            partners, config.code, config.cron_interval,
        )
        partner_ids = self._exclude_logged_partners(partners.ids, config, period_key)
        if not partner_ids:
            return 0
        Channel = self.env['slide.channel'].sudo()
        recent = Channel.search(
            [('website_published', '=', True)],
            limit=10,
            order='create_date desc',
        )
        recent = Channel.search(
            [('website_published', '=', True)],
            limit=10,
            order='create_date desc',
        )
        if config.cron_interval == 'monthly':
            subject = _('📬 Newsletter mensual · Academia Virtual DAS')
            title = _('Destacados del mes')
        else:
            subject = _('📬 Newsletter semanal · Academia Virtual DAS')
            title = _('Destacados de la semana')
        body = self._das_build_campaign_body(
            'newsletter', channels=recent, channels_title=title,
        )
        self._create_mailing_and_logs(config, subject, body, partner_ids, period_key)
        return len(partner_ids)

    # -------------------------------------------------------------------------
    # Punto de entrada por cron
    # -------------------------------------------------------------------------

    @api.model
    def _run_campaign_config(self, config):
        if not config or not config.active:
            return 0
        handlers = {
            'birthday': self._run_birthday,
            'upcoming': self._run_upcoming,
            'new_courses': self._run_new_courses,
            'experience': self._run_experience,
            'newsletter': self._run_newsletter,
        }
        handler = handlers.get(config.code)
        if not handler:
            _logger.warning('DAS campaigns: tipo de campaña desconocido %s', config.code)
            return 0
        try:
            count = handler(config)
            _logger.info(
                'DAS campaigns: %s (%s) → %s destinatarios procesados.',
                config.name, config.code, count,
            )
            return count
        except Exception:
            _logger.exception(
                'DAS campaigns: error ejecutando campaña %s (%s).',
                config.name, config.code,
            )
            return 0

    @api.model
    def cron_run_daily_campaigns(self):
        Config = self.env['das.email.campaign.config'].sudo()
        configs = Config.search([
            ('active', '=', True),
            ('cron_interval', '=', 'daily'),
        ])
        total = sum(self._run_campaign_config(c) for c in configs)
        self.env['das.email.campaign.log']._cron_sync_delivery_status()
        return total

    @api.model
    def cron_run_weekly_campaigns(self):
        Config = self.env['das.email.campaign.config'].sudo()
        configs = Config.search([
            ('active', '=', True),
            ('cron_interval', '=', 'weekly'),
        ])
        total = sum(self._run_campaign_config(c) for c in configs)
        self.env['das.email.campaign.log']._cron_sync_delivery_status()
        return total

    @api.model
    def cron_run_monthly_campaigns(self):
        Config = self.env['das.email.campaign.config'].sudo()
        configs = Config.search([
            ('active', '=', True),
            ('cron_interval', '=', 'monthly'),
        ])
        total = sum(self._run_campaign_config(c) for c in configs)
        self.env['das.email.campaign.log']._cron_sync_delivery_status()
        return total
