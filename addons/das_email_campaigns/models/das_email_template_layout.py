# -*- coding: utf-8 -*-
"""Plantillas HTML compatibles con Gmail (tablas + bgcolor + estilos inline)."""

from .das_email_assets import das_email_logo_src

_BADGE_COLORS = {
    'newsletter': ('#2563eb', '#eff6ff', '✨ Newsletter exclusiva'),
    'interest': ('#7c3aed', '#f5f3ff', '🎯 Seleccionado para ti'),
    'category': ('#ea580c', '#fff7ed', '📚 Tu categoría favorita'),
    'level': ('#059669', '#ecfdf5', '🚀 Tu nivel, tu ruta'),
    'upcoming': ('#dc2626', '#fef2f2', '⏰ ¡Empieza pronto!'),
    'birthday': ('#db2777', '#fdf2f8', '🎂 Feliz cumpleaños'),
    'new_courses': ('#2563eb', '#eff6ff', '🆕 Curso nuevo'),
    'experience': ('#059669', '#ecfdf5', '💡 Recomendación DAS'),
}

_HEADER_BG = {
    'newsletter': '#1e40af',
    'interest': '#6d28d9',
    'category': '#c2410c',
    'level': '#047857',
    'upcoming': '#b91c1c',
    'birthday': '#be185d',
    'new_courses': '#1e40af',
    'experience': '#047857',
}

_SUBJECTS = {
    'newsletter': '🎓 Novedades exclusivas · Academia Virtual DAS',
    'interest': '🎯 Cursos seleccionados según tus intereses',
    'category': '📚 Novedades en tu categoría favorita',
    'level': '🚀 Tu ruta de aprendizaje personalizada',
    'upcoming': '⏰ Un curso que te interesa inicia pronto',
    'birthday': '🎂 ¡Feliz cumpleaños! · Academia Virtual DAS',
    'new_courses': '🆕 Nuevo curso disponible para ti',
    'experience': '💡 Cursos recomendados para tu nivel',
}

_CONTENT = {
    'newsletter': {
        'headline': 'Descubre lo nuevo en tu academia virtual',
        'lead': (
            'Hemos preparado un resumen con <strong>cursos, talleres y certificaciones</strong> '
            'pensados para impulsar tu perfil profesional.'
        ),
        'bullets': [
            ('Nuevos cursos', 'Contenido actualizado cada semana'),
            ('Rutas personalizadas', 'Según tus intereses registrados'),
            ('Certificaciones', 'Valida tus competencias con DAS'),
        ],
        'cta': 'Explorar novedades',
        'cta_hint': 'Accede a la plataforma y continúa aprendiendo hoy mismo.',
    },
    'interest': {
        'headline': 'Cursos que encajan con tus intereses',
        'lead': (
            'Porque elegiste tus temas favoritos, te mostramos '
            '<strong>formación relevante</strong> para seguir creciendo en lo que más te apasiona.'
        ),
        'bullets': [
            ('Contenido a medida', 'Alineado a tus gustos'),
            ('Docentes expertos', 'Aprende con los mejores'),
            ('Flexibilidad total', 'Estudia a tu ritmo'),
        ],
        'cta': 'Ver cursos recomendados',
        'cta_hint': 'Tu próximo gran paso está a un clic de distancia.',
    },
    'category': {
        'headline': 'Novedades en tu categoría preferida',
        'lead': (
            'Tenemos <strong>nuevas propuestas formativas</strong> en eLearning, '
            'certificaciones y talleres en vivo — justo lo que buscas.'
        ),
        'bullets': [
            ('eLearning', 'Cursos flexibles 100% online'),
            ('Certificaciones', 'Impulsa tu currículum'),
            ('Talleres en vivo', 'Aprende con sesiones en directo'),
        ],
        'cta': 'Ver oferta formativa',
        'cta_hint': 'Plazas limitadas en algunos programas. ¡No te quedes fuera!',
    },
    'level': {
        'headline': 'Tu ruta de aprendizaje ideal',
        'lead': (
            'Según tu <strong>nivel de experiencia</strong>, armamos una selección de cursos '
            'para que avances con confianza y sin saltarte etapas.'
        ),
        'bullets': [
            ('Nivel adecuado', 'Ni muy fácil, ni imposible'),
            ('Progresión clara', 'Del concepto a la práctica'),
            ('Resultados reales', 'Habilidades aplicables ya'),
        ],
        'cta': 'Descubrir mi ruta',
        'cta_hint': 'Invierte en ti: el mejor momento es ahora.',
    },
    'upcoming': {
        'headline': 'Un curso que te interesa inicia pronto',
        'lead': (
            'El calendario académico avanza y hay un <strong>curso próximo a iniciar</strong> '
            'que coincide con tus preferencias. ¡Asegura tu cupo!'
        ),
        'bullets': [
            ('Inicio cercano', 'Prepárate con antelación'),
            ('Cupos limitados', 'Inscríbete a tiempo'),
            ('Contenido premium', 'Calidad Academia Virtual DAS'),
        ],
        'cta': 'Inscribirme ahora',
        'cta_hint': 'El periodo de matrícula puede cerrar en cualquier momento.',
    },
    'birthday': {
        'headline': '¡Feliz cumpleaños desde Academia Virtual DAS!',
        'lead': (
            'Hoy es tu día y queremos celebrarlo contigo. '
            '<strong>Gracias por ser parte</strong> de nuestra comunidad de aprendizaje.'
        ),
        'bullets': [
            ('Un regalo para ti', 'Sigue explorando nuevos cursos'),
            ('Comunidad DAS', 'Miles de estudiantes como tú'),
            ('Tu crecimiento', 'Nuestro mayor orgullo'),
        ],
        'cta': 'Celebrar aprendiendo',
        'cta_hint': 'Que este nuevo año venga lleno de logros y conocimiento.',
    },
    'new_courses': {
        'headline': '¡Nuevo curso disponible para ti!',
        'lead': (
            'Acabamos de publicar un curso que encaja con tus intereses. '
            '<strong>Sé de los primeros</strong> en descubrirlo.'
        ),
        'bullets': [
            ('Recién publicado', 'Contenido de última generación'),
            ('Alta demanda', 'Los mejores cursos se llenan rápido'),
            ('Certificado DAS', 'Valida lo aprendido'),
        ],
        'cta': 'Ver curso nuevo',
        'cta_hint': 'Las plazas son limitadas. Reserva la tuya hoy.',
    },
    'experience': {
        'headline': 'Recomendaciones para tu nivel',
        'lead': (
            'Analizamos tu perfil y seleccionamos <strong>cursos ideales</strong> '
            'para que sigas avanzando sin fricción.'
        ),
        'bullets': [
            ('Curado para ti', 'Sin perder tiempo buscando'),
            ('Enfoque práctico', 'Aprende haciendo'),
            ('Comunidad activa', 'Conecta con otros estudiantes'),
        ],
        'cta': 'Ver recomendaciones',
        'cta_hint': 'El conocimiento correcto, en el momento correcto.',
    },
}

