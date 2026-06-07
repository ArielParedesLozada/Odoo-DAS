# -*- coding: utf-8 -*-
import werkzeug
from urllib.parse import urlparse

from odoo import http, tools, _
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_slides.controllers.main import WebsiteSlides, handle_wslide_error
from odoo.addons.website_sale_slides.controllers.slides import WebsiteSaleSlides
from odoo.http import request


def _das_lms_url_path_only(raw):
    """Quita dominio absoluto (p. ej. túnel caduco); misma idea que slide.channel._das_lms_public_course_href."""
    if not raw or raw == '#':
        return ''
    if raw.startswith(('http://', 'https://')):
        parsed = urlparse(raw)
        path = parsed.path or '/'
        if parsed.query:
            path = '%s?%s' % (path, parsed.query)
        return path
    return raw


class DasLmsWebsiteSlides(WebsiteSaleSlides):
    """Restringe eLearning en web para portal: solo cursos con slide.channel.partner activo."""

    def _das_lms_portal_can_open_lessons(self, channel):
        """Lecciones y contenidos: inscrito + calendario académico DAS (bloqueo antes del inicio)."""
        return request.env['slide.channel']._das_lms_portal_can_access_course_lessons(channel)

    def _das_lms_slide_access_error_message(self, channel):
        """Mensaje JSON cuando no se puede consumir una lección (no confundir bloqueo calendario con no inscripción)."""
        ch = channel.sudo()
        if self._das_lms_portal_can_study(channel) and ch.das_academic_status == 'proximo' and ch.das_start_date:
            ds = ch.das_start_date.strftime('%d/%m/%Y')
            return _('El curso aún no inicia. Podrás acceder al contenido desde el %s.') % ds
        return _('No estás inscrito en este curso.')

    def _das_lms_portal_response_lessons_calendar_locked(self, channel):
        """Miembro válido del curso pero el calendario DAS aún no permite abrir lecciones."""
        url = channel._das_lms_public_course_href()
        if url and url != '#':
            sep = '&' if '?' in url else '?'
            url = '%s%sdas_lms_lesson_pending=1' % (url, sep)
            return request.redirect(url, code=302)
        return request.render(
            'das_lms.portal_slide_course_lessons_locked',
            {
                'channel': channel,
                'main_object': channel,
            },
        )

    def _das_lms_portal_guard_lesson_http(self, channel):
        """Si el portal no puede abrir lecciones, devuelve respuesta HTTP adecuada; si puede, None."""
        if not self._das_lms_restrict_portal_elearning() or not channel:
            return None
        if self._das_lms_portal_can_open_lessons(channel):
            return None
        if self._das_lms_portal_can_study(channel):
            return self._das_lms_portal_response_lessons_calendar_locked(channel)
        return self._das_lms_portal_course_access_response(channel)

    def _das_lms_portal_guard_lesson_binary(self, channel):
        """PDF/imagen: mismo criterio que HTTP; sin miembro → 403."""
        if not self._das_lms_restrict_portal_elearning() or not channel:
            return None
        if self._das_lms_portal_can_open_lessons(channel):
            return None
        if self._das_lms_portal_can_study(channel):
            return self._das_lms_portal_response_lessons_calendar_locked(channel)
        return werkzeug.exceptions.Forbidden()

    def _das_lms_restrict_portal_elearning(self):
        user = request.env.user
        if user._is_public():
            return False
        if not user.share:
            return False
        if user.has_group('website_slides.group_website_slides_officer') or user.has_group(
            'website_slides.group_website_slides_manager'
        ):
            return False
        return True

    def _das_lms_portal_course_access_response(self, channel):
        channel_sudo = channel.sudo()
        product = channel_sudo.product_id
        if product and product.website_published:
            url = _das_lms_url_path_only(product.website_url)
            if url:
                return request.redirect(url, code=302)
        return request.render(
            'das_lms.portal_slide_channel_access_denied',
            {
                'channel': channel,
                'main_object': channel,
                'das_lms_registration_notice': channel_sudo._das_lms_registration_notice_message(),
                'das_lms_registration_notice_kind': channel_sudo._das_lms_registration_notice_kind(),
            },
        )

    def _das_lms_portal_can_study(self, channel):
        return request.env['slide.channel']._das_lms_portal_can_study_channel(channel)

    def slides_channel_all_values(self, slide_category=None, slug_tags=None, my=False, **post):
        render_values = super().slides_channel_all_values(
            slide_category=slide_category, slug_tags=slug_tags, my=my, **post,
        )
        if my:
            return render_values
        channels = render_values.get('channels')
        if not channels:
            return render_values
        partner = request.env.user.partner_id if not request.env.user._is_public() else None
        visible = channels.filtered(
            lambda c: c._das_lms_is_public_catalog_visible(partner=partner),
        )
        render_values['channels'] = visible
        render_values['search_count'] = len(visible)
        return render_values

    @http.route('/slides', type='http', auth='public', website=True, sitemap=True, readonly=True)
    def slides_channel_home(self, **post):
        if not self._das_lms_restrict_portal_elearning():
            return super().slides_channel_home(**post)

        channels_all = tools.lazy(
            lambda: request.env['slide.channel'].search(request.website.website_domain())
        )
        channels_my = tools.lazy(
            lambda: channels_all.filtered(lambda c: c.is_member).sorted(
                lambda c: 0 if c.completed else c.completion, reverse=True
            )
        )
        # Una sola sección en la home: no duplicar populares / novedades (misma lista que "Mis cursos").
        channels_popular = tools.lazy(lambda: request.env['slide.channel'].browse())
        channels_newest = tools.lazy(lambda: request.env['slide.channel'].browse())

        achievements = tools.lazy(
            lambda: request.env['gamification.badge.user']
            .sudo()
            .search([('badge_id.is_published', '=', True)], limit=5)
        )
        challenges = tools.lazy(
            lambda: request.env['gamification.challenge']
            .sudo()
            .search(
                [
                    ('challenge_category', '=', 'slides'),
                    ('reward_id.is_published', '=', True),
                ],
                order='id asc',
                limit=5,
            )
        )
        challenges_done = tools.lazy(
            lambda: request.env['gamification.badge.user']
            .sudo()
            .search(
                [
                    ('challenge_id', 'in', challenges.ids),
                    ('user_id', '=', request.env.user.id),
                    ('badge_id.is_published', '=', True),
                ]
            ).mapped('challenge_id')
        )

        users = tools.lazy(
            lambda: request.env['res.users']
            .sudo()
            .search(
                [('karma', '>', 0), ('website_published', '=', True)],
                limit=5,
                order='karma desc',
            )
        )

        render_values = self._slide_render_context_base()
        render_values.update(self._prepare_user_values(**post))
        render_values.update(
            {
                'das_lms_slides_portal_home': True,
                'channels_my': channels_my,
                'channels_popular': channels_popular,
                'channels_newest': channels_newest,
                'achievements': achievements,
                'users': users,
                'top3_users': tools.lazy(self._get_top3_users),
                'challenges': challenges,
                'challenges_done': challenges_done,
                'search_tags': request.env['slide.channel.tag'],
                'slide_query_url': QueryURL('/slides/all', ['tag']),
                'slugify_tags': self._slugify_tags,
            }
        )
        return request.render('website_slides.courses_home', render_values)

    @http.route(
        ['/slides/all', '/slides/all/tag/<string:slug_tags>'],
        type='http',
        auth='public',
        website=True,
        sitemap=True,
        readonly=True,
    )
    def slides_channel_all(self, slide_category=None, slug_tags=None, my=False, **post):
        if self._das_lms_restrict_portal_elearning():
            my = True
        return super().slides_channel_all(
            slide_category=slide_category, slug_tags=slug_tags, my=my, **post
        )

    @http.route(
        [
            '/slides/<int:channel_id>',
            '/slides/<int:channel_id>/category/<int:category_id>',
            '/slides/<int:channel_id>/category/<int:category_id>/page/<int:page>',
            '/slides/<model("slide.channel"):channel>',
            '/slides/<model("slide.channel"):channel>/page/<int:page>',
            '/slides/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>',
            '/slides/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>/page/<int:page>',
            '/slides/<model("slide.channel"):channel>/category/<model("slide.slide"):category>',
            '/slides/<model("slide.channel"):channel>/category/<model("slide.slide"):category>/page/<int:page>',
        ],
        type='http',
        auth='public',
        website=True,
        sitemap=WebsiteSlides.sitemap_slide,
        handle_params_access_error=handle_wslide_error,
        readonly=True,
    )
    def channel(
        self,
        channel=False,
        channel_id=False,
        category=None,
        category_id=False,
        tag=None,
        page=1,
        slide_category=None,
        uncategorized=False,
        sorting=None,
        search=None,
        **kw,
    ):
        ch = channel
        if not ch and channel_id:
            cid = channel_id
            if cid < 0:
                cid = abs(cid)
            ch = request.env['slide.channel'].browse(cid).exists()
        if ch:
            partner = request.env.user.partner_id if not request.env.user._is_public() else None
            ch_sudo = ch.sudo()
            if not ch_sudo._das_lms_is_public_catalog_visible(partner=partner):
                return self._das_lms_portal_course_access_response(ch_sudo)
        if self._das_lms_restrict_portal_elearning():
            if ch and ch.has_access('read') and not self._das_lms_portal_can_study(ch):
                return self._das_lms_portal_course_access_response(ch)
        return super().channel(
            channel=channel,
            channel_id=channel_id,
            category=category,
            category_id=category_id,
            tag=tag,
            page=page,
            slide_category=slide_category,
            uncategorized=uncategorized,
            sorting=sorting,
            search=search,
            **kw,
        )

    @http.route(
        '/slides/slide/<model("slide.slide"):slide>',
        type='http',
        auth='public',
        website=True,
        sitemap=True,
        handle_params_access_error=handle_wslide_error,
    )
    def slide_view(self, slide, **kwargs):
        resp = self._das_lms_portal_guard_lesson_http(slide.channel_id)
        if resp is not None:
            return resp
        return super().slide_view(slide, **kwargs)

    @http.route(
        '/slides/slide/<model("slide.slide"):slide>/pdf_content',
        type='http',
        auth='public',
        website=True,
        sitemap=False,
        handle_params_access_error=handle_wslide_error,
    )
    def slide_get_pdf_content(self, slide):
        resp = self._das_lms_portal_guard_lesson_binary(slide.channel_id)
        if resp is not None:
            return resp
        return super().slide_get_pdf_content(slide)

    @http.route('/slides/slide/<int:slide_id>/share', type='http', auth='public', website=True, sitemap=False)
    def slide_shared_view(self, slide_id, **kwargs):
        if self._das_lms_restrict_portal_elearning():
            slide = request.env['slide.slide'].sudo().browse(int(slide_id)).exists()
            resp = self._das_lms_portal_guard_lesson_http(slide.channel_id)
            if resp is not None:
                return resp
        return super().slide_shared_view(slide_id, **kwargs)

    @http.route('/slides/slide/<int:slide_id>/get_image', type='http', auth='public', website=True, sitemap=False)
    def slide_get_image(self, slide_id, field='image_128', width=0, height=0, crop=False):
        if self._das_lms_restrict_portal_elearning():
            slide = request.env['slide.slide'].search([('id', '=', int(slide_id))], limit=1)
            resp = self._das_lms_portal_guard_lesson_binary(slide.channel_id)
            if resp is not None:
                return resp
        return super().slide_get_image(slide_id, field=field, width=width, height=height, crop=crop)

    @http.route('/slides/slide/get_html_content', type='json', auth='public', website=True)
    def get_html_content(self, slide_id):
        if self._das_lms_restrict_portal_elearning():
            slide = request.env['slide.slide'].browse(int(slide_id)).exists()
            if slide and slide.channel_id and not self._das_lms_portal_can_open_lessons(slide.channel_id):
                return {
                    'error': 'slide_access',
                    'error_message': self._das_lms_slide_access_error_message(slide.channel_id),
                }
        return super().get_html_content(slide_id)

    @http.route(
        '/slides/slide/<model("slide.slide"):slide>/set_completed',
        website=True,
        type='http',
        auth='user',
        handle_params_access_error=handle_wslide_error,
    )
    def slide_set_completed_and_redirect(self, slide, next_slide_id=None):
        resp = self._das_lms_portal_guard_lesson_http(slide.channel_id)
        if resp is not None:
            return resp
        return super().slide_set_completed_and_redirect(slide, next_slide_id=next_slide_id)

    @http.route('/slides/slide/set_completed', website=True, type='json', auth='public')
    def slide_set_completed(self, slide_id):
        if self._das_lms_restrict_portal_elearning():
            slide = request.env['slide.slide'].browse(int(slide_id)).exists()
            if slide and slide.channel_id and not self._das_lms_portal_can_open_lessons(slide.channel_id):
                return {
                    'error': 'slide_access',
                    'error_message': self._das_lms_slide_access_error_message(slide.channel_id),
                }
        return super().slide_set_completed(slide_id)

    @http.route(
        '/slides/slide/<model("slide.slide"):slide>/set_uncompleted',
        website=True,
        type='http',
        auth='user',
        handle_params_access_error=handle_wslide_error,
    )
    def slide_set_uncompleted_and_redirect(self, slide):
        resp = self._das_lms_portal_guard_lesson_http(slide.channel_id)
        if resp is not None:
            return resp
        return super().slide_set_uncompleted_and_redirect(slide)

    @http.route('/slides/slide/set_uncompleted', website=True, type='json', auth='public')
    def slide_set_uncompleted(self, slide_id):
        if self._das_lms_restrict_portal_elearning():
            slide = request.env['slide.slide'].browse(int(slide_id)).exists()
            if slide and slide.channel_id and not self._das_lms_portal_can_open_lessons(slide.channel_id):
                return {
                    'error': 'slide_access',
                    'error_message': self._das_lms_slide_access_error_message(slide.channel_id),
                }
        return super().slide_set_uncompleted(slide_id)

    @http.route('/slides/slide/quiz/get', type='json', auth='public', website=True)
    def slide_quiz_get(self, slide_id):
        if self._das_lms_restrict_portal_elearning():
            fetch_res = self._fetch_slide(slide_id)
            slide = fetch_res.get('slide')
            if slide and slide.channel_id and not self._das_lms_portal_can_open_lessons(slide.channel_id):
                return {
                    'error': 'slide_access',
                    'error_message': self._das_lms_slide_access_error_message(slide.channel_id),
                }
        return super().slide_quiz_get(slide_id)

    @http.route('/slides/slide/quiz/reset', type='json', auth='user', website=True)
    def slide_quiz_reset(self, slide_id):
        if self._das_lms_restrict_portal_elearning():
            fetch_res = self._fetch_slide(slide_id)
            slide = fetch_res.get('slide')
            if slide and slide.channel_id and not self._das_lms_portal_can_open_lessons(slide.channel_id):
                return {
                    'error': 'slide_access',
                    'error_message': self._das_lms_slide_access_error_message(slide.channel_id),
                }
        return super().slide_quiz_reset(slide_id)

    @http.route('/slides/slide/quiz/submit', type='json', auth='public', website=True)
    def slide_quiz_submit(self, slide_id, answer_ids):
        if self._das_lms_restrict_portal_elearning():
            fetch_res = self._fetch_slide(slide_id)
            slide = fetch_res.get('slide')
            if slide and slide.channel_id and not self._das_lms_portal_can_open_lessons(slide.channel_id):
                return {
                    'error': 'slide_access',
                    'error_message': self._das_lms_slide_access_error_message(slide.channel_id),
                }
        return super().slide_quiz_submit(slide_id, answer_ids)

    @http.route('/slides/embed/<int:slide_id>', type='http', auth='public', website=True, sitemap=False)
    def slides_embed(self, slide_id, page='1', **kw):
        if self._das_lms_restrict_portal_elearning():
            slide = request.env['slide.slide'].browse(int(slide_id)).exists()
            if slide and slide.channel_id and not self._das_lms_portal_can_open_lessons(slide.channel_id):
                return request.render('website_slides.embed_slide_forbidden', {})
        return super().slides_embed(slide_id, page=page, **kw)

    @http.route('/slides/embed_external/<int:slide_id>', type='http', auth='public', website=True, sitemap=False)
    def slides_embed_external(self, slide_id, page='1', **kw):
        if self._das_lms_restrict_portal_elearning():
            slide = request.env['slide.slide'].browse(int(slide_id)).exists()
            if slide and slide.channel_id and not self._das_lms_portal_can_open_lessons(slide.channel_id):
                return request.render('website_slides.embed_slide_forbidden', {})
        return super().slides_embed_external(slide_id, page=page, **kw)

