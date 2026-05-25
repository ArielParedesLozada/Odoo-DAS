# -*- coding: utf-8 -*-
{
    'name': 'DAS - Campañas automáticas Email Marketing',
    'summary': (
        'Campañas automáticas de Email Marketing basadas en preferencias de usuario '
        'y calendario académico DAS LMS (cumpleaños, promociones, newsletter).'
    ),
    'version': '18.0.1.4.6',
    'category': 'Marketing/Email Marketing',
    'author': 'DAS',
    'license': 'LGPL-3',
    'depends': [
        'das_email_preferences',
        'das_lms',
        'mass_mailing',
    ],
    'data': [
        'security/das_email_campaigns_security.xml',
        'security/ir.model.access.csv',
        'data/das_email_mail_layout.xml',
        'data/mail_template_data.xml',
        'data/das_email_list_mail_templates.xml',
        'data/das_email_campaign_config_data.xml',
        'data/das_email_mailing_filter_data.xml',
        'data/das_email_mailing_list_data.xml',
        'data/ir_cron_data.xml',
        'views/das_email_campaign_config_views.xml',
        'views/das_email_campaign_log_views.xml',
        'views/mailing_mailing_views.xml',
        'views/mailing_list_views.xml',
        'views/slide_channel_views.xml',
        'views/das_email_campaign_menus.xml',
    ],
    'installable': True,
    'application': False,
    'post_init_hook': 'post_init_hook',
}
