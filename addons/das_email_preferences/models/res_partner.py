# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    das_email_preference_id = fields.One2many(
        'das.email.preference',
        'partner_id',
        string='Preferencias Email Marketing',
    )
    das_preference_completed = fields.Boolean(
        string='Preferencias completadas',
        compute='_compute_das_preference_marketing_fields',
        store=True,
        index=True,
    )
    das_birthday = fields.Date(
        string='Cumpleaños (marketing)',
        compute='_compute_das_preference_marketing_fields',
        store=True,
        index=True,
    )
    das_interest_ids = fields.Many2many(
        'das.email.interest',
        string='Intereses (marketing)',
        compute='_compute_das_preference_marketing_fields',
        store=True,
    )
    das_comm_email = fields.Boolean(
        string='Acepta email',
        compute='_compute_das_preference_marketing_fields',
        store=True,
    )
    das_comm_sms = fields.Boolean(
        string='Acepta SMS',
        compute='_compute_das_preference_marketing_fields',
        store=True,
    )
    das_comm_push = fields.Boolean(
        string='Acepta push',
        compute='_compute_das_preference_marketing_fields',
        store=True,
    )
    das_experience_level = fields.Selection(
        selection=[
            ('beginner', 'Básico'),
            ('intermediate', 'Intermedio'),
            ('advanced', 'Avanzado'),
            ('expert', 'Experto'),
        ],
        string='Nivel experiencia (marketing)',
        compute='_compute_das_preference_marketing_fields',
        store=True,
    )
    das_communication_frequency = fields.Selection(
        selection=[
            ('weekly', 'Semanal'),
            ('biweekly', 'Quincenal'),
            ('monthly', 'Mensual'),
            ('daily', 'Diaria'),
            ('promotions', 'Solo promociones'),
            ('minimal', 'Mínima'),
        ],
        string='Frecuencia comunicación',
        compute='_compute_das_preference_marketing_fields',
        store=True,
    )
    das_course_category_ids = fields.Many2many(
        'das.email.course.category',
        string='Cursos preferidos',
        compute='_compute_das_preference_marketing_fields',
        store=True,
    )

    @api.depends(
        'das_email_preference_id.completed',
        'das_email_preference_id.birthday',
        'das_email_preference_id.interest_ids',
        'das_email_preference_id.comm_email',
        'das_email_preference_id.comm_sms',
        'das_email_preference_id.comm_push',
        'das_email_preference_id.comm_push',
        'das_email_preference_id.course_category_ids',
        'das_email_preference_id.experience_level',
        'das_email_preference_id.communication_frequency',
    )
    def _compute_das_preference_marketing_fields(self):
        for partner in self:
            pref = partner.das_email_preference_id[:1]
            partner.das_preference_completed = bool(pref and pref.completed)
            partner.das_birthday = pref.birthday if pref else False
            partner.das_interest_ids = pref.interest_ids if pref else False
            partner.das_comm_email = bool(pref and pref.comm_email)
            partner.das_comm_sms = bool(pref and pref.comm_sms)
            partner.das_comm_push = bool(pref and pref.comm_push)
            partner.das_course_category_ids = pref.course_category_ids if pref else False
            partner.das_experience_level = pref.experience_level if pref else False
            partner.das_communication_frequency = pref.communication_frequency if pref else False
