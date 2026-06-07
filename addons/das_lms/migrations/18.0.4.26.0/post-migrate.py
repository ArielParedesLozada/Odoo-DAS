# -*- coding: utf-8 -*-
"""Renombrar etiquetas de modalidad académica (slide.channel.das_modality).

Las claves técnicas (grabado, en_vivo, mixto) se conservan; solo cambian las etiquetas
mostradas en backend, portal y website:
  En vivo → Presencial | Grabado → Virtual | Mixto → Híbrido
"""


def migrate(cr, version):
    import logging

    from odoo import api, SUPERUSER_ID

    _logger = logging.getLogger(__name__)
    env = api.Environment(cr, SUPERUSER_ID, {})

    _logger.info(
        'DAS LMS modalidades: aplicando renombre de etiquetas — '
        'En vivo → Presencial, Grabado → Virtual, Mixto → Híbrido '
        '(claves técnicas sin cambio: en_vivo, grabado, mixto).'
    )

    Channel = env['slide.channel'].sudo()
    Enrollment = env['course.enrollment'].sudo()
    modality_keys = ('grabado', 'en_vivo', 'mixto')

    for key in modality_keys:
        channel_count = Channel.search_count([('das_modality', '=', key)])
        if channel_count:
            _logger.info(
                'DAS LMS modalidades: %s curso(s) slide.channel con das_modality=%r '
                '(etiqueta actualizada al recargar el módulo).',
                channel_count,
                key,
            )

    for key in modality_keys:
        enrollment_count = Enrollment.search_count([('modality', '=', key)])
        if enrollment_count:
            _logger.info(
                'DAS LMS modalidades: %s inscripción(es) course.enrollment con modality=%r '
                '(etiqueta actualizada al recargar el módulo).',
                enrollment_count,
                key,
            )
