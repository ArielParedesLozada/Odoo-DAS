# -*- coding: utf-8 -*-
"""Revertir restricciones de menús por roles DAS (restaura valores estándar Odoo 18)."""

import logging

_logger = logging.getLogger(__name__)

# xmlid -> lista de xmlids de grupos (lista vacía = sin restricción)
_MENU_STANDARD_GROUPS = {
    'base.menu_administration': ['base.group_system'],
    'base.menu_management': [],
    'base.menu_tests': ['base.group_system'],
    'website.menu_website_configuration': ['base.group_user'],
    'website_slides.website_slides_menu_root': ['website_slides.group_website_slides_officer'],
    'website_slides.website_slides_menu_courses': [],
    'website_slides.website_slides_menu_courses_courses': [],
    'website_slides.website_slides_menu_courses_content': [],
    'website_slides.website_slides_menu_configuration': [],
    'website_slides.website_slides_menu_config_settings': ['base.group_system'],
    'website_slides.website_slides_menu_config_course_groups': [],
    'website_slides.website_slides_menu_config_content_tags': [],
    'website_slides.website_slides_menu_report': ['website_slides.group_website_slides_manager'],
    'website_slides.website_slides_menu_report_courses': [],
    'website_slides.website_slides_menu_report_contents': [],
    'website_slides.website_slides_menu_report_attendees': [],
    'website_slides.website_slides_menu_report_reviews': [],
    'website_slides.website_slides_menu_report_quizzes': [],
    'website_slides.menu_slide_channel_pages': [],
    'sale.sale_menu_root': [],
    'account.menu_finance': ['account.group_account_readonly', 'account.group_account_invoice'],
    'account.menu_action_payment_term_form': ['account.group_account_manager'],
    'account.menu_action_incoterm_open': ['account.group_account_manager'],
    'contacts.menu_contacts': ['base.group_user', 'base.group_partner_manager'],
    'mass_mailing.mass_mailing_menu_root': ['mass_mailing.group_mass_mailing_user'],
    'das_lms.menu_das_lms_root': [],
    'das_lms.menu_das_lms_statistics': [],
    'das_lms.menu_das_lms_inscripciones': [],
    'das_lms.menu_das_lms_analytics': [],
    'das_lms.menu_das_lms_link_audit': [],
    'das_lms.menu_das_lms_invoice_enroll_backfill': ['base.group_system', 'base.group_erp_manager'],
    'spreadsheet_dashboard.spreadsheet_dashboard_menu_root': [],
    'mail.menu_root_discuss': ['base.group_user'],
    'utm.menu_link_tracker_root': ['base.group_no_one'],
}

_DAS_ROLE_GROUP_XMLIDS = (
    'das_lms.group_das_admin',
    'das_lms.group_das_coordinador_academico',
    'das_lms.group_das_comercial',
    'das_lms.group_das_financiero',
    'das_lms.group_das_instructor',
    'das_lms.group_das_soporte',
    'das_lms.module_category_das_roles',
)

_DAS_MENU_ACL_XMLIDS = (
    'das_lms.access_slide_channel_soporte',
    'das_lms.access_slide_slide_soporte',
    'das_lms.access_course_enrollment_soporte',
    'das_lms.access_sale_order_soporte',
    'das_lms.access_account_move_soporte',
    'das_lms.access_res_partner_soporte',
)


def _xmlids_to_group_ids(env, group_xmlids):
    group_ids = []
    for xmlid in group_xmlids:
        group = env.ref(xmlid, raise_if_not_found=False)
        if group:
            group_ids.append(group.id)
    return group_ids


def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    Menu = env['ir.ui.menu'].sudo()

    for menu_xmlid, group_xmlids in _MENU_STANDARD_GROUPS.items():
        menu = env.ref(menu_xmlid, raise_if_not_found=False)
        if not menu:
            continue
        group_ids = _xmlids_to_group_ids(env, group_xmlids)
        menu.write({'groups_id': [(6, 0, group_ids)]})

    for xmlid in _DAS_MENU_ACL_XMLIDS:
        access = env.ref(xmlid, raise_if_not_found=False)
        if access:
            access.unlink()

    for xmlid in _DAS_ROLE_GROUP_XMLIDS:
        record = env.ref(xmlid, raise_if_not_found=False)
        if record and record._name == 'res.groups':
            record.unlink()
        elif record and record._name == 'ir.module.category':
            record.unlink()

    _logger.info('das_lms post-migrate: menús restaurados a valores estándar Odoo 18.')
