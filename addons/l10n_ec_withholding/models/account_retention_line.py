# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountRetentionLine(models.Model):
    _name = "account.retention.line"
    _description = "Detalle de Retención"

    retention_id = fields.Many2one(
        "account.retention",
        string="Retention",
        required=True,
        ondelete="cascade",
        index=True,
    )
    currency_id = fields.Many2one(related="retention_id.currency_id")

    # Tax Information
    tax_type = fields.Selection(
        [("1", "Renta"), ("2", "IVA"), ("6", "ISD")], string="Impuesto", required=True
    )

    tax_id = fields.Many2one(
        "l10n_ec.withholding.tax",
        string="Tax Code",
        required=True,
        domain="[('type', '=', tax_type)]",
    )

    # Related fields for ease of use/display
    tax_code = fields.Char(
        related="tax_id.code", string="Código", store=True, readonly=True
    )
    percentage = fields.Float(
        related="tax_id.percentage", string="Porcentaje %", store=True, readonly=True
    )

    base = fields.Monetary(string="Base Imponible", required=True)
    amount = fields.Monetary(
        string="Valor Retenido", required=True, compute="_compute_amount", store=True
    )

    # Document Sustento (if multi-invoice retention allowed, usually 1-to-1 but data structure supports N)
    invoice_id = fields.Many2one("account.move", string="Invoice Reference")

    @api.depends("base", "percentage")
    def _compute_amount(self):
        for line in self:
            line.amount = line.base * (line.percentage / 100.0)
