# -*- coding: utf-8 -*-
import logging
from urllib.parse import urlparse

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from .das_lms_constants import DAS_LMS_ACADEMIC_MODALITY

_logger = logging.getLogger(__name__)


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
        string='Contenidos desbloqueados (calendario)',
        compute='_compute_das_academic_lifecycle',
        readonly=True,
        help='Según fechas DAS: si es falso en estado «próximo», el alumno sigue siendo miembro del curso pero no debe abrir lecciones hasta la fecha de inicio.',
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

    def _filter_add_members(self, target_partners, raise_on_access=False):
        """Permite inscripción administrativa vía factura (`_das_lms_enroll_partner`)."""
        if self.env.context.get('das_lms_allow_structured_enroll'):
            return self
        return super()._filter_add_members(target_partners, raise_on_access=raise_on_access)

    def _action_add_members(self, target_partners, member_status='joined', raise_on_access=False):
        """Evita la alta automática al confirmar pedido (website_sale_slides); la inscripción va por factura."""
        if self.env.context.get('das_lms_skip_slide_channel_auto_enroll'):
            return self.env['slide.channel.partner'].browse()
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
            if getattr(self, 'das_academic_status', None) == 'finalizado':
                return False
            return True
        except Exception:
            _logger.exception(
                'DAS LMS: _das_lms_can_sell_to_partner canal id=%s.',
                self.id,
            )
            return True

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
