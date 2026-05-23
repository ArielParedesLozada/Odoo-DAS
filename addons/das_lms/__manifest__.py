# -*- coding: utf-8 -*-
{
    'name': 'DAS LMS - Inscripciones',
    'summary':
        'Seguimiento LMS vía slide.channel.partner; vínculo producto-curso explícito o nativo Odoo '
        '(slide.channel.product_id / das_lms_channel_id).',
    'version': '18.0.4.23.0',
    'category': 'Website/eLearning',
    'author': 'DAS',
    'license': 'LGPL-3',
    'depends': [
        'website_slides',
        'sale',
        'account',
        'payment',
        'account_payment',
        'website_sale',
        'website_sale_slides',
        'website',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/das_lms_link_audit_views.xml',
        'views/das_lms_dashboard_views.xml',
        'views/course_enrollment_views.xml',
        'views/das_lms_invoice_backfill_wizard_views.xml',
        'views/das_lms_advanced_analytics_views.xml',
        'views/slide_channel_views.xml',
        'views/product_template_views.xml',
        'views/das_lms_slide_channel_course_website.xml',
        'views/das_lms_slide_duration_website.xml',
        'views/product_template_website.xml',
        'views/das_lms_website_sale_cart.xml',
        'views/das_lms_website_sale_payment_confirmation.xml',
        'views/das_lms_portal_elearning_templates.xml',
        'data/das_lms_cleanup_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'das_lms/static/src/scss/das_lms_backend.scss',
        ],
        'web.assets_frontend': [
            'das_lms/static/src/scss/das_lms_website_slides.scss',
            'das_lms/static/src/js/das_lms_sale_variant.js',
        ],
    },
    'installable': True,
    'application': False,
}
