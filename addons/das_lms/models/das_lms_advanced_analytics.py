# -*- coding: utf-8 -*-
from datetime import timedelta

from html import escape

from markupsafe import Markup

from odoo import _, api, fields, models

from .course_enrollment import DAS_LMS_INACTIVE_DAYS


class DasLmsAdvancedAnalytics(models.TransientModel):
    """Vista analítica por curso (agregados desde course.enrollment).

    Pensada como centro de consulta tabular; pivot/lista/gráficos nativos
    siguen en la acción «Vista técnica».
    """

    _name = 'das.lms.advanced.analytics'
    _description = 'Análisis avanzado DAS LMS (panel)'

    name = fields.Char(string='Título', default=lambda self: _('Análisis avanzado'), readonly=True)

    header_date_display = fields.Char(string='Fecha', compute='_compute_aux_html', readonly=True)

    total_enrollments = fields.Integer(string='Total inscritos', readonly=True)
    total_courses_active = fields.Integer(string='Cursos con datos', readonly=True)
    avg_progress_general = fields.Float(
        string='Avance medio global (%)',
        digits=(16, 1),
        readonly=True,
    )
    count_completados = fields.Integer(string='Inscripciones completadas', readonly=True)

    aux_html = fields.Html(
        string='Contexto visual',
        sanitize=False,
        compute='_compute_aux_html',
        readonly=True,
        help='Mini resumen gráfico del engagement (complemento a la tabla).',
    )

    line_ids = fields.One2many(
        'das.lms.analytics.course.line',
        'analytics_id',
        string='Por curso',
        readonly=True,
    )

    @api.depends(
        'line_ids',
        'line_ids.total_enrolled',
        'line_ids.avg_progress',
        'line_ids.avg_progress_int',
        'line_ids.course_id',
        'total_enrollments',
        'total_courses_active',
        'avg_progress_general',
        'count_completados',
    )
    def _compute_aux_html(self):
        for rec in self:
            today = fields.Date.context_today(rec)
            rec.header_date_display = today.strftime('%d/%m/%Y')
            rec.aux_html = rec._das_lms_analytics_build_mini_engagement()

    def _das_lms_analytics_build_mini_engagement(self):
        """Una sola visual pequeña: doughnut compacto de engagement global."""
        self.ensure_one()
        Enrollment = self.env['course.enrollment'].sudo()
        all_rec = Enrollment.search([])
        s_sin = len(all_rec.filtered(lambda e: e.engagement_status == 'sin_iniciar'))
        s_prog = len(all_rec.filtered(lambda e: e.engagement_status == 'en_progreso'))
        s_done = len(all_rec.filtered(lambda e: e.engagement_status == 'completado'))
        s_ina = len(all_rec.filtered(lambda e: e.engagement_status == 'inactivo'))
        total_eng = s_sin + s_prog + s_done + s_ina
        parts = ['<div class="o_das_lms_analytics_mini_chart">']
        parts.append('<span class="o_das_lms_analytics_mini_chart__label">Engagement global</span>')
        if total_eng <= 0:
            parts.append('<span class="text-muted small">Sin datos.</span></div>')
            return Markup(''.join(parts))
        spec = [
            (s_sin, '#94a3b8', _('Sin iniciar')),
            (s_prog, '#0ea5e9', _('En progreso')),
            (s_done, '#22c55e', _('Completados')),
            (s_ina, '#f87171', _('Inactivos')),
        ]
        cursor = 0.0
        stops = []
        for count, color, _lbl in spec:
            if count <= 0:
                continue
            deg = 360.0 * count / total_eng
            stops.append('%s %.4fdeg %.4fdeg' % (color, cursor, cursor + deg))
            cursor += deg
        grad = 'conic-gradient(from 0deg, %s)' % ', '.join(stops)
        legend = ''.join(
            '<span class="o_das_lms_analytics_mini_leg"><i style="background:%s"></i>%s %s</span>'
            % (color, escape(str(lbl)), cnt)
            for cnt, color, lbl in spec
            if cnt > 0
        )
        parts.append(
            '<div class="o_das_lms_analytics_mini_donut" style="background:%s" title="Distribución inscripciones"></div>'
            % grad
        )
        parts.append('<div class="o_das_lms_analytics_mini_legwrap">%s</div>' % legend)
        parts.append('</div>')
        return Markup(''.join(parts))

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        Enrollment = self.env['course.enrollment'].sudo()
        all_rec = Enrollment.search([])

        res['name'] = _('Análisis avanzado')
        res['total_enrollments'] = len(all_rec)
        courses = all_rec.mapped('course_id').filtered(lambda c: c)
        res['total_courses_active'] = len(courses)
        res['count_completados'] = len(all_rec.filtered(lambda e: e.engagement_status == 'completado'))

        if all_rec:
            res['avg_progress_general'] = round(sum(all_rec.mapped('progress')) / len(all_rec), 1)
        else:
            res['avg_progress_general'] = 0.0

        line_commands = []
        for course in courses.sorted('name'):
            sub = all_rec.filtered(lambda e, c=course: e.course_id == c)
            if not sub:
                continue
            last_times = [t for t in sub.mapped('last_activity_at') if t]
            last_activity_max = max(last_times) if last_times else False
            ld = {
                'course_id': course.id,
                'total_enrolled': len(sub),
                'count_sin_iniciar': len(sub.filtered(lambda e: e.engagement_status == 'sin_iniciar')),
                'count_en_progreso': len(sub.filtered(lambda e: e.engagement_status == 'en_progreso')),
                'count_completados': len(sub.filtered(lambda e: e.engagement_status == 'completado')),
                'count_inactivos': len(sub.filtered(lambda e: e.engagement_status == 'inactivo')),
                'avg_progress': round(sum(sub.mapped('progress')) / len(sub), 1),
                'avg_progress_int': int(round(sum(sub.mapped('progress')) / len(sub))),
                'last_activity_max': last_activity_max,
            }
            line_commands.append((0, 0, ld))
        res['line_ids'] = line_commands

        return res

    def action_refresh(self):
        return self.env['ir.actions.act_window']._for_xml_id('das_lms.action_course_enrollment_analytics')

    def action_open_technical_views(self):
        """Lista, pivot y gráficos nativos con buscador y filtros (course.enrollment)."""
        return self.env['ir.actions.act_window']._for_xml_id('das_lms.action_course_enrollment_analytics_technical')

    def action_open_dashboard(self):
        return self.env['ir.actions.act_window']._for_xml_id('das_lms.action_das_lms_dashboard')


