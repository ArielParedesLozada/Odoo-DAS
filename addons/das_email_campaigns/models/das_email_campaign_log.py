# -*- coding: utf-8 -*-
from odoo import api, fields, models


class DasEmailCampaignLog(models.Model):
    _name = 'das.email.campaign.log'
    _description = 'Registro de envío de campaña automática DAS'
    _order = 'create_date desc, id desc'
    _rec_name = 'display_name'

    display_name = fields.Char(compute='_compute_display_name', store=True)
    config_id = fields.Many2one(
        'das.email.campaign.config',
        string='Campaña',
        required=True,
        ondelete='cascade',
        index=True,
    )
    campaign_type = fields.Selection(
        related='config_id.code',
        store=True,
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Contacto',
        required=True,
        ondelete='cascade',
        index=True,
    )
    channel_id = fields.Many2one(
        'slide.channel',
        string='Curso relacionado',
        ondelete='set null',
        index=True,
    )
    channel_ref_id = fields.Integer(
        string='Ref. curso (idempotencia)',
        default=0,
        required=True,
        index=True,
        help='0 si no hay curso; usado en la restricción única de envío.',
    )
    period_key = fields.Char(
        string='Clave de periodo',
        required=True,
        index=True,
        help='Identificador del periodo de envío (p. ej. 2026-W21, 2026-05-22).',
    )
    mailing_id = fields.Many2one(
        'mailing.mailing',
        string='Correo masivo',
        ondelete='set null',
        index=True,
    )
    state = fields.Selection(
        selection=[
            ('queued', 'En cola'),
            ('sent', 'Enviado'),
            ('failed', 'Fallido'),
            ('skipped', 'Omitido'),
        ],
        default='queued',
        required=True,
        index=True,
    )
    sent_at = fields.Datetime(string='Enviado el', readonly=True)
    trace_status = fields.Selection(
        selection=[
            ('none', 'Sin traza'),
            ('sent', 'Enviado'),
            ('open', 'Abierto'),
            ('reply', 'Respondido'),
            ('bounce', 'Rebotado'),
            ('error', 'Error'),
            ('cancel', 'Cancelado'),
        ],
        string='Estado de entrega',
        default='none',
        index=True,
    )
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        index=True,
    )

    _sql_constraints = [
        (
            'das_campaign_log_unique',
            'unique(partner_id, config_id, period_key, channel_ref_id)',
            'Ya se registró un envío para este contacto, campaña, periodo y curso.',
        ),
    ]

    @api.depends('config_id.name', 'partner_id.name', 'period_key', 'channel_id.name')
    def _compute_display_name(self):
        for rec in self:
            parts = [rec.config_id.name or '', rec.partner_id.name or '', rec.period_key or '']
            if rec.channel_id:
                parts.append(rec.channel_id.name)
            rec.display_name = ' · '.join(p for p in parts if p)

    @api.model
    def _sync_trace_status_from_mailing(self, mailing):
        """Actualiza estado de entrega desde mailing.trace."""
        if not mailing:
            return
        Trace = self.env['mailing.trace'].sudo()
        logs = self.search([('mailing_id', '=', mailing.id)])
        if not logs:
            return
        trace_by_partner = {}
        for trace in Trace.search([
            ('mass_mailing_id', '=', mailing.id),
            ('model', '=', 'res.partner'),
        ]):
            partner_id = trace.res_id
            status = trace.trace_status or 'sent'
            trace_by_partner[partner_id] = status
        status_map = {
            'sent': 'sent',
            'open': 'open',
            'reply': 'reply',
            'bounce': 'bounce',
            'error': 'error',
            'cancel': 'cancel',
        }
        for log in logs:
            raw = trace_by_partner.get(log.partner_id.id, 'sent' if mailing.state == 'done' else 'none')
            log.write({
                'trace_status': status_map.get(raw, 'sent'),
                'state': 'failed' if raw in ('bounce', 'error') else 'sent',
                'sent_at': log.sent_at or mailing.sent_date,
            })

    @api.model
    def _cron_sync_delivery_status(self):
        """Sincroniza estados de entrega desde mailing.trace."""
        logs = self.sudo().search([
            ('mailing_id', '!=', False),
            ('state', 'in', ('queued', 'sent')),
        ])
        for mailing in logs.mapped('mailing_id'):
            self._sync_trace_status_from_mailing(mailing)
