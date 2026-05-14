# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

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
    alert_line_ids = fields.One2many(
        'das.lms.dashboard.alert.line',
        'dashboard_id',
        string='Alertas académicas',
        readonly=True,
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        Enrollment = self.env['course.enrollment'].sudo()
        all_rec = Enrollment.search([])
        now = fields.Datetime.now()
        stale_limit = now - timedelta(days=30)

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
        line_dicts = []
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
            line_dicts.append((course, ld))
            line_commands.append((0, 0, ld))
        res['line_ids'] = line_commands

        alert_commands = []
        seen_titles = set()
        # Cursos con mayor cantidad de alumnos sin iniciar (top 3 con al menos 2 sin iniciar)
        by_sin = sorted(line_dicts, key=lambda x: x[1]['count_sin_iniciar'], reverse=True)[:3]
        for course, ld in by_sin:
            if ld['count_sin_iniciar'] >= 2:
                key = ('sin', course.id)
                if key in seen_titles:
                    continue
                seen_titles.add(key)
                alert_commands.append((0, 0, {
                    'title': _('Curso con acumulación «sin iniciar»'),
                    'body': _('%s: %s alumnos aún sin iniciar el contenido.') % (
                        course.display_name, ld['count_sin_iniciar']),
                    'severity': 'warning',
                }))
        # Avance promedio bajo por curso (una alerta por curso)
        for course, ld in sorted(line_dicts, key=lambda x: x[1]['avg_progress']):
            if ld['total_enrolled'] >= 2 and ld['avg_progress'] < 25:
                key = ('low', course.id)
                if key in seen_titles:
                    continue
                seen_titles.add(key)
                alert_commands.append((0, 0, {
                    'title': _('Avance promedio bajo'),
                    'body': _('%s: promedio %.1f %% con %s inscritos.') % (
                        course.display_name, ld['avg_progress'], ld['total_enrolled']),
                    'severity': 'warning',
                }))
        # Alumnos inactivos (global)
        if res['count_inactivos']:
            alert_commands.append((0, 0, {
                'title': _('Alumnos inactivos'),
                'body': _('Hay %s inscripciones marcadas como inactivas (sin actividad reciente con avance incompleto).')
                % res['count_inactivos'],
                'severity': 'danger',
            }))
        # Cursos sin actividad reciente (máximo 3)
        stale_rows = []
        for course, ld in line_dicts:
            la = ld['last_activity_max']
            if ld['total_enrolled'] and (not la or la < stale_limit):
                stale_rows.append((course, la))
        stale_rows.sort(key=lambda x: x[1] or datetime(1970, 1, 1))
        for course, _la in stale_rows[:3]:
            key = ('stale', course.id)
            if key in seen_titles:
                continue
            seen_titles.add(key)
            alert_commands.append((0, 0, {
                'title': _('Curso con poca actividad reciente'),
                'body': _('%s: última actividad antigua o sin registrar.') % course.display_name,
                'severity': 'info',
            }))

        if len(alert_commands) > 10:
            alert_commands = alert_commands[:10]

        if not alert_commands:
            alert_commands.append((0, 0, {
                'title': _('Sin alertas críticas'),
                'body': _('No existen alertas académicas críticas por el momento.'),
                'severity': 'success',
            }))
        res['alert_line_ids'] = alert_commands
        return res

    def action_refresh(self):
        return self.env['ir.actions.act_window']._for_xml_id('das_lms.action_das_lms_dashboard')

    def action_open_enrollments(self):
        return self.env['ir.actions.actions']._for_xml_id('das_lms.action_course_enrollment')

    def action_open_analytics(self):
        return self.env['ir.actions.actions']._for_xml_id('das_lms.action_course_enrollment_analytics')

    def action_open_sync(self):
        """Abre la acción servidor de sincronización (mismos permisos que el menú)."""
        return self.env.ref('das_lms.action_das_lms_sync_server').sudo().read()[0]

    def action_open_elearning_courses(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Cursos eLearning'),
            'res_model': 'slide.channel',
            'view_mode': 'list,kanban,form',
            'target': 'current',
            'context': {},
        }


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
    total_enrolled = fields.Integer(string='Inscritos', readonly=True)
    count_sin_iniciar = fields.Integer(string='Sin iniciar', readonly=True)
    count_en_progreso = fields.Integer(string='En progreso', readonly=True)
    count_completados = fields.Integer(string='Completados', readonly=True)
    count_inactivos = fields.Integer(string='Inactivos', readonly=True)
    avg_progress = fields.Float(string='Avance prom. (%)', digits=(16, 1), readonly=True)
    avg_progress_int = fields.Integer(string='Avance prom. (barra)', readonly=True)
    last_activity_max = fields.Datetime(string='Última actividad', readonly=True)


class DasLmsDashboardAlertLine(models.TransientModel):
    _name = 'das.lms.dashboard.alert.line'
    _description = 'Alerta académica (dashboard DAS LMS)'

    dashboard_id = fields.Many2one(
        'das.lms.academic.dashboard',
        string='Dashboard',
        ondelete='cascade',
        required=True,
    )
    title = fields.Char(string='Título', readonly=True)
    body = fields.Text(string='Detalle', readonly=True)
    severity = fields.Selection(
        [
            ('info', 'Información'),
            ('warning', 'Atención'),
            ('danger', 'Importante'),
            ('success', 'Sin incidencias'),
        ],
        string='Nivel',
        readonly=True,
    )
