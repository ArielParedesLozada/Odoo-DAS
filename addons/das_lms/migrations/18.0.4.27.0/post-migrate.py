# -*- coding: utf-8 -*-
"""Corte de inscripción: valores por defecto en cursos existentes."""


def migrate(cr, version):
    import logging

    from odoo import api, SUPERUSER_ID

    from odoo.addons.das_lms.models.das_lms_constants import DAS_LMS_REGISTRATION_CUTOFF_DAYS_DEFAULT

    _logger = logging.getLogger(__name__)
    env = api.Environment(cr, SUPERUSER_ID, {})
    Channel = env['slide.channel'].sudo()

    _logger.info(
        'DAS LMS inscripciones: aplicando registration_cutoff_days=%s en cursos existentes.',
        DAS_LMS_REGISTRATION_CUTOFF_DAYS_DEFAULT,
    )

    missing_cutoff = Channel.search([
        '|',
        ('registration_cutoff_days', '=', False),
        ('registration_cutoff_days', '=', 0),
    ])
    if missing_cutoff:
        missing_cutoff.write({
            'registration_cutoff_days': DAS_LMS_REGISTRATION_CUTOFF_DAYS_DEFAULT,
        })
        _logger.info(
            'DAS LMS inscripciones: %s curso(s) actualizados con días de corte por defecto.',
            len(missing_cutoff),
        )

    invalid_dates = Channel.search([
        ('das_start_date', '!=', False),
        ('das_end_date', '!=', False),
    ]).filtered(lambda ch: ch.das_end_date < ch.das_start_date)
    for channel in invalid_dates:
        _logger.error(
            'DAS LMS inscripciones: curso id=%s «%s» tiene fecha fin (%s) anterior al inicio (%s).',
            channel.id,
            channel.display_name,
            channel.das_end_date,
            channel.das_start_date,
        )

    no_end = Channel.search([('das_end_date', '=', False)])
    if no_end:
        _logger.warning(
            'DAS LMS inscripciones: %s curso(s) sin das_end_date; el corte por días solo aplica con fecha de fin.',
            len(no_end),
        )
