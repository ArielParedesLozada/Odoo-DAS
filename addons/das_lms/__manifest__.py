# -*- coding: utf-8 -*-
{
    'name': 'DAS LMS - Inscripciones',
    'summary': 'Seguimiento y estadísticas de inscripciones eLearning (slide.channel.partner)',
    'version': '18.0.3.8.3',
    'category': 'Website/eLearning',
    'author': 'DAS',
    'license': 'LGPL-3',
    'depends': [
        'website_slides',
        'website_sale',
        'website_sale_slides',
        'website',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/das_lms_dashboard_views.xml',
        'views/course_enrollment_views.xml',
        'views/das_lms_advanced_analytics_views.xml',
        'views/slide_channel_views.xml',
        'views/product_template_website.xml',
        'views/das_lms_portal_elearning_templates.xml',
        'data/das_lms_cleanup_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'das_lms/static/src/scss/das_lms_backend.scss',
        ],
    },
    'installable': True,
    'application': False,
}
