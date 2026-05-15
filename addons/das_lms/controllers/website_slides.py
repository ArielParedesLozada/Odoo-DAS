# -*- coding: utf-8 -*-
import werkzeug

from odoo import http, tools, _
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_slides.controllers.main import WebsiteSlides, handle_wslide_error
from odoo.addons.website_sale_slides.controllers.slides import WebsiteSaleSlides
from odoo.http import request


class DasLmsWebsiteSlides(WebsiteSaleSlides):
    """Restringe eLearning en web para portal: solo cursos con slide.channel.partner activo."""

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
            url = product.website_url
            if url:
                return request.redirect(url, code=302)
        return request.render(
            'das_lms.portal_slide_channel_access_denied',
            {
                'channel': channel,
                'main_object': channel,
            },
        )

    def _das_lms_portal_can_study(self, channel):
        return request.env['slide.channel']._das_lms_portal_can_study_channel(channel)

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
        if self._das_lms_restrict_portal_elearning():
            ch = channel
            if not ch and channel_id:
                cid = channel_id
                if cid < 0:
                    cid = abs(cid)
                ch = request.env['slide.channel'].browse(cid).exists()
            if ch:
                if ch.has_access('read') and not self._das_lms_portal_can_study(ch):
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
        if (
            self._das_lms_restrict_portal_elearning()
            and slide.channel_id
            and not self._das_lms_portal_can_study(slide.channel_id)
        ):
            return self._das_lms_portal_course_access_response(slide.channel_id)
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
        if (
            self._das_lms_restrict_portal_elearning()
            and slide.channel_id
            and not self._das_lms_portal_can_study(slide.channel_id)
        ):
            return werkzeug.exceptions.Forbidden()
        return super().slide_get_pdf_content(slide)

    @http.route('/slides/slide/<int:slide_id>/share', type='http', auth='public', website=True, sitemap=False)
    def slide_shared_view(self, slide_id, **kwargs):
        if self._das_lms_restrict_portal_elearning():
            slide = request.env['slide.slide'].sudo().browse(int(slide_id)).exists()
            if slide.channel_id and not self._das_lms_portal_can_study(slide.channel_id):
                return self._das_lms_portal_course_access_response(slide.channel_id)
        return super().slide_shared_view(slide_id, **kwargs)

    @http.route('/slides/slide/<int:slide_id>/get_image', type='http', auth='public', website=True, sitemap=False)
    def slide_get_image(self, slide_id, field='image_128', width=0, height=0, crop=False):
        if self._das_lms_restrict_portal_elearning():
            slide = request.env['slide.slide'].search([('id', '=', int(slide_id))], limit=1)
            if slide and slide.channel_id and not self._das_lms_portal_can_study(slide.channel_id):
                return werkzeug.exceptions.Forbidden()
        return super().slide_get_image(slide_id, field=field, width=width, height=height, crop=crop)

    @http.route('/slides/slide/get_html_content', type='json', auth='public', website=True)
    def get_html_content(self, slide_id):
        if self._das_lms_restrict_portal_elearning():
            slide = request.env['slide.slide'].browse(int(slide_id)).exists()
            if slide and slide.channel_id and not self._das_lms_portal_can_study(slide.channel_id):
                return {'error': 'slide_access', 'error_message': _('No estás inscrito en este curso.')}
        return super().get_html_content(slide_id)

    @http.route(
        '/slides/slide/<model("slide.slide"):slide>/set_completed',
        website=True,
        type='http',
        auth='user',
        handle_params_access_error=handle_wslide_error,
    )
    def slide_set_completed_and_redirect(self, slide, next_slide_id=None):
        if (
            self._das_lms_restrict_portal_elearning()
            and slide.channel_id
            and not self._das_lms_portal_can_study(slide.channel_id)
        ):
            return self._das_lms_portal_course_access_response(slide.channel_id)
        return super().slide_set_completed_and_redirect(slide, next_slide_id=next_slide_id)

    @http.route('/slides/slide/set_completed', website=True, type='json', auth='public')
    def slide_set_completed(self, slide_id):
        if self._das_lms_restrict_portal_elearning():
            slide = request.env['slide.slide'].browse(int(slide_id)).exists()
            if slide and slide.channel_id and not self._das_lms_portal_can_study(slide.channel_id):
                return {'error': 'slide_access', 'error_message': _('No estás inscrito en este curso.')}
        return super().slide_set_completed(slide_id)

    @http.route(
        '/slides/slide/<model("slide.slide"):slide>/set_uncompleted',
        website=True,
        type='http',
        auth='user',
        handle_params_access_error=handle_wslide_error,
    )
    def slide_set_uncompleted_and_redirect(self, slide):
        if (
            self._das_lms_restrict_portal_elearning()
            and slide.channel_id
            and not self._das_lms_portal_can_study(slide.channel_id)
        ):
            return self._das_lms_portal_course_access_response(slide.channel_id)
        return super().slide_set_uncompleted_and_redirect(slide)

    @http.route('/slides/slide/set_uncompleted', website=True, type='json', auth='public')
    def slide_set_uncompleted(self, slide_id):
        if self._das_lms_restrict_portal_elearning():
            slide = request.env['slide.slide'].browse(int(slide_id)).exists()
            if slide and slide.channel_id and not self._das_lms_portal_can_study(slide.channel_id):
                return {'error': 'slide_access', 'error_message': _('No estás inscrito en este curso.')}
        return super().slide_set_uncompleted(slide_id)

    @http.route('/slides/slide/quiz/get', type='json', auth='public', website=True)
    def slide_quiz_get(self, slide_id):
        if self._das_lms_restrict_portal_elearning():
            fetch_res = self._fetch_slide(slide_id)
            slide = fetch_res.get('slide')
            if slide and slide.channel_id and not self._das_lms_portal_can_study(slide.channel_id):
                return {'error': 'slide_access', 'error_message': _('No estás inscrito en este curso.')}
        return super().slide_quiz_get(slide_id)

    @http.route('/slides/slide/quiz/reset', type='json', auth='user', website=True)
    def slide_quiz_reset(self, slide_id):
        if self._das_lms_restrict_portal_elearning():
            fetch_res = self._fetch_slide(slide_id)
            slide = fetch_res.get('slide')
            if slide and slide.channel_id and not self._das_lms_portal_can_study(slide.channel_id):
                return {'error': 'slide_access', 'error_message': _('No estás inscrito en este curso.')}
        return super().slide_quiz_reset(slide_id)

    @http.route('/slides/slide/quiz/submit', type='json', auth='public', website=True)
    def slide_quiz_submit(self, slide_id, answer_ids):
        if self._das_lms_restrict_portal_elearning():
            fetch_res = self._fetch_slide(slide_id)
            slide = fetch_res.get('slide')
            if slide and slide.channel_id and not self._das_lms_portal_can_study(slide.channel_id):
                return {'error': 'slide_access', 'error_message': _('No estás inscrito en este curso.')}
        return super().slide_quiz_submit(slide_id, answer_ids)

    @http.route('/slides/embed/<int:slide_id>', type='http', auth='public', website=True, sitemap=False)
    def slides_embed(self, slide_id, page='1', **kw):
        if self._das_lms_restrict_portal_elearning():
            slide = request.env['slide.slide'].browse(int(slide_id)).exists()
            if slide and slide.channel_id and not self._das_lms_portal_can_study(slide.channel_id):
                return request.render('website_slides.embed_slide_forbidden', {})
        return super().slides_embed(slide_id, page=page, **kw)

    @http.route('/slides/embed_external/<int:slide_id>', type='http', auth='public', website=True, sitemap=False)
    def slides_embed_external(self, slide_id, page='1', **kw):
        if self._das_lms_restrict_portal_elearning():
            slide = request.env['slide.slide'].browse(int(slide_id)).exists()
            if slide and slide.channel_id and not self._das_lms_portal_can_study(slide.channel_id):
                return request.render('website_slides.embed_slide_forbidden', {})
        return super().slides_embed_external(slide_id, page=page, **kw)

