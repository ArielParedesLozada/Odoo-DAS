# -*- coding: utf-8 -*-
"""Constantes compartidas DAS LMS (sin dependencias entre modelos)."""

# Modalidades académicas de slide.channel (das_modality) y course.enrollment (modality).
# Etiquetas renombradas (v18.0.4.26.0): claves técnicas sin cambio para no migrar datos.
#   en_vivo → Presencial | grabado → Virtual | mixto → Híbrido
DAS_LMS_ACADEMIC_MODALITY = [
    ('grabado', 'Virtual'),
    ('en_vivo', 'Presencial'),
    ('mixto', 'Híbrido'),
]
