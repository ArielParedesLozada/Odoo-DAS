# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from .das_lms_constants import DAS_LMS_ACADEMIC_MODALITY


class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    das_lms_enrollment_ids = fields.One2many(
        'course.enrollment',
        'course_id',
        string='Seguimiento DAS LMS',
        readonly=True,
    )

    das_start_date = fields.Date(
        string='Fecha de inicio',
        tracking=True,
        help='Inicio académico oficial del curso (independiente de la duración técnica por lecciones).',
    )
    das_end_date = fields.Date(
        string='Fecha de fin',
        tracking=True,
        help='Fin académico oficial del curso.',
    )
    das_modality = fields.Selection(
        DAS_LMS_ACADEMIC_MODALITY,
        string='Modalidad',
        tracking=True,
        help='Modalidad académica declarada para el curso.',
    )
    das_autonomous_hours = fields.Float(
        string='Horas autónomas',
        digits=(16, 2),
        default=0.0,
        help='Horas de trabajo autónomo del estudiante.',
    )
    das_teacher_contact_hours = fields.Float(
        string='Horas con docente',
        digits=(16, 2),
        default=0.0,
        help='Horas de contacto directo con el docente.',
    )
    das_total_hours = fields.Float(
        string='Total de horas',
        digits=(16, 2),
        compute='_compute_das_total_hours',
        store=True,
        readonly=True,
        help='Suma de horas autónomas y horas con docente.',
    )

    # --- Ciclo académico (no almacenado: siempre coherente con la fecha del día al leer) ---
    das_academic_status = fields.Selection(
        [
            ('sin_fechas', 'Sin fechas definidas'),
            ('proximo', 'Próximo a iniciar'),
            ('en_curso', 'En curso'),
            ('finalizado', 'Finalizado'),
        ],
        string='Estado académico',
        compute='_compute_das_academic_lifecycle',
        readonly=True,
        help='Derivado de las fechas académicas DAS y la fecha actual.',
    )
    das_is_before_start = fields.Boolean(
        string='Antes del inicio',
        compute='_compute_das_academic_lifecycle',
        readonly=True,
    )
    das_is_running = fields.Boolean(
        string='Periodo lectivo activo',
        compute='_compute_das_academic_lifecycle',
        readonly=True,
    )
    das_is_finished = fields.Boolean(
        string='Ciclo finalizado',
        compute='_compute_das_academic_lifecycle',
        readonly=True,
    )
    das_can_sell = fields.Boolean(
        string='Permite nuevas inscripciones (venta)',
        compute='_compute_das_academic_lifecycle',
        readonly=True,
        help='Falso si el curso está finalizado académicamente; no afecta a alumnos ya inscritos.',
    )
    das_can_study = fields.Boolean(
        string='Contenidos desbloqueados',
        compute='_compute_das_academic_lifecycle',
        readonly=True,
        help='Para alumnos inscritos: permite abrir lecciones. Falso antes de la fecha de inicio académica.',
    )

    @api.depends('das_autonomous_hours', 'das_teacher_contact_hours')
    def _compute_das_total_hours(self):
        for rec in self:
            rec.das_total_hours = (rec.das_autonomous_hours or 0.0) + (rec.das_teacher_contact_hours or 0.0)

    @api.depends('das_start_date', 'das_end_date')
    def _compute_das_academic_lifecycle(self):
        for channel in self:
            today = fields.Date.context_today(channel)
            start = channel.das_start_date
            end = channel.das_end_date

            if not start and not end:
                status = 'sin_fechas'
            elif start and end:
                if today < start:
                    status = 'proximo'
                elif today <= end:
                    status = 'en_curso'
                else:
                    status = 'finalizado'
            elif start and not end:
                status = 'proximo' if today < start else 'en_curso'
            else:
                # Solo fecha fin
                status = 'en_curso' if today <= end else 'finalizado'

            channel.das_academic_status = status
            channel.das_is_before_start = status == 'proximo'
            channel.das_is_running = status == 'en_curso'
            channel.das_is_finished = status == 'finalizado'
            channel.das_can_sell = status != 'finalizado'
            # Inscritos pueden repasar contenido tras el fin; antes del inicio el material queda cerrado.
            channel.das_can_study = status in ('sin_fechas', 'en_curso', 'finalizado')

    @api.constrains('das_start_date', 'das_end_date')
    def _check_das_academic_dates(self):
        for rec in self:
            if rec.das_start_date and rec.das_end_date and rec.das_end_date < rec.das_start_date:
                raise ValidationError(
                    _('La fecha de fin no puede ser anterior a la fecha de inicio en el curso «%s».')
                    % (rec.display_name,)
                )

    @api.constrains('das_autonomous_hours', 'das_teacher_contact_hours')
    def _check_das_hours_non_negative(self):
        for rec in self:
            if (rec.das_autonomous_hours or 0.0) < 0 or (rec.das_teacher_contact_hours or 0.0) < 0:
                raise ValidationError(
                    _('Las horas autónomas y las horas con docente no pueden ser negativas (curso «%s»).')
                    % (rec.display_name,)
                )

    def write(self, vals):
        res = super().write(vals)
        if 'das_modality' in vals:
            enrollments = self.env['course.enrollment'].sudo().search([('course_id', 'in', self.ids)])
            enrollments._sync_fields_from_channel_partner()
        return res

    @api.model
    def _das_lms_portal_can_study_channel(self, channel):
        """Inscrito o invitación pendiente (acceso a la ficha del curso en portal DAS)."""
        if not channel:
            return False
        channel.ensure_one()
        user = channel.env.user
        if user._is_public():
            return False
        return bool(channel.is_member or channel.is_member_invited)

    @api.model
    def _das_lms_portal_can_access_course_lessons(self, channel):
        """Inscrito y calendario académico permite abrir lecciones (no aplica antes del inicio)."""
        if not self._das_lms_portal_can_study_channel(channel):
            return False
        return bool(channel.das_can_study)
