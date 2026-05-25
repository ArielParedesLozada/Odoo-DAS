# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class DasEmailCampaignConfig(models.Model):
    _name = 'das.email.campaign.config'
    _description = 'Configuración de campaña automática DAS'
    _order = 'sequence, id'

    name = fields.Char(required=True, translate=True)
    code = fields.Selection(
        selection=[
            ('new_courses', 'Promoción cursos nuevos'),
            ('experience', 'Recomendación por nivel'),
            ('upcoming', 'Cursos próximos a iniciar'),
            ('newsletter', 'Newsletter novedades'),
            ('birthday', 'Felicitación cumpleaños'),
        ],
        required=True,
        index=True,
    )
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    description = fields.Text(translate=True)
    mail_template_id = fields.Many2one(
        'mail.template',
        string='Plantilla de correo',
        domain="[('model', '=', 'res.partner')]",
    )
    days_before_start = fields.Integer(
        string='Días de anticipación (inicio curso)',
        default=3,
        help='Para campañas de cursos próximos: ventana de días antes del inicio.',
    )
    new_course_window_days = fields.Integer(
        string='Ventana cursos nuevos (días)',
        default=14,
        help='Cursos publicados en los últimos N días se consideran nuevos.',
    )
    cron_interval = fields.Selection(
        selection=[
            ('daily', 'Diario'),
            ('weekly', 'Semanal'),
            ('monthly', 'Mensual'),
        ],
        string='Intervalo del cron',
        required=True,
        default='weekly',
    )
    last_run_date = fields.Date(string='Última ejecución', readonly=True)
    log_count = fields.Integer(compute='_compute_log_count', string='Envíos registrados')

    def _compute_log_count(self):
        Log = self.env['das.email.campaign.log']
        grouped = Log.read_group(
            [('config_id', 'in', self.ids)],
            ['config_id'],
            ['config_id'],
        )
        counts = {row['config_id'][0]: row['config_id_count'] for row in grouped}
        for rec in self:
            rec.log_count = counts.get(rec.id, 0)

    def action_view_logs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.name,
            'res_model': 'das.email.campaign.log',
            'view_mode': 'list,form',
            'domain': [('config_id', '=', self.id)],
            'context': {'default_config_id': self.id},
        }

    @api.model
    def cron_run_daily_campaigns(self):
        return self.env['das.email.campaign.runner'].cron_run_daily_campaigns()

    @api.model
    def cron_run_weekly_campaigns(self):
        return self.env['das.email.campaign.runner'].cron_run_weekly_campaigns()

    @api.model
    def cron_run_monthly_campaigns(self):
        return self.env['das.email.campaign.runner'].cron_run_monthly_campaigns()

    @api.model
    def _das_required_campaign_codes(self):
        return ('birthday', 'upcoming', 'new_courses', 'experience', 'newsletter')

    @api.model
    def _das_ensure_active_campaign_configs(self):
        """Garantiza al menos las 5 campañas automáticas activas."""
        required = self._das_required_campaign_codes()
        configs = self.sudo().search([('code', 'in', required), ('active', '=', True)])
        found = set(configs.mapped('code'))
        missing = set(required) - found
        if missing:
            inactive = self.sudo().search([('code', 'in', list(missing)), ('active', '=', False)])
            if inactive:
                inactive.write({'active': True})
            still_missing = set(required) - set(
                self.sudo().search([('code', 'in', required), ('active', '=', True)]).mapped('code')
            )
            if still_missing:
                _logger.warning(
                    'DAS campaigns: faltan configuraciones activas para: %s',
                    ', '.join(sorted(still_missing)),
                )
        return self.sudo().search([('code', 'in', required), ('active', '=', True)])
