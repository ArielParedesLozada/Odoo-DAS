# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# Palabras clave en nombre del curso → xmlid de interés DAS.
_NAME_INTEREST_HINTS = (
    ('desarrollo', 'das_email_preferences.das_email_interest_development'),
    ('programación', 'das_email_preferences.das_email_interest_development'),
    ('software', 'das_email_preferences.das_email_interest_quality'),
    ('calidad', 'das_email_preferences.das_email_interest_quality'),
    ('marketing', 'das_email_preferences.das_email_interest_marketing'),
    ('diseño', 'das_email_preferences.das_email_interest_design'),
    ('tecnolog', 'das_email_preferences.das_email_interest_technology'),
)

# Modalidad DAS → categoría de marketing por defecto.
_MODALITY_CATEGORY = {
    'grabado': 'das_email_preferences.das_email_course_category_lms',
    'en_vivo': 'das_email_preferences.das_email_course_category_workshops',
    'mixto': 'das_email_preferences.das_email_course_category_lms',
}

# Palabras clave → nivel de experiencia sugerido para el curso.
_NAME_LEVEL_HINTS = (
    ('básico', 'beginner'),
    ('basico', 'beginner'),
    ('introducción', 'beginner'),
    ('introduccion', 'beginner'),
    ('fundamentos', 'beginner'),
    ('principiante', 'beginner'),
    ('intermedio', 'intermediate'),
    ('avanzado', 'advanced'),
    ('experto', 'expert'),
    ('master', 'expert'),
    ('especialización', 'expert'),
    ('especializacion', 'expert'),
)


class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    das_email_category_ids = fields.Many2many(
        'das.email.course.category',
        'slide_channel_das_email_category_rel',
        'channel_id',
        'category_id',
        string='Categorías Email Marketing',
        help='Usuarios con esta categoría en sus preferencias recibirán campañas del curso.',
    )
    das_email_interest_ids = fields.Many2many(
        'das.email.interest',
        'slide_channel_das_email_interest_rel',
        'channel_id',
        'interest_id',
        string='Intereses Email Marketing',
        help='Usuarios con estos intereses recibirán campañas del curso.',
    )
    das_experience_level = fields.Selection(
        [
            ('beginner', 'Básico'),
            ('intermediate', 'Intermedio'),
            ('advanced', 'Avanzado'),
            ('expert', 'Experto'),
        ],
        string='Nivel del curso (Email)',
        help='Usado para recomendaciones por nivel de experiencia del usuario.',
    )
    das_email_published_date = fields.Date(
        string='Fecha publicación (marketing)',
        help='Fecha en que el curso quedó publicado para campañas de cursos nuevos.',
    )
    das_email_marketing_configured = fields.Boolean(
        string='Marketing configurado',
        compute='_compute_das_email_marketing_configured',
        store=True,
    )

    @api.depends('das_email_category_ids', 'das_email_interest_ids')
    def _compute_das_email_marketing_configured(self):
        for channel in self:
            channel.das_email_marketing_configured = bool(
                channel.das_email_category_ids or channel.das_email_interest_ids
            )

    def _das_detect_experience_level(self):
        name_lower = (self.name or '').lower()
        for keyword, level in _NAME_LEVEL_HINTS:
            if keyword in name_lower:
                return level
        return False

    def _das_effective_published_date(self):
        """Fecha de referencia para campaña de curso nuevo."""
        self.ensure_one()
        if self.das_email_published_date:
            return self.das_email_published_date
        if self.create_date:
            return self.create_date.date()
        return False

    def _das_is_new_since(self, since_date):
        self.ensure_one()
        ref = self._das_effective_published_date()
        return bool(ref and ref >= since_date)

    def _das_stamp_email_published_date(self):
        today = fields.Date.context_today(self)
        to_stamp = self.filtered(lambda c: c.website_published and not c.das_email_published_date)
        if to_stamp:
            to_stamp.write({'das_email_published_date': today})

    def _das_apply_default_email_marketing(self):
        """Asigna intereses, categorías y nivel por defecto en cursos publicados."""
        default_interest = self.env.ref(
            'das_email_preferences.das_email_interest_technology',
            raise_if_not_found=False,
        )
        default_category = self.env.ref(
            'das_email_preferences.das_email_course_category_lms',
            raise_if_not_found=False,
        )
        for channel in self:
            name_lower = (channel.name or '').lower()
            vals = {}

            interest_ids = set(channel.das_email_interest_ids.ids)
            for keyword, xml_id in _NAME_INTEREST_HINTS:
                if keyword in name_lower:
                    interest = self.env.ref(xml_id, raise_if_not_found=False)
                    if interest:
                        interest_ids.add(interest.id)
            if not interest_ids and default_interest:
                interest_ids.add(default_interest.id)
            if not channel.das_email_interest_ids and interest_ids:
                vals['das_email_interest_ids'] = [(6, 0, list(interest_ids))]

            category_ids = set(channel.das_email_category_ids.ids)
            if channel.das_modality and channel.das_modality in _MODALITY_CATEGORY:
                cat = self.env.ref(
                    _MODALITY_CATEGORY[channel.das_modality],
                    raise_if_not_found=False,
                )
                if cat:
                    category_ids.add(cat.id)
            if not category_ids and default_category:
                category_ids.add(default_category.id)
            if not channel.das_email_category_ids and category_ids:
                vals['das_email_category_ids'] = [(6, 0, list(category_ids))]

            if not channel.das_experience_level:
                level = channel._das_detect_experience_level()
                if level:
                    vals['das_experience_level'] = level

            if vals:
                channel.write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        today = fields.Date.context_today(self)
        for vals in vals_list:
            if vals.get('website_published') and not vals.get('das_email_published_date'):
                vals.setdefault('das_email_published_date', today)
        channels = super().create(vals_list)
        published = channels.filtered('website_published')
        if published:
            published._das_stamp_email_published_date()
            published._das_apply_default_email_marketing()
        return channels

    def write(self, vals):
        if vals.get('website_published'):
            for channel in self:
                if not channel.das_email_published_date:
                    channel.das_email_published_date = fields.Date.context_today(self)
        res = super().write(vals)
        if vals.get('website_published') or 'name' in vals or 'das_modality' in vals:
            self.filtered('website_published')._das_apply_default_email_marketing()
        return res

    @api.model
    def _das_configure_published_channels_email_marketing(self):
        """Post-instalación: configura cursos publicados sin segmentación de marketing."""
        channels = self.search([('website_published', '=', True)])
        channels._das_stamp_email_published_date()
        need_config = channels.filtered(
            lambda c: not c.das_email_category_ids or not c.das_email_interest_ids
        )
        need_config._das_apply_default_email_marketing()
        _logger.info(
            'DAS campaigns: segmentación email aplicada a %s curso(s) publicado(s).',
            len(channels),
        )
