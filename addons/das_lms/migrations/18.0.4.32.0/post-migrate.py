# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """v18.0.4.32.0: corte de inscripción respecto a das_start_date (no das_end_date)."""
    _logger.info(
        'DAS LMS: corte de inscripción ahora usa das_start_date − registration_cutoff_days. '
        'Revise cursos con fechas académicas para validar el último día de inscripción.'
    )
