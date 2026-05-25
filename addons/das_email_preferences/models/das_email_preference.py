# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class DasEmailPreference(models.Model):
    _name = 'das.email.preference'
    _description = 'Preferencias de comunicación y marketing del usuario'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'completed_on desc, id desc'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one(
        'res.partner',
        string='Contacto',
        required=True,
        ondelete='cascade',
        index=True,
        tracking=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Usuario',
        compute='_compute_user_id',
        store=True,
        readonly=True,
    )
    interest_ids = fields.Many2many(
        'das.email.interest',
        'das_email_preference_interest_rel',
        'preference_id',
        'interest_id',
        string='Gustos / intereses',
        tracking=True,
    )
    birthday = fields.Date(
        string='Fecha de cumpleaños',
        tracking=True,
        help='Utilizada para campañas personalizadas por fecha de nacimiento.',
    )
    comm_email = fields.Boolean(string='Email', default=True, tracking=True)
    comm_sms = fields.Boolean(string='SMS', tracking=True)
    comm_push = fields.Boolean(string='Push', tracking=True)
    experience_level = fields.Selection(
        [
            ('beginner', 'Básico'),
            ('intermediate', 'Intermedio'),
            ('advanced', 'Avanzado'),
            ('expert', 'Experto'),
        ],
        string='Nivel de experiencia',
        tracking=True,
    )
    course_category_ids = fields.Many2many(
        'das.email.course.category',
        'das_email_preference_course_category_rel',
        'preference_id',
        'category_id',
        string='Categorías de cursos preferidas',
        tracking=True,
    )
    communication_frequency = fields.Selection(
        [
            ('weekly', 'Semanal'),
            ('biweekly', 'Quincenal'),
            ('monthly', 'Mensual'),
            ('daily', 'Diaria'),
            ('promotions', 'Solo promociones'),
            ('minimal', 'Mínima'),
        ],
        string='Frecuencia de comunicaciones',
        default='weekly',
        tracking=True,
    )
    terms_accepted = fields.Boolean(string='Acepta términos', tracking=True)
    privacy_accepted = fields.Boolean(string='Acepta privacidad', tracking=True)
    completed = fields.Boolean(
        string='Preferencias completadas',
        default=False,
        tracking=True,
        index=True,
    )
    completed_on = fields.Datetime(string='Completado el', readonly=True, copy=False)
    completed_ip = fields.Char(string='IP de registro', readonly=True, copy=False)
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        default=lambda self: self.env.company,
        index=True,
    )

    _sql_constraints = [
        (
            'partner_unique',
            'unique(partner_id)',
            'Ya existe un registro de preferencias para este contacto.',
        ),
    ]

    @api.depends('partner_id')
    def _compute_user_id(self):
        Users = self.env['res.users'].sudo()
        for rec in self:
            rec.user_id = Users.search([('partner_id', '=', rec.partner_id.id)], limit=1)

    @api.constrains('birthday')
    def _check_birthday(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if not rec.birthday:
                continue
            if rec.birthday > today:
                raise ValidationError(_('La fecha de cumpleaños no puede ser futura.'))
            age_years = today.year - rec.birthday.year - (
                (today.month, today.day) < (rec.birthday.month, rec.birthday.day)
            )
            if age_years < 13:
                raise ValidationError(
                    _('El usuario debe tener al menos 13 años para registrarse.')
                )

    @api.model
    def _get_or_create_for_partner(self, partner, *, force_create=True):
        """Obtiene o crea el borrador de preferencias para un contacto."""
        partner = partner.sudo()
        existing = self.search([('partner_id', '=', partner.id)], limit=1)
        if existing:
            return existing
        if not force_create:
            return self.browse()
        return self.create({'partner_id': partner.id})

    def _validate_required_for_completion(self):
        """Valida campos obligatorios antes de marcar como completado."""
        self.ensure_one()
        errors = []
        if not self.interest_ids:
            errors.append(_('Selecciona al menos un gusto o interés.'))
        if not self.birthday:
            errors.append(_('Indica tu fecha de cumpleaños.'))
        if not self.terms_accepted:
            errors.append(_('Debes aceptar los términos y condiciones.'))
        if not self.privacy_accepted:
            errors.append(_('Debes aceptar la política de privacidad.'))
        if errors:
            raise ValidationError('\n'.join(errors))

    def action_mark_completed(self, ip_address=None):
        """Marca preferencias como completadas tras validación."""
        for rec in self:
            rec._validate_required_for_completion()
            rec.write({
                'completed': True,
                'completed_on': fields.Datetime.now(),
                'completed_ip': ip_address or False,
            })
            try:
                rec.message_post(
                    body=_('Preferencias de comunicación registradas correctamente.'),
                    subtype_xmlid='mail.mt_note',
                )
            except Exception:
                _logger.exception(
                    'DAS email preferences: no se pudo registrar mensaje en chatter (id=%s).',
                    rec.id,
                )
        return True

    @api.model
    def submit_from_portal(self, partner, values, ip_address=None):
        """Crea o actualiza preferencias desde el formulario web/portal."""
        partner = partner.sudo()
        pref = self._get_or_create_for_partner(partner)
        write_vals = {
            'interest_ids': [(6, 0, values.get('interest_ids', []))],
            'birthday': values.get('birthday'),
            'comm_email': True,
            'comm_sms': False,
            'comm_push': False,
            'experience_level': values.get('experience_level') or False,
            # Sin selector en portal: frecuencia por defecto semanal (crons respetan el campo en BD).
            'communication_frequency': 'weekly',
            'course_category_ids': [(6, 0, values.get('course_category_ids', []))],
            'terms_accepted': bool(values.get('terms_accepted')),
            'privacy_accepted': bool(values.get('privacy_accepted')),
        }
        pref.write(write_vals)
        pref.action_mark_completed(ip_address=ip_address)
        return pref
