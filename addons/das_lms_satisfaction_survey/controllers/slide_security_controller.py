# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.website_slides.controllers.main import WebsiteSlides


class SlideSecurityController(WebsiteSlides):
    @http.route()
    def slide(self, slide, **kwargs):
        """
        HEREDA correctamente el controller original.
        'slide' ya viene como record gracias al slug de Odoo.
        """

        # 👇 IMPORTANTE: slide ya es record, NO browse manual
        if slide and not request.env.user._is_public():
            enrollment = (
                request.env["course.enrollment"]
                .sudo()
                .search(
                    [
                        ("course_id", "=", slide.channel_id.id),
                        ("student_id", "=", request.env.user.partner_id.id),
                    ],
                    limit=1,
                )
            )

            # 🔴 BLOQUEO ENCUESTA
            if slide.das_is_satisfaction_survey:
                if not enrollment or enrollment.das_lms_final_status == "pending":
                    return request.render(
                        "http_routing.403",
                        {
                            "error_message": _(
                                "Debes completar el examen final antes de acceder a la encuesta."
                            )
                        },
                    )

            # 🔴 BLOQUEO EXAMEN SIN INSCRIPCIÓN
            if slide.das_is_final_exam:
                if not enrollment:
                    return request.render(
                        "http_routing.403",
                        {"error_message": _("Debes estar inscrito en el curso.")},
                    )

        # ✅ LLAMADA REAL AL CORE
        return super().slide(slide, **kwargs)