class DasLmsAnalyticsCourseLine(models.TransientModel):
    _name = 'das.lms.analytics.course.line'
    _description = 'Línea resumen por curso (análisis avanzado DAS LMS)'
    _order = 'course_id'

    analytics_id = fields.Many2one(
        'das.lms.advanced.analytics',
        string='Análisis',
        ondelete='cascade',
        required=True,
    )
    course_id = fields.Many2one('slide.channel', string='Curso', readonly=True)
    total_enrolled = fields.Integer(string='Inscritos', readonly=True)
    count_sin_iniciar = fields.Integer(string='Sin iniciar', readonly=True)
    count_en_progreso = fields.Integer(string='En progreso', readonly=True)
    count_completados = fields.Integer(string='Completados', readonly=True)
    count_inactivos = fields.Integer(string='Inactivos', readonly=True)
    avg_progress = fields.Float(string='Avance prom. %', digits=(16, 1), readonly=True)
    avg_progress_int = fields.Integer(string='Avance %', readonly=True)
    last_activity_max = fields.Datetime(string='Última actividad', readonly=True)
    course_health = fields.Selection(
        [
            ('ok', 'Favorable'),
            ('watch', 'Revisar'),
            ('risk', 'Riesgo'),
        ],
        string='Estado del curso',
        compute='_compute_course_health',
        readonly=True,
    )

    @api.depends(
        'avg_progress',
        'total_enrolled',
        'count_inactivos',
        'last_activity_max',
    )
    def _compute_course_health(self):
        now = fields.Datetime.now()
        limit = now - timedelta(days=DAS_LMS_INACTIVE_DAYS)
        for rec in self:
            ap = rec.avg_progress or 0.0
            stale = (
                rec.total_enrolled
                and (not rec.last_activity_max or rec.last_activity_max < limit)
            )
            low = rec.total_enrolled >= 2 and ap < 25.0
            if low or stale:
                rec.course_health = 'risk'
            elif rec.count_inactivos or ap < 50.0:
                rec.course_health = 'watch'
            else:
                rec.course_health = 'ok'
