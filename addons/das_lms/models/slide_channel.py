# -*- coding: utf-8 -*-
import logging
from urllib.parse import urlparse

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from .das_lms_constants import (
    DAS_LMS_ACADEMIC_MODALITY,
    DAS_LMS_REGISTRATION_CLOSED_MESSAGE,
    DAS_LMS_REGISTRATION_CUTOFF_DAYS_DEFAULT,
)

_logger = logging.getLogger(__name__)


class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    das_lms_enrollment_ids = fields.One2many(
        'course.enrollment',
        'course_id',
        string='Seguimiento DAS LMS',
        readonly=True,
        domain=[('is_das_student', '=', True)],
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
    registration_cutoff_days = fields.Integer(
        string='Días de corte de inscripción',
        default=DAS_LMS_REGISTRATION_CUTOFF_DAYS_DEFAULT,
        tracking=True,
        help=(
            'Número de días antes de la fecha de inicio hasta los cuales los estudiantes '
            'pueden inscribirse. Ejemplo: 2 → el último día de inscripción es dos días '
            'antes del inicio del curso.'
        ),
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
        help=(
            'Falso si el curso finalizó, si ya pasó el último día de inscripción '
            'o si la fecha de inicio ya llegó (solo aplica a no inscritos).'
        ),
    )
    das_registration_deadline = fields.Date(
        string='Último día de inscripción',
        compute='_compute_das_academic_lifecycle',
        readonly=True,
        help='Calculado: fecha de inicio menos días de corte de inscripción.',
    )
    das_registration_open = fields.Boolean(
        string='Inscripción abierta',
        compute='_compute_das_academic_lifecycle',
        readonly=True,
        help='Indica si aún se aceptan nuevas inscripciones según el calendario y el corte configurado.',
    )
    das_can_study = fields.Boolean(
        string='Contenidos desbloqueados (calendario)',
        compute='_compute_das_academic_lifecycle',
        readonly=True,
        help='Según fechas DAS: si es falso en estado «próximo», el alumno sigue siendo miembro del curso pero no debe abrir lecciones hasta la fecha de inicio.',
    )

    @api.depends('das_autonomous_hours', 'das_teacher_contact_hours')
    def _compute_das_total_hours(self):
        for rec in self:
            rec.das_total_hours = (rec.das_autonomous_hours or 0.0) + (rec.das_teacher_contact_hours or 0.0)

    @api.depends('das_start_date', 'das_end_date', 'registration_cutoff_days')
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

            deadline = channel._das_lms_registration_deadline_date()
            registration_open = channel._das_lms_is_registration_open(
                today=today, status=status, deadline=deadline,
            )
            catalog_visible = channel._das_lms_is_public_catalog_visible(today=today)

            channel.das_academic_status = status
            channel.das_is_before_start = status == 'proximo'
            channel.das_is_running = status == 'en_curso'
            channel.das_is_finished = status == 'finalizado'
            channel.das_registration_deadline = deadline
            channel.das_registration_open = registration_open
            channel.das_can_sell = registration_open and catalog_visible
            # Inscritos pueden repasar contenido tras el fin; antes del inicio el material queda cerrado.
            channel.das_can_study = status in ('sin_fechas', 'en_curso', 'finalizado')

    @api.constrains('das_start_date', 'das_end_date', 'registration_cutoff_days')
    def _check_das_academic_dates(self):
        for rec in self:
            if rec.das_start_date and rec.das_end_date and rec.das_end_date < rec.das_start_date:
                raise ValidationError(
                    _('La fecha de fin no puede ser anterior a la fecha de inicio en el curso «%s».')
                    % (rec.display_name,)
                )
            if rec.registration_cutoff_days is not None and rec.registration_cutoff_days < 0:
                raise ValidationError(
                    _('Los días de corte de inscripción no pueden ser negativos en el curso «%s».')
                    % (rec.display_name,)
                )
            if rec.das_start_date and rec.registration_cutoff_days and rec.registration_cutoff_days > 0:
                deadline = rec._das_lms_registration_deadline_date()
                if deadline and deadline < rec.das_start_date:
                    _logger.info(
                        'DAS LMS: curso id=%s «%s» — último día de inscripción: %s (inicio: %s).',
                        rec.id,
                        rec.display_name,
                        deadline,
                        rec.das_start_date,
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

    def _filter_add_members(self, target_partners, raise_on_access=False):
        """Permite inscripción administrativa vía factura (`_das_lms_enroll_partner`)."""
        if self.env.context.get('das_lms_allow_structured_enroll'):
            return self
        return super()._filter_add_members(target_partners, raise_on_access=raise_on_access)

    def _action_add_members(self, target_partners, member_status='joined', raise_on_access=False):
        """Evita la alta automática al confirmar pedido; valida corte de inscripción en altas comerciales."""
        if self.env.context.get('das_lms_skip_slide_channel_auto_enroll'):
            return self.env['slide.channel.partner'].browse()
        if not self.env.context.get('das_lms_bypass_academic_close'):
            for channel in self:
                if channel.das_academic_status == 'finalizado':
                    responsible = channel.user_id.partner_id if channel.user_id else self.env['res.partner']
                    if target_partners - responsible:
                        raise UserError(channel._das_lms_registration_closed_message())
                    continue
                if channel._das_lms_is_registration_open():
                    continue
                responsible = channel.user_id.partner_id if channel.user_id else self.env['res.partner']
                if target_partners - responsible:
                    raise UserError(channel._das_lms_registration_closed_message())
        return super()._action_add_members(
            target_partners, member_status=member_status, raise_on_access=raise_on_access
        )

    def _das_lms_enroll_partner(self, partner):
        """Crea miembro eLearning si no existe (por canal + jerarquía comercial). Sin heurísticas por nombre.

        Usar tras factura cliente validada y en migraciones internas.
        """
        self.ensure_one()
        SlideChannelPartner = self.env['slide.channel.partner'].sudo()
        if not partner:
            return SlideChannelPartner.browse()
        commercial = partner.commercial_partner_id
        root_id = commercial.id if commercial else partner.id
        if not root_id:
            return SlideChannelPartner.browse()
        existing = SlideChannelPartner.search(
            [
                ('channel_id', '=', self.id),
                ('partner_id', 'child_of', root_id),
                ('active', '=', True),
            ],
            limit=1,
        )
        if existing:
            return existing
        if not self.env.context.get('das_lms_bypass_registration_close'):
            if not self._das_lms_is_registration_open():
                raise ValidationError(self._das_lms_registration_closed_message())
        partner.ensure_one()
        _logger.info(
            'DAS LMS enroll_partner start channel=%s partner=%s commercial_root=%s academic_status=%s '
            'ctx_skip_auto=%s',
            self.id,
            partner.id,
            partner.commercial_partner_id.id,
            getattr(self, 'das_academic_status', None),
            bool(self.env.context.get('das_lms_skip_slide_channel_auto_enroll')),
        )
        ctx = dict(self.env.context)
        ctx.pop('das_lms_skip_slide_channel_auto_enroll', None)
        ctx['das_lms_allow_structured_enroll'] = True
        created = (
            self.sudo()
            .with_context(**ctx)
            ._action_add_members(partner, member_status='joined', raise_on_access=False)
        )
        return created.filtered(lambda r: r.channel_id.id == self.id)[:1]

    def _das_lms_user_is_enrolled(self, partner=None):
        """Inscripción efectiva vía slide.channel.partner (jerarquía comercial/contactos hijos incluidos)."""
        self.ensure_one()
        try:
            partner = partner or self.env.user.partner_id
            if not partner:
                return False
            root = partner.commercial_partner_id.id or partner.id
            if not root:
                return False
            return bool(
                self.env['slide.channel.partner']
                .sudo()
                .search(
                    [
                        ('channel_id', '=', self.id),
                        ('partner_id', 'child_of', root),
                        ('active', '=', True),
                    ],
                    limit=1,
                )
            )
        except Exception:
            _logger.exception(
                'DAS LMS: _das_lms_user_is_enrolled canal id=%s.',
                self.id,
            )
            return False

    def _das_lms_can_sell_to_partner(self, partner=None):
        """Reglas comerciales DAS sobre este canal para el contacto dado."""
        self.ensure_one()
        try:
            partner = partner or self.env.user.partner_id
            if self._das_lms_user_is_enrolled(partner):
                return False
            if not self._das_lms_is_registration_open():
                return False
            if not self._das_lms_is_public_catalog_visible(partner=partner):
                return False
            return True
        except Exception:
            _logger.exception(
                'DAS LMS: _das_lms_can_sell_to_partner canal id=%s.',
                self.id,
            )
            return True

    def _das_lms_registration_closed_message(self):
        """Mensaje estándar cuando el corte de inscripción ya pasó."""
        return _(DAS_LMS_REGISTRATION_CLOSED_MESSAGE)

    def _das_lms_registration_deadline_date(self):
        """Último día calendario en que se aceptan nuevas inscripciones.

        Fórmula: ``das_start_date − registration_cutoff_days``.

        Si no hay fecha de inicio configurada, no hay corte explícito y se
        devuelve ``False`` (la apertura depende solo del estado académico).
        """
        self.ensure_one()
        if not self.das_start_date:
            return False
        cutoff = self.registration_cutoff_days or 0
        return fields.Date.subtract(self.das_start_date, days=cutoff)

    def _das_lms_is_registration_open(self, today=None, status=None, deadline=None):
        """True si hoy aún se pueden crear nuevas inscripciones comerciales.

        Condiciones:
        - El curso no está finalizado.
        - Si hay ``das_start_date``, hoy debe ser ``<=`` último día de inscripción
          (fecha de inicio − días de corte).
        """
        self.ensure_one()
        today = today or fields.Date.context_today(self)
        status = status if status is not None else self.das_academic_status
        if status == 'finalizado':
            return False
        deadline = deadline if deadline is not None else self._das_lms_registration_deadline_date()
        if deadline:
            return today <= deadline
        return True

    def _das_lms_is_public_catalog_visible(self, partner=None, today=None):
        """Visible en tienda y catálogo eLearning para visitantes no inscritos.

        Los cursos con ``das_start_date`` dejan de mostrarse cuando
        ``fecha_actual >= fecha de inicio``. Los alumnos ya inscritos
        siempre pueden ver el curso.
        """
        self.ensure_one()
        partner = partner if partner is not None else (
            self.env.user.partner_id if not self.env.user._is_public() else self.env['res.partner']
        )
        if partner and self._das_lms_user_is_enrolled(partner):
            return True
        start = self.das_start_date
        if not start:
            return True
        today = today or fields.Date.context_today(self)
        return today < start

    def _das_lms_registration_notice_kind(self, partner=None):
        """Tipo de aviso para visitantes: closed | before_start | open | none."""
        self.ensure_one()
        if partner and self._das_lms_user_is_enrolled(partner):
            return 'none'
        today = fields.Date.context_today(self)
        if not self._das_lms_is_registration_open(today=today):
            return 'closed'
        if not self._das_lms_is_public_catalog_visible(partner=partner, today=today):
            return 'closed'
        if self.das_start_date and today < self.das_start_date:
            return 'before_start'
        return 'open'

    def _das_lms_registration_notice_message(self, partner=None):
        """Mensaje dinámico de inscripción para tienda, portal y backend."""
        self.ensure_one()
        kind = self._das_lms_registration_notice_kind(partner=partner)
        if kind == 'closed':
            today = fields.Date.context_today(self)
            if self.das_start_date and today >= self.das_start_date:
                return _(
                    'El curso ya ha comenzado. La inscripción para este curso ha cerrado.'
                )
            return self._das_lms_registration_closed_message()
        if kind == 'before_start':
            deadline = self.das_registration_deadline or self._das_lms_registration_deadline_date()
            if deadline:
                ds = deadline.strftime('%d/%m/%Y')
                return _(
                    'El curso aún no ha comenzado. Inscríbete hasta el %(deadline)s.'
                ) % {'deadline': ds}
            return _('El curso aún no ha comenzado. Inscríbete ahora.')
        if kind == 'open':
            return _('Inscripción abierta.')
        return ''

    def _das_lms_public_course_href(self):
        """Ruta para enlazar el curso desde la web (/slides/...) sin dominio absoluto.

        Odoo rellena ``website_url`` con el host de ``web.base.url``. Si queda un túnel
        temporal (p. ej. trycloudflare.com) ya caído, un href absoluto provoca NXDOMAIN;
        usando solo la ruta se mantiene el mismo host que el usuario tiene en la barra.
        """
        self.ensure_one()
        try:
            raw = self.website_url
            if not raw or raw == '#':
                return '/slides/%s' % self.env['ir.http']._slug(self)
            if raw.startswith(('http://', 'https://')):
                parsed = urlparse(raw)
                path = parsed.path or '/'
                if parsed.query:
                    path = '%s?%s' % (path, parsed.query)
                return path
            return raw
        except Exception:
            _logger.exception(
                'DAS LMS: _das_lms_public_course_href canal id=%s.',
                self.id,
            )
            try:
                return '/slides/%s' % self.env['ir.http']._slug(self)
            except Exception:
                return '#'

    def _das_lms_get_related_channel(self):
        """API simétrica con product.template (un canal es su propio curso)."""
        self.ensure_one()
        return self

    @api.model
    def _das_lms_portal_can_study_channel(self, channel):
        """Ficha del curso: slide.channel.partner activo o invitación Odoo pendiente."""
        if not channel:
            return False
        channel.ensure_one()
        user = channel.env.user
        if user._is_public():
            return False
        if channel._das_lms_user_is_enrolled(partner=user.partner_id):
            return True
        return bool(channel.is_member_invited)

    @api.model
    def _das_lms_portal_can_access_course_lessons(self, channel):
        """Inscrito y calendario académico permite abrir lecciones (no aplica antes del inicio)."""
        if not self._das_lms_portal_can_study_channel(channel):
            return False
        return bool(channel.das_can_study)
