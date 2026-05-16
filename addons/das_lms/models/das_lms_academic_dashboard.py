# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from html import escape

from markupsafe import Markup

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
    count_courses_proximo = fields.Integer(
        string='Cursos próximos',
        readonly=True,
        help='Cursos con inscritos cuyo ciclo académico DAS está «Próximo a iniciar».',
    )
    count_courses_en_curso = fields.Integer(
        string='Cursos en curso',
        readonly=True,
        help='Cursos con inscritos en periodo lectivo activo según fechas DAS.',
    )
    count_courses_finalizado = fields.Integer(
        string='Cursos finalizados',
        readonly=True,
        help='Cursos con inscritos cuyo ciclo académico DAS ya finalizó.',
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

    # --- Solo presentación (no alteran KPIs ni default_get) ---
    header_date_display = fields.Char(
        string='Fecha panel',
        compute='_compute_dashboard_visuals',
    )
    charts_html = fields.Html(
        string='Gráficos (vista previa)',
        sanitize=False,
        compute='_compute_dashboard_visuals',
    )
    activity_html = fields.Html(
        string='Actividad reciente (vista previa)',
        sanitize=False,
        compute='_compute_dashboard_visuals',
    )

    @api.depends(
        'line_ids',
        'line_ids.total_enrolled',
        'line_ids.course_id',
        'line_ids.avg_progress',
        'line_ids.avg_progress_int',
        'line_ids.last_activity_max',
        'total_enrollments',
        'total_courses_with_students',
        'active_students',
        'avg_progress_general',
        'count_sin_iniciar',
        'count_en_progreso',
        'count_completados',
        'count_inactivos',
        'count_courses_proximo',
        'count_courses_en_curso',
        'count_courses_finalizado',
    )
    def _compute_dashboard_visuals(self):
        for rec in self:
            today = fields.Date.context_today(rec)
            rec.header_date_display = today.strftime('%d/%m/%Y')
            rec.charts_html = rec._das_lms_build_charts_markup()
            rec.activity_html = rec._das_lms_build_activity_markup()

    def _das_lms_build_charts_markup(self):
        self.ensure_one()
        parts = ['<div class="o_das_lms_charts_root">']

        # --- Fila 1: donut (izq.) + barras horizontales top inscritos (der.) ---
        parts.append('<div class="o_das_lms_charts_top">')

        # Donut — misma fuente numérica que los KPI (solo presentación).
        s_sin = int(self.count_sin_iniciar or 0)
        s_prog = int(self.count_en_progreso or 0)
        s_done = int(self.count_completados or 0)
        s_ina = int(self.count_inactivos or 0)
        total_eng = s_sin + s_prog + s_done + s_ina
        parts.append('<div class="o_das_lms_chart-block o_das_lms_chart-block--donut">')
        parts.append('<h6 class="o_das_lms_chart-title">Distribución académica</h6>')
        if total_eng <= 0:
            parts.append('<p class="text-muted small mb-0">Sin datos de engagement.</p>')
        else:
            spec = [
                (s_sin, '#64748b', _('Sin iniciar')),
                (s_prog, '#0284c7', _('En progreso')),
                (s_done, '#16a34a', _('Completados')),
                (s_ina, '#dc2626', _('Inactivos')),
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
                '<span class="o_das_lms_legend-item"><i class="o_das_lms_legend-dot" style="background:%s"></i>%s: %s</span>'
                % (color, escape(str(lbl)), cnt)
                for cnt, color, lbl in spec
                if cnt > 0
            )
            parts.append(
                '<div class="o_das_lms_donut-wrap"><div class="o_das_lms_donut" style="background:%s"></div>'
                '<div class="o_das_lms_donut-legend">%s</div></div>' % (grad, legend)
            )
        parts.append('</div>')

        # Barras horizontales — top cursos por volumen de inscritos.
        lines = self.line_ids.sorted(lambda l: -l.total_enrolled)[:10]
        parts.append('<div class="o_das_lms_chart-block o_das_lms_chart-block--hbars">')
        parts.append('<h6 class="o_das_lms_chart-title">Top cursos por inscritos</h6>')
        if not lines:
            parts.append('<p class="text-muted small mb-0">Sin resumen por curso.</p>')
        else:
            mx = max(lines.mapped('total_enrolled')) or 1
            for line in lines:
                raw = line.course_id.display_name or ''
                name_esc = escape(raw)
                short = escape(raw[:48] + ('…' if len(raw) > 48 else ''))
                n = int(line.total_enrolled or 0)
                pct = min(100.0, 100.0 * n / mx)
                parts.append(
                    '<div class="o_das_lms_bar-row"><div class="o_das_lms_bar-name" title="%s">%s</div>'
                    '<div class="o_das_lms_bar-track"><div class="o_das_lms_bar-fill" style="width:%.1f%%"></div></div>'
                    '<div class="o_das_lms_bar-val">%s</div></div>' % (name_esc, short, pct, n)
                )
        parts.append('</div>')

        parts.append('</div>')  # charts_top

        parts.append('</div>')
        return Markup(''.join(parts))

    def _das_lms_build_activity_markup(self):
        self.ensure_one()
        Enrollment = self.env['course.enrollment'].sudo()
        parts = ['<div class="o_das_lms_activity_root">']

        last_sync_rec = Enrollment.search([('last_sync_at', '!=', False)], order='last_sync_at desc', limit=1)
        last_sync = last_sync_rec.last_sync_at if last_sync_rec else False
        # last_activity_at no está almacenado: no puede usarse en domain/order de search().
        # last_activity_date sí (store=True), coherente con la misma lógica de cómputo.
        last_act_rec = Enrollment.search(
            [('last_activity_date', '!=', False)],
            order='last_activity_date desc',
            limit=1,
        )
        last_act = last_act_rec.last_activity_at if last_act_rec else False

        parts.append('<div class="o_das_lms_activity-meta">')
        if last_sync:
            parts.append(
                '<div class="o_das_lms_activity-chip"><i class="fa fa-refresh me-1"></i><strong>Última sincronización</strong><br/>%s</div>'
                % escape(fields.Datetime.to_string(last_sync))
            )
        if last_act:
            parts.append(
                '<div class="o_das_lms_activity-chip"><i class="fa fa-clock-o me-1"></i><strong>Última actividad registrada</strong><br/>%s</div>'
                % escape(fields.Datetime.to_string(last_act))
            )
        parts.append('</div>')

        recent = Enrollment.search([], order='create_date desc', limit=4)
        parts.append('<div class="o_das_lms_activity-split">')
        parts.append('<div class="o_das_lms_activity-split__col">')
        parts.append('<h6 class="o_das_lms_activity-h">Nuevas inscripciones</h6>')
        parts.append('<ul class="o_das_lms_timeline">')
        if not recent:
            parts.append('<li class="text-muted">Sin registros recientes.</li>')
        else:
            for e in recent:
                st = escape(e.student_id.display_name or '')
                cr = escape(e.course_id.display_name or '')
                dt = e.create_date
                dts = escape(fields.Datetime.to_string(dt) if dt else '')
                parts.append(
                    '<li><span class="o_das_lms_tl-dot"></span><div class="o_das_lms_tl-body">'
                    '<div class="o_das_lms_tl-title">%s</div>'
                    '<div class="o_das_lms_tl-sub">%s</div><div class="o_das_lms_tl-date">%s</div></div></li>'
                    % (st, cr, dts)
                )
        parts.append('</ul></div>')

        done = Enrollment.search(
            [('engagement_status', '=', 'completado')],
            order='write_date desc',
            limit=3,
        )
        parts.append('<div class="o_das_lms_activity-split__col">')
        parts.append('<h6 class="o_das_lms_activity-h">Finalizaciones recientes</h6>')
        parts.append('<ul class="o_das_lms_timeline o_das_lms_timeline--compact">')
        if not done:
            parts.append('<li class="text-muted">Sin finalizaciones recientes.</li>')
        else:
            for e in done:
                st = escape(e.student_id.display_name or '')
                cr = escape(e.course_id.display_name or '')
                dts = escape(fields.Datetime.to_string(e.write_date) if e.write_date else '')
                parts.append(
                    '<li><span class="o_das_lms_tl-dot o_das_lms_tl-dot--ok"></span><div class="o_das_lms_tl-body">'
                    '<div class="o_das_lms_tl-title">%s</div><div class="o_das_lms_tl-sub">%s</div><div class="o_das_lms_tl-date">%s</div></div></li>'
                    % (st, cr, dts)
                )
        parts.append('</ul></div></div></div>')
        return Markup(''.join(parts))

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

        n_prox = n_cur = n_fin = 0
        for c in courses:
            st = c.das_academic_status
            if st == 'proximo':
                n_prox += 1
            elif st == 'en_curso':
                n_cur += 1
            elif st == 'finalizado':
                n_fin += 1
        res['count_courses_proximo'] = n_prox
        res['count_courses_en_curso'] = n_cur
        res['count_courses_finalizado'] = n_fin

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

        _sev_rank = {'danger': 0, 'warning': 1, 'info': 2, 'success': 3}
        alert_commands.sort(key=lambda cmd: _sev_rank.get(cmd[2].get('severity'), 9))
        if len(alert_commands) > 5:
            alert_commands = alert_commands[:5]

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
