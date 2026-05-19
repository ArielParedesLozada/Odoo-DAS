{
    'name': 'DAS LMS Certificates',
    'version': '1.0',
    'category': 'eLearning',
    'summary': 'Generación y validación de certificados dinámicos para cursos',
    'description': """
        Módulo complementario para das_lms que permite la generación de certificados
        en formato PDF dinámico (Aprobación y Participación) e incluye validación por Código QR.
    """,
    'author': 'DAS Team',
    'depends': ['base', 'web', 'das_lms', 'website_slides_survey'],
    'data': [
        'report/certificate_report.xml',
        'views/course_enrollment_inherit_views.xml',
        'views/portal_templates_inherit.xml',
        'views/slide_slide_inherit_views.xml',
        'views/slide_channel_inherit_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
