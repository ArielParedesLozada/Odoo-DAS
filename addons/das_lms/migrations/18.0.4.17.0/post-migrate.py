# -*- coding: utf-8 -*-
"""Recalcular is_das_student y limpiar espejos de usuarios internos."""


def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    Enrollment = env['course.enrollment'].sudo()
    if 'is_das_student' not in Enrollment._fields:
        return
    all_rows = Enrollment.search([])
    if all_rows:
        all_rows._compute_is_das_student()
    Enrollment._das_lms_prune_non_student_enrollments()
