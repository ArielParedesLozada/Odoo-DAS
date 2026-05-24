# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class LmsSatisfactionSurvey(models.Model):
    _name = "lms.satisfaction.survey"
    _description = "LMS Satisfaction Survey Configuration"

    name = fields.Char(string="Reference Name", required=True)
    channel_id = fields.Many2one("slide.channel", string="Course", required=False)
    survey_id = fields.Many2one("survey.survey", string="Survey", required=False)
    responsible_id = fields.Many2one(
        "res.partner",
        string="Responsible",
        default=lambda self: self.env.user.partner_id,
    )
    active = fields.Boolean(default=True)
    auto_generated = fields.Boolean(
        string="Auto Generated", default=False, readonly=True
    )
    last_generated = fields.Datetime(string="Last Generated At", readonly=True)

    answers_count = fields.Integer(string="Answers", compute="_compute_answers_count")

    def _compute_answers_count(self):
        for rec in self:
            if rec.survey_id:
                rec.answers_count = self.env["survey.user_input"].search_count(
                    [("survey_id", "=", rec.survey_id.id), ("state", "=", "done")]
                )
            else:
                rec.answers_count = 0

    def action_view_results(self):
        self.ensure_one()
        if self.survey_id:
            return {
                "type": "ir.actions.act_url",
                "url": f"/survey/results/{self.survey_id.id}",
                "target": "new",
            }

    def action_generate_survey_and_slide(self):
        for rec in self:
            if not rec.channel_id:
                raise UserError(_("Seleccione un curso"))

            # Validación fuerte contra duplicados
            existing = self.env["slide.slide"].search(
                [
                    ("channel_id", "=", rec.channel_id.id),
                    ("das_is_satisfaction_survey", "=", True),
                ],
                limit=1,
            )

            if existing:
                raise UserError(
                    _("Ya existe una encuesta de satisfacción para este curso.")
                )

            # Llamar al flujo principal centralizado
            rec.channel_id.action_generate_certification_flow()

            rec.auto_generated = True
            rec.last_generated = fields.Datetime.now()

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Éxito"),
                "message": _("Flujo de certificación disparado exitosamente."),
                "type": "success",
                "sticky": False,
            },
        }
    