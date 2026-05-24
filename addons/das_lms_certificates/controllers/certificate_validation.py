# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError
import odoo.addons.survey.controllers.main as survey_main


class CertificateValidationController(http.Controller):
    @http.route(
        ["/validar/certificado/<string:token>"],
        type="http",
        auth="public",
        website=True,
    )
    def validate_certificate(self, token, **kwargs):
        enrollment = (
            request.env["course.enrollment"]
            .sudo()
            .search([("das_lms_certificate_token", "=", token)], limit=1)
        )

        if not enrollment:
            return request.render("das_lms_certificates.certificate_invalid_page", {})

        return request.render(
            "das_lms_certificates.certificate_valid_page",
            {
                "enrollment": enrollment,
            },
        )

    @http.route(
        ["/my/certificate/<int:channel_id>"], type="http", auth="user", website=True
    )
    def download_certificate(self, channel_id, **kwargs):
        enrollment = (
            request.env["course.enrollment"]
            .sudo()
            .search(
                [
                    ("course_id", "=", channel_id),
                    ("student_id", "=", request.env.user.partner_id.id),
                ],
                limit=1,
            )
        )

        # VALIDACIÓN COMPLETA
        if not enrollment:
            return request.redirect("/slides")

        if enrollment.das_lms_final_status == "pending":
            return request.render(
                "http_routing.403",
                {"error_message": _("Debes completar el examen final.")},
            )

        if not enrollment.das_lms_survey_completed:
            return request.render(
                "http_routing.403",
                {"error_message": _("Debes completar la encuesta de satisfacción.")},
            )

        pdf, _ = (
            request.env["ir.actions.report"]
            .sudo()
            ._render_qweb_pdf(
                "das_lms_certificates.action_report_course_certificate", [enrollment.id]
            )
        )

        return request.make_response(
            pdf,
            headers=[
                ("Content-Type", "application/pdf"),
                ("Content-Length", len(pdf)),
                (
                    "Content-Disposition",
                    f'attachment; filename="Certificado_{channel_id}.pdf"',
                ),
            ],
        )