_FONT = 'Arial,Helvetica Neue,Helvetica,sans-serif'


def das_email_subject(variant):
    return _SUBJECTS.get(variant, _SUBJECTS['newsletter'])


def das_email_base_url(env):
    return (env['ir.config_parameter'].sudo().get_param('web.base.url') or '').rstrip('/')


def _bullet_cells(bullets):
    cells = ''
    for title, desc in bullets:
        cells += (
            '<td width="33%" valign="top" style="padding:4px;">'
            '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
            'bgcolor="#f8fafc" style="background-color:#f8fafc;border:1px solid #e2e8f0;">'
            '<tr><td align="center" style="padding:14px 10px;font-family:{font};">'
            '<p style="margin:0 0 6px;font-size:13px;line-height:18px;font-weight:bold;color:#0f172a;">{title}</p>'
            '<p style="margin:0;font-size:11px;line-height:16px;color:#64748b;">{desc}</p>'
            '</td></tr></table></td>'
        ).format(font=_FONT, title=title, desc=desc)
    return cells


def das_email_render(variant, env, *, extra_html='', cta_path='/slides'):
    """HTML con tablas y bgcolor — compatible con Gmail, Outlook y Apple Mail."""
    logo = das_email_logo_src(env)
    content = _CONTENT.get(variant, _CONTENT['newsletter'])
    accent, badge_bg, badge_text = _BADGE_COLORS.get(variant, _BADGE_COLORS['newsletter'])
    header_bg = _HEADER_BG.get(variant, '#1e40af')
    btn_bg = accent if accent.startswith('#') else '#2563eb'

    return (
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
        'bgcolor="#eef2ff" style="background-color:#eef2ff;margin:0;padding:0;">'
        '<tr><td align="center" style="padding:24px 12px;">'

        '<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" '
        'bgcolor="#ffffff" style="background-color:#ffffff;width:600px;max-width:600px;'
        'border:1px solid #dbeafe;">'

        # Cabecera
        '<tr><td align="center" bgcolor="{header_bg}" style="background-color:{header_bg};'
        'padding:32px 24px 24px;font-family:{font};">'
        '<img src="{logo}" alt="Academia Virtual DAS" width="140" height="auto" '
        'style="display:block;margin:0 auto 14px;border:0;outline:none;"/>'
        '<p style="margin:0;font-size:11px;line-height:16px;letter-spacing:2px;text-transform:uppercase;'
        'color:#ffffff;font-family:{font};">Academia Virtual de Tecnología</p>'
        '</td></tr>'

        # Cuerpo
        '<tr><td style="padding:28px 28px 8px;font-family:{font};">'
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">'
        '<tr><td align="center" style="padding-bottom:18px;">'
        '<table role="presentation" cellpadding="0" cellspacing="0" border="0">'
        '<tr><td align="center" bgcolor="{badge_bg}" style="background-color:{badge_bg};'
        'padding:8px 18px;font-family:{font};">'
        '<span style="font-size:12px;line-height:16px;font-weight:bold;color:{accent};">{badge_text}</span>'
        '</td></tr></table></td></tr></table>'
        '<p style="margin:0 0 10px;font-size:16px;line-height:24px;color:#334155;font-family:{font};">'
        'Hola, <strong style="color:#0f172a;"><t t-out="object.name"/></strong> 👋</p>'
        '<p style="margin:0 0 14px;font-size:26px;line-height:32px;font-weight:bold;color:#0f172a;'
        'font-family:{font};">{headline}</p>'
        '<p style="margin:0 0 20px;font-size:15px;line-height:24px;color:#475569;font-family:{font};">'
        '{lead}</p>'
        '</td></tr>'

        # Tarjetas
        '<tr><td style="padding:0 20px 8px;">'
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
        '{bullets}'
        '</tr></table></td></tr>'

        '{extra_block}'

        # CTA
        '<tr><td align="center" style="padding:24px 28px 12px;font-family:{font};">'
        '<table role="presentation" cellpadding="0" cellspacing="0" border="0" class="das-btn">'
        '<tr><td align="center" bgcolor="{btn_bg}" style="background-color:{btn_bg};border-radius:8px;">'
        '<a href="{slides}" target="_blank" style="display:inline-block;padding:14px 32px;'
        'font-size:15px;line-height:20px;font-weight:bold;color:#ffffff;text-decoration:none;'
        'font-family:{font};background-color:{btn_bg};border-radius:8px;">{cta} →</a>'
        '</td></tr></table>'
        '<p style="margin:14px 0 0;font-size:12px;line-height:18px;color:#94a3b8;font-family:{font};">'
        '{cta_hint}</p>'
        '</td></tr>'

        # Pie
        '<tr><td align="center" bgcolor="#f8fafc" style="background-color:#f8fafc;'
        'border-top:1px solid #e2e8f0;padding:20px 24px;font-family:{font};">'
        '<p style="margin:0 0 8px;font-size:13px;line-height:18px;font-weight:bold;color:#475569;">'
        'Academia Virtual DAS</p>'
        '<p style="margin:0;font-size:11px;line-height:17px;color:#94a3b8;">'
        'Formación de calidad · eLearning · Certificaciones · Talleres en vivo<br/>'
        'Recibes este correo porque completaste tus preferencias de comunicación.</p>'
        '</td></tr>'

        '</table></td></tr></table>'
    ).format(
        font=_FONT,
        logo=logo,
        header_bg=header_bg,
        badge_bg=badge_bg,
        accent=accent,
        badge_text=badge_text,
        headline=content['headline'],
        lead=content['lead'],
        bullets=_bullet_cells(content['bullets']),
        extra_block=extra_html or '',
        btn_bg=btn_bg,
        slides=cta_path,
        cta=content['cta'],
        cta_hint=content['cta_hint'],
    )


