# -*- coding: utf-8 -*-
{
    'name': 'DAS - Preferencias de usuario y Email Marketing',
    'summary': (
        'Formulario obligatorio al crear cuenta: intereses, cumpleaños, nivel de experiencia '
        'y aceptación legal. Solo comunicación por correo electrónico.'
    ),
    'version': '18.0.2.2.0',
    'category': 'Marketing/Email Marketing',
    'author': 'DAS',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'portal',
        'website',
        'auth_signup',
        'mass_mailing',
    ],
    'data': [
        'security/das_email_preferences_security.xml',
        'security/ir.model.access.csv',
        'data/das_email_interest_data.xml',
        'views/das_email_interest_views.xml',
        'views/das_email_preference_views.xml',
        'views/res_partner_views.xml',
        'views/res_users_views.xml',
        'views/portal_email_preferences_templates.xml',
        'views/mass_mailing_menus.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'das_email_preferences/static/src/scss/das_email_preferences.scss',
        ],
    },
    'installable': True,
    'application': False,
}
