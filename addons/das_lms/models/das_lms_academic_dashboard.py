# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class DasLmsAcademicDashboard(models.TransientModel):
    """Panel resumido de KPIs y resumen por curso (solo lectura de course.enrollment)."""

    _name = 'das.lms.academic.dashboard'
    _description = 'Dashboard académico DAS LMS'

    name = fields.Char(string='Título', default=lambda self: _('Dashboard académico'), readonly=True)

    total_enrollments = fields.Integer(string='Inscripciones totales', readonly=True)
    total_courses_with_students = fields.Integer(string='Cursos con inscritos', readonly=True)
    active_students = fields.Integer(
        string='Alumnos activos',
        readonly=True,
        help='Inscripciones con estado académico «Activo».',
    )
    count_sin_iniciar = fields.Integer(string='Sin iniciar', readonly=True)
    count_en_progreso = fields.Integer(string='En progreso', readonly=True)
    count_completados = fields.Integer(string='Completados', readonly=True)
    count_inactivos = fields.Integer(string='Inactivos', readonly=True)
    avg_progress_general = fields.Float(
        string='Promedio de avance (%)',
        digits=(16, 1),
        readonly=True,
    )

    line_ids = fields.One2many(
        'das.lms.dashboard.course.line',
        'dashboard_id',
        string='Resumen por curso',
        readonly=True,
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        Enrollment = self.env['course.enrollment'].sudo()
        all_rec = Enrollment.search([])

        res['name'] = _('Dashboard académico')
        res['total_enrollments'] = len(all_rec)

        courses = all_rec.mapped('course_id').filtered(lambda c: c)
        res['total_courses_with_students'] = len(courses)

        res['active_students'] = len(all_rec.filtered(lambda e: e.status == 'activo'))
        res['count_sin_iniciar'] = len(all_rec.filtered(lambda e: e.engagement_status == 'sin_iniciar'))
        res['count_en_progreso'] = len(all_rec.filtered(lambda e: e.engagement_status == 'en_progreso'))
        res['count_completados'] = len(all_rec.filtered(lambda e: e.engagement_status == 'completado'))
        res['count_inactivos'] = len(all_rec.filtered(lambda e: e.engagement_status == 'inactivo'))

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
            line_commands.append((0, 0, {
                'course_id': course.id,
                'total_enrolled': len(sub),
                'count_sin_iniciar': len(sub.filtered(lambda e: e.engagement_status == 'sin_iniciar')),
                'count_en_progreso': len(sub.filtered(lambda e: e.engagement_status == 'en_progreso')),
                'count_completados': len(sub.filtered(lambda e: e.engagement_status == 'completado')),
                'count_inactivos': len(sub.filtered(lambda e: e.engagement_status == 'inactivo')),
                'avg_progress': round(sum(sub.mapped('progress')) / len(sub), 1),
                'last_activity_max': last_activity_max,
            }))
        res['line_ids'] = line_commands
        return res

    def action_refresh(self):
        return self.env['ir.actions.act_window']._for_xml_id('das_lms.action_das_lms_dashboard')

    def action_open_enrollments(self):
        return self.env['ir.actions.actions']._for_xml_id('das_lms.action_course_enrollment')

    def action_open_analytics(self):
        """Vistas pivot y gráficas (uso avanzado)."""
        return self.env['ir.actions.actions']._for_xml_id('das_lms.action_course_enrollment_analytics')


class DasLmsDashboardCourseLine(models.TransientModel):
    _name = 'das.lms.dashboard.course.line'
    _description = 'Resumen por curso (dashboard DAS LMS)'
    _order = 'course_id'

    dashboard_id = fields.Many2one(
        'das.lms.academic.dashboard',
        string='Dashboard',
        ondelete='cascade',
        required=True,
    )
    course_id = fields.Many2one('slide.channel', string='Curso', readonly=True)
    total_enrolled = fields.Integer(string='Total inscritos', readonly=True)
    count_sin_iniciar = fields.Integer(string='Sin iniciar', readonly=True)
    count_en_progreso = fields.Integer(string='En progreso', readonly=True)
    count_completados = fields.Integer(string='Completados', readonly=True)
    count_inactivos = fields.Integer(string='Inactivos', readonly=True)
    avg_progress = fields.Float(string='Avance promedio (%)', digits=(16, 1), readonly=True)
    last_activity_max = fields.Datetime(string='Última actividad (más reciente)', readonly=True)