def das_email_render_course_cards_html(channels, env, title='Cursos destacados'):
    if not channels:
        return ''
    base = das_email_base_url(env) or ''
    rows = ''
    for channel in channels[:4]:
        href = channel._das_lms_public_course_href()
        if base and href.startswith('/'):
            href = base + href
        start = channel.das_start_date and str(channel.das_start_date) or ''
        modality = dict(channel._fields['das_modality'].selection).get(channel.das_modality, '')
        meta = ' · '.join(x for x in (start and ('Inicio: %s' % start), modality) if x)
        meta_row = (
            '<p style="margin:6px 0 0;font-size:12px;line-height:16px;color:#64748b;font-family:{font};">'
            '{meta}</p>'.format(font=_FONT, meta=meta)
        ) if meta else ''
        rows += (
            '<tr><td style="padding:6px 0;">'
            '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
            'bgcolor="#ffffff" style="background-color:#ffffff;border:1px solid #e2e8f0;'
            'border-left:4px solid #2563eb;">'
            '<tr><td style="padding:14px 16px;font-family:{font};">'
            '<a href="{href}" style="font-size:15px;line-height:20px;font-weight:bold;'
            'color:#1d4ed8;text-decoration:none;">{name}</a>'
            '{meta_row}'
            '</td></tr></table></td></tr>'
        ).format(font=_FONT, href=href, name=channel.name, meta_row=meta_row)

    return (
        '<tr><td style="padding:8px 20px 0;font-family:{font};">'
        '<p style="margin:0 0 10px;font-size:13px;line-height:16px;font-weight:bold;color:#64748b;'
        'text-transform:uppercase;letter-spacing:1px;">{title}</p>'
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">'
        '{rows}</table></td></tr>'
    ).format(font=_FONT, title=title, rows=rows)
