# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError

from .das_lms_constants import DAS_LMS_ACADEMIC_MODALITY

# Días sin actividad con avance < 100 % para marcar como inactivo
DAS_LMS_INACTIVE_DAYS = 30


class CourseEnrollment(models.Model):
    """Espejo estadístico de slide.channel.partner para seguimiento DAS LMS."""

    _name = 'course.enrollment'
    _description = 'Seguimiento estadístico de alumno en curso (eLearning)'
    _order = 'enrollment_date desc, id desc'

    _sql_constraints = [
        (
            'course_enrollment_channel_partner_unique',
            'UNIQUE(channel_partner_id)',
            'Ya existe un registro DAS para este miembro del curso en eLearning.',
        ),
    ]

    channel_partner_id = fields.Many2one(
        'slide.channel.partner',
        string='Miembro eLearning',
        required=True,
        ondelete='cascade',
        index=True,
    )

    student_id = fields.Many2one(
        related='channel_partner_id.partner_id',
        comodel_name='res.partner',
        string='Alumno',
        store=True,
        readonly=True,
    )
    course_id = fields.Many2one(
        related='channel_partner_id.channel_id',
        comodel_name='slide.channel',
        string='Curso',
        store=True,
        readonly=True,
    )

    student_email = fields.Char(
        related='student_id.email',
        string='Correo del alumno',
        readonly=True,
    )
    student_phone = fields.Char(
        string='Teléfono del alumno',
        compute='_compute_student_phone',
        store=True,
        readonly=True,
    )

    member_status = fields.Selection(
        related='channel_partner_id.member_status',
        string='Estado miembro (eLearning)',
        readonly=True,
    )

    progress = fields.Integer(
        string='Avance (%)',
        related='channel_partner_id.completion',
        readonly=True,
        store=True,
        aggregator='avg',
    )

    enrollment_date = fields.Date(
        string='Fecha de inscripción',
        compute='_compute_enrollment_date',
        store=True,
        readonly=True,
    )

    course_start_date = fields.Date(
        string='Fecha de inicio del curso',
        compute='_compute_course_start_date',
        store=True,
        readonly=True,
        help='Primera fecha de publicación de contenidos del curso en eLearning (si existe).',
    )

    modality = fields.Selection(
        selection=DAS_LMS_ACADEMIC_MODALITY,
        string='Modalidad',
        required=True,
        default='grabado',
        help='Por defecto coincide con la modalidad académica del curso; puede ajustarse puntualmente.',
    )
    course_das_total_hours = fields.Float(
        related='course_id.das_total_hours',
        string='Horas totales (curso)',
        readonly=True,
        digits=(16, 1),
    )
    status = fields.Selection(
        selection=[
            ('activo', 'Activo'),
            ('completado', 'Completado'),
            ('abandonado', 'Abandonado'),
        ],
        string='Estado académico',
        required=True,
        default='activo',
        help='Sincronizado desde eLearning; puede ajustarse para seguimiento interno DAS.',
    )

    engagement_status = fields.Selection(
        selection=[
            ('sin_iniciar', 'Sin iniciar'),
            ('en_progreso', 'En progreso'),
            ('completado', 'Completado'),
            ('inactivo', 'Inactivo'),
        ],
        string='Compromiso / engagement',
        compute='_compute_engagement_status',
        store=True,
        readonly=True,
    )

    last_activity_at = fields.Datetime(
        string='Última actividad',
        compute='_compute_last_activity_at',
        readonly=True,
    )
    last_activity_date = fields.Date(
        string='Última actividad (fecha)',
        compute='_compute_last_activity_date',
        store=True,
        readonly=True,
        help='Derivada de la última actividad; reservada para informes y futuras sincronizaciones.',
    )

    last_sync_at = fields.Datetime(
        string='Última sincronización',
        readonly=True,
        copy=False,
    )

    notes = fields.Text(
        string='Observaciones internas',
    )

    is_das_student = fields.Boolean(
        string='Es alumno DAS',
        compute='_compute_is_das_student',
        store=True,
        index=True,
        help='Verdadero si el contacto no está vinculado a un usuario interno de Odoo.',
    )

    course_website_url = fields.Char(
        related='course_id.website_url',
        string='Curso en web',
        readonly=True,
    )

    @api.depends('student_id', 'student_id.user_ids', 'student_id.user_ids.share')
    def _compute_is_das_student(self):
        for rec in self:
            partner = rec.student_id
            rec.is_das_student = bool(
                partner and partner._das_lms_is_academic_student_partner()
            )

    @api.model
    def _das_lms_student_domain(self, domain=None):
        """Dominio estándar DAS: solo inscripciones de alumnos reales."""
        base = [('is_das_student', '=', True)]
        return base + (domain or [])

    @api.model
    def _das_lms_search_students(self, domain=None, **kwargs):
        return self.search(self._das_lms_student_domain(domain), **kwargs)

    @api.depends('student_id.phone', 'student_id.mobile')
    def _compute_student_phone(self):
        for rec in self:
            p = rec.student_id
            rec.student_phone = (p.phone or p.mobile or '').strip() or False

    @api.depends('channel_partner_id.create_date')
    def _compute_enrollment_date(self):
        for rec in self:
            cd = rec.channel_partner_id.create_date
            rec.enrollment_date = fields.Date.to_date(cd) if cd else False

    @api.depends(
        'course_id.slide_ids.date_published',
        'course_id.slide_ids.is_category',
        'course_id.slide_ids.is_published',
    )
    def _compute_course_start_date(self):
        for rec in self:
            if not rec.course_id:
                rec.course_start_date = False
                continue
            dates = []
            for slide in rec.course_id.slide_ids:
                if slide.is_category or not slide.is_published or not slide.date_published:
                    continue
                dates.append(fields.Date.to_date(slide.date_published))
            rec.course_start_date = min(dates) if dates else False

    @api.depends('last_activity_at')
    def _compute_last_activity_date(self):
        for rec in self:
            rec.last_activity_date = (
                fields.Date.to_date(rec.last_activity_at) if rec.last_activity_at else False
            )

    @api.depends('progress', 'last_activity_at')
    def _compute_engagement_status(self):
        now = fields.Datetime.now()
        limit = timedelta(days=DAS_LMS_INACTIVE_DAYS)
        for rec in self:
            p = rec.progress or 0
            if p >= 100:
                rec.engagement_status = 'completado'
            elif p <= 0:
                rec.engagement_status = 'sin_iniciar'
            else:
                last = rec.last_activity_at
                if last and (now - last) <= limit:
                    rec.engagement_status = 'en_progreso'
                else:
                    rec.engagement_status = 'inactivo'

    @api.depends(
        'channel_partner_id.write_date',
        'channel_partner_id.create_date',
        'student_id',
        'course_id',
    )
    def _compute_last_activity_at(self):
        SlidePartner = self.env['slide.slide.partner'].sudo()
        for rec in self:
            if not rec.channel_partner_id:
                rec.last_activity_at = False
                continue
            base = rec.channel_partner_id.write_date or rec.channel_partner_id.create_date
            slides = self.env['slide.slide'].sudo().search([
                ('channel_id', '=', rec.course_id.id),
                ('is_category', '=', False),
            ])
            latest_sp = False
            if slides and rec.student_id:
                latest_sp = SlidePartner.search([
                    ('slide_id', 'in', slides.ids),
                    ('partner_id', '=', rec.student_id.id),
                ], order='write_date desc', limit=1)
            wd = latest_sp.write_date if latest_sp else False
            candidates = [d for d in (base, wd) if d]
            rec.last_activity_at = max(candidates) if candidates else False

    @api.model
    def _prepare_vals_from_channel_partner(self, scp):
        channel = scp.channel_id
        modality = (channel.das_modality or 'grabado') if channel else 'grabado'
        return {
            'channel_partner_id': scp.id,
            'modality': modality,
            'status': self._status_from_channel_partner(scp),
            'last_sync_at': fields.Datetime.now(),
        }

    @api.model
    def _status_from_channel_partner(self, scp):
        if not scp.active:
            return 'abandonado'
        if (scp.completion or 0) >= 100 or scp.member_status == 'completed':
            return 'completado'
        return 'activo'

    def _sync_fields_from_channel_partner(self):
        for rec in self:
            scp = rec.channel_partner_id
            if not scp:
                continue
            new_status = self._status_from_channel_partner(scp)
            new_modality = (rec.course_id.das_modality or 'grabado') if rec.course_id else rec.modality
            vals = {}
            if new_status != rec.status:
                vals['status'] = new_status
            if new_modality != rec.modality:
                vals['modality'] = new_modality
            if vals:
                super(CourseEnrollment, rec).write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('channel_partner_id'):
                raise UserError(
                    _('Las inscripciones DAS solo existen como reflejo de eLearning. '
                      'Sincronice desde el Dashboard DAS LMS (Actualizar datos) o espere a que exista slide.channel.partner.')
                )
            scp = self.env['slide.channel.partner'].browse(vals['channel_partner_id'])
            partner = scp.partner_id
            if partner and not partner._das_lms_is_academic_student_partner():
                raise UserError(
                    _('El contacto «%s» no es un alumno (usuario interno). '
                      'No se crea seguimiento DAS para instructores ni personal administrativo.')
                    % partner.display_name
                )
            ch = scp.channel_id
            vals.setdefault('modality', (ch.das_modality or 'grabado') if ch else 'grabado')
            vals.setdefault('status', self._status_from_channel_partner(scp))
            vals.setdefault('last_sync_at', fields.Datetime.now())
        records = super().create(vals_list)
        records._sync_fields_from_channel_partner()
        return records

    def write(self, vals):
        res = super().write(vals)
        if 'channel_partner_id' in vals:
            self._sync_fields_from_channel_partner()
        return res

    def _das_lms_require_sync_admin(self):
        if self.env.su:
            return
        if not (
            self.env.user.has_group('base.group_system')
            or self.env.user.has_group('base.group_erp_manager')
        ):
            raise AccessError(
                _('Solo administradores pueden ejecutar la sincronización eLearning → DAS LMS.')
            )

    @api.model
    def _das_lms_prune_non_student_enrollments(self):
        """Elimina espejos DAS de miembros no alumnos (no toca slide.channel.partner)."""
        stale = self.sudo().search([('is_das_student', '=', False)])
        if stale:
            stale.unlink()

    @api.model
    def action_sync_from_elearning(self):
        """Crea o actualiza course.enrollment a partir de slide.channel.partner (solo alumnos)."""
        self._das_lms_require_sync_admin()
        SlideChannelPartner = self.env['slide.channel.partner'].sudo()
        now = fields.Datetime.now()
        created = 0
        updated = 0
        for scp in SlideChannelPartner.search([]):
            partner = scp.partner_id
            existing = self.sudo().search([('channel_partner_id', '=', scp.id)], limit=1)
            if partner and not partner._das_lms_is_academic_student_partner():
                if existing:
                    existing.unlink()
                continue
            if existing:
                existing._sync_fields_from_channel_partner()
                existing.write({'last_sync_at': now})
                updated += 1
            else:
                self.create(self._prepare_vals_from_channel_partner(scp))
                created += 1

        self._das_lms_prune_non_student_enrollments()

        list_action = self.env['ir.actions.actions']._for_xml_id('das_lms.action_course_enrollment')
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Sincronización DAS LMS'),
                'message': _('Creadas: %(c)d · Actualizadas: %(u)d') % {'c': created, 'u': updated},
                'type': 'success',
                'sticky': False,
                'next': list_action,
            },
        }

    def action_open_course(self):
        self.ensure_one()
        channel = self.course_id
        if not channel:
            return False
        url = channel.sudo()._das_lms_public_course_href()
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    def action_open_student(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Alumno'),
            'res_model': 'res.partner',
            'res_id': self.student_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_open_channel_partner(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Miembro eLearning'),
            'res_model': 'slide.channel.partner',
            'res_id': self.channel_partner_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.model
    def _das_lms_cleanup_obsolete_view_fields(self):
        """Quita de ir.ui.view referencias a campos eliminados o renombrados (vistas en BD)."""
        import re

        View = self.env['ir.ui.view'].sudo()
        field_names = (
            'certificate_state_text',
            'certificate_id',
            'certificate_state',
            'partner_email',
        )
        for view in View.search([('model', '=', 'course.enrollment')]):
            arch = view.arch_db or ''
            if not arch or not any(n in arch for n in field_names):
                continue
            new_arch = arch
            for fname in field_names:
                new_arch = re.sub(
                    r'<field\b[^>]*\bname=["\']%s["\'][^>]*/>' % re.escape(fname),
                    '',
                    new_arch,
                    flags=re.IGNORECASE | re.DOTALL,
                )
            if new_arch != arch:
                view.write({'arch_db': new_arch})
        return True