class SurveyInherit(survey_main.Survey):
    @http.route(
        ["/survey/<int:survey_id>/get_certification"],
        type="http",
        auth="user",
        methods=["GET"],
        website=True,
    )
    def survey_get_certification(self, survey_id, **kwargs):
        survey = (
            request.env["survey.survey"]
            .sudo()
            .search([("id", "=", int(survey_id)), ("certification", "=", True)])
        )
        if not survey:
            return request.redirect("/")

        # Grab the latest attempt for this survey by the current user
        attempt = (
            request.env["survey.user_input"]
            .sudo()
            .search(
                [
                    ("partner_id", "=", request.env.user.partner_id.id),
                    ("survey_id", "=", int(survey_id)),
                    ("state", "=", "done"),
                ],
                order="create_date desc",
                limit=1,
            )
        )

        # Reliably find the slide associated with this survey
        slide = (
            request.env["slide.slide"]
            .sudo()
            .search([("survey_id", "=", int(survey_id))], limit=1)
        )
        # If we have an attempt and it's either our "Examen Final" or "Encuesta de Satisfacción" slide
        if (
            attempt
            and slide
            and (slide.das_is_final_exam or slide.das_is_satisfaction_survey)
        ):
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

            # Check if they have actually completed the final exam (status is not pending)
            if enrollment and enrollment.das_lms_final_status != "pending":
                # NUEVA LÓGICA: Validar si la encuesta de satisfacción fue completada
                if not enrollment.das_lms_survey_completed:
                    # Buscar el slide de la encuesta de satisfacción de este curso
                    sat_slide = (
                        request.env["slide.slide"]
                        .sudo()
                        .search(
                            [
                                ("channel_id", "=", slide.channel_id.id),
                                ("das_is_satisfaction_survey", "=", True),
                            ],
                            limit=1,
                        )
                    )

                    if sat_slide:
                        # Redirigir automáticamente al estudiante a la diapositiva de la encuesta
                        return request.redirect(f"/slides/slide/{sat_slide.id}")
                    else:
                        # Fallback en caso de que el curso no tenga configurada la encuesta
                        return request.render(
                            "http_routing.403",
                            {
                                "error_message": _(
                                    "Debe completar la Encuesta de Satisfacción antes de descargar el certificado."
                                )
                            },
                        )

                # Intercept! Generate OUR custom PDF
                pdf, _ = (
                    request.env["ir.actions.report"]
                    .sudo()
                    ._render_qweb_pdf(
                        "das_lms_certificates.action_report_course_certificate",
                        [enrollment.id],
                    )
                )
                pdfhttpheaders = [
                    ("Content-Type", "application/pdf"),
                    ("Content-Length", len(pdf)),
                    (
                        "Content-Disposition",
                        'attachment; filename="Certificado_%s.pdf"'
                        % enrollment.course_id.name,
                    ),
                ]
                return request.make_response(pdf, headers=pdfhttpheaders)

        # If it is NOT our Examen Final, let Odoo do its normal native thing
        return request.redirect("/slides")

    @http.route(
        ["/survey/submit/<string:survey_token>/<string:answer_token>"],
        type="json",
        auth="public",
        website=True,
    )
    def survey_submit(self, survey_token, answer_token, **post):
        res = super(SurveyInherit, self).survey_submit(
            survey_token, answer_token, **post
        )

        # Buscar el intento actual para ver si acaba de finalizar
        user_input = (
            request.env["survey.user_input"]
            .sudo()
            .search([("access_token", "=", answer_token)], limit=1)
        )
        if user_input and user_input.state == "done":
            # Verificar si este survey corresponde al Examen Final
            slide = (
                request.env["slide.slide"]
                .sudo()
                .search(
                    [
                        ("survey_id", "=", user_input.survey_id.id),
                        ("das_is_final_exam", "=", True),
                    ],
                    limit=1,
                )
            )
            if slide:
                # Buscar la encuesta de satisfacción
                sat_slide = (
                    request.env["slide.slide"]
                    .sudo()
                    .search(
                        [
                            ("channel_id", "=", slide.channel_id.id),
                            ("das_is_satisfaction_survey", "=", True),
                        ],
                        limit=1,
                    )
                )
                if sat_slide and isinstance(res, dict):
                    # Forzar la redirección a la encuesta de satisfacción
                    res["redirect"] = f"/slides/slide/{sat_slide.id}"

        return res

    @http.route(
        ["/survey/start/<string:survey_token>"],
        type="http",
        auth="public",
        website=True,
    )
    def survey_start(self, survey_token, answer_token=None, email=False, **post):
        survey = (
            request.env["survey.survey"]
            .sudo()
            .search([("access_token", "=", survey_token)], limit=1)
        )

        if survey:
            slide = (
                request.env["slide.slide"]
                .sudo()
                .search([("survey_id", "=", survey.id)], limit=1)
            )

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

                # 🔒 BLOQUEO ENCUESTA SIN EXAMEN
                if slide.das_is_satisfaction_survey:
                    if not enrollment or enrollment.das_lms_final_status == "pending":
                        return request.render(
                            "http_routing.403",
                            {
                                "error_message": _(
                                    "Acceso Denegado: Debes completar el examen final antes de acceder a la encuesta."
                                )
                            },
                        )
        # 🔥 ANTES de llamar al super
        if slide and slide.das_is_satisfaction_survey:
            old_attempts = (
                request.env["survey.user_input"]
                .sudo()
                .search(
                    [
                        ("survey_id", "=", survey.id),
                        ("partner_id", "=", request.env.user.partner_id.id),
                        ("state", "=", "done"),
                    ]
                )
            )

        # ✅ CRÍTICO: SIEMPRE retornar al core
        return super(SurveyInherit, self).survey_start(
            survey_token, answer_token=answer_token, email=email, **post
        )

    @http.route(
        ["/survey/results/<string:answer_token>"],
        type="http",
        auth="public",
        website=True,
    )
    def survey_results(self, answer_token, **kwargs):
        user_input = (
            request.env["survey.user_input"]
            .sudo()
            .search(
                [("access_token", "=", answer_token)],
                limit=1,
            )
        )

        if user_input:
            slide = (
                request.env["slide.slide"]
                .sudo()
                .search(
                    [
                        ("survey_id", "=", user_input.survey_id.id),
                        ("das_is_final_exam", "=", True),
                    ],
                    limit=1,
                )
            )

            if slide:
                sat_slide = (
                    request.env["slide.slide"]
                    .sudo()
                    .search(
                        [
                            ("channel_id", "=", slide.channel_id.id),
                            ("das_is_satisfaction_survey", "=", True),
                        ],
                        limit=1,
                    )
                )

                if sat_slide:
                    return request.redirect(f"/slides/slide/{sat_slide.id}")

        return super().survey_results(answer_token, **kwargs)
