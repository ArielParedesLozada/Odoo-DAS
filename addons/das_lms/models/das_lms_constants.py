# -*- coding: utf-8 -*-
"""Constantes compartidas DAS LMS (sin dependencias entre modelos)."""

# Días antes de das_start_date en que se cierra la inscripción (valor por defecto en slide.channel).
DAS_LMS_REGISTRATION_CUTOFF_DAYS_DEFAULT = 2

# Mensaje estándar cuando el corte de inscripción ya pasó.
DAS_LMS_REGISTRATION_CLOSED_MESSAGE = 'La inscripción para este curso ha cerrado.'

# Modalidades académicas de slide.channel (das_modality) y course.enrollment (modality).
# Etiquetas renombradas (v18.0.4.26.0): claves técnicas sin cambio para no migrar datos.
#   en_vivo → Presencial | grabado → Virtual | mixto → Híbrido
DAS_LMS_ACADEMIC_MODALITY = [
    ('grabado', 'Virtual'),
    ('en_vivo', 'Presencial'),
    ('mixto', 'Híbrido'),
]
