# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class RetentionWizard(models.TransientModel):
    _name = "l10n_ec.retention.wizard"
    _description = "Wizard to Create Withholding Document"

    invoice_id = fields.Many2one("account.move", string="Invoice", required=True)
    partner_id = fields.Many2one(related="invoice_id.partner_id", string="Vendor")
    date = fields.Date(string="Date", default=fields.Date.context_today)

    line_ids = fields.One2many(
        "l10n_ec.retention.wizard.line", "wizard_id", string="Withholding Lines"
    )

    @api.model
    def default_get(self, fields_list):
        res = super(RetentionWizard, self).default_get(fields_list)
        if (
            "active_id" in self.env.context
            and self.env.context.get("active_model") == "account.move"
        ):
            invoice = self.env["account.move"].browse(self.env.context["active_id"])
            res["invoice_id"] = invoice.id

            lines = []
            # Auto-calculation logic
            # We look for Taxes on the Invoice Lines that are "Retentions"
            # Since we don't have strict Tax Group mapping in this scaffold yet,
            # we will create lines based on the invoice lines tax calculations if they appear to be retentions
            # OR, more robustly for a Wizard: We allow the user to select the code and we apply it to the base.

            # Strategy: Pre-fill base amounts from invoice totals to save typing
            # Separate by VAT and Income Tax bases if possible.

            # Simple approach: Create one line for Income Tax (Renta) and one for VAT (IVA) if applicable.
            # Base Imponible Renta = Amount Untaxed
            # Base Imponible IVA = Amount Tax (only if Retaining IVA)

            # 1. Renta Line Suggestion
            lines.append(
                (
                    0,
                    0,
                    {
                        "tax_type": "1",  # Renta
                        "base": invoice.amount_untaxed,
                        "percentage": 0.0,
                        "tax_code": "332",  # Default/Common code, user can change
                    },
                )
            )

            # 2. IVA Line Suggestion (if there is VAT)
            total_vat = sum(
                line.price_total - line.price_subtotal
                for line in invoice.invoice_line_ids
            )
            if total_vat > 0:
                lines.append(
                    (
                        0,
                        0,
                        {
                            "tax_type": "2",  # IVA
                            "base": total_vat,  # Base for IVA Retention is the VAT amount itself?
                            # No, usually percentage of VAT amount (10%, 30%, 70%, 100%)
                            # Or is base the invoice subtotal?
                            # Ficha Tecnica: baseImponible for code 2 (IVA) is the VAT AMOUNT.
                            # Review DM_02: "baseImponible" -> "Decimal 2 places".
                            # For IVA retention, the base is the IVA value.
                            # Let's confirm: "Retention of IVA is X% of the IVA Value."
                            "base": total_vat,
                            "percentage": 30.0,  # Common Goods %
                            "tax_code": "2",  # Common Code
                        },
                    )
                )

            res["line_ids"] = lines

        return res

    def action_create_retention(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_("Please add at least one withholding line."))

        retention_vals = {
            "invoice_id": self.invoice_id.id,
            "partner_id": self.partner_id.id,
            "date": self.date,
            "company_id": self.invoice_id.company_id.id,
            "l10n_ec_sri_status": "draft",
            "retention_line_ids": [],
        }

        for line in self.line_ids:
            retention_vals["retention_line_ids"].append(
                (
                    0,
                    0,
                    {
                        "tax_type": line.tax_type,
                        "tax_code": line.tax_code,
                        "base": line.base,
                        "percentage": line.percentage,
                        "amount": line.amount,
                    },
                )
            )

        retention = self.env["account.retention"].create(retention_vals)

        # Link back to invoice for smart button (if we add one) or just return view
        return {
            "name": _("Withholding"),
            "type": "ir.actions.act_window",
            "res_model": "account.retention",
            "res_id": retention.id,
            "view_mode": "form",
            "target": "current",
        }


class RetentionWizardLine(models.TransientModel):
    _name = "l10n_ec.retention.wizard.line"
    _description = "Retention Wizard Line"

    wizard_id = fields.Many2one("l10n_ec.retention.wizard", required=True)
    tax_type = fields.Selection(
        [("1", "Renta"), ("2", "IVA"), ("6", "ISD")], string="Impuesto", required=True
    )

    tax_code = fields.Char(string="Código Retención", required=True)
    base = fields.Monetary(string="Base Imponible", required=True)
    percentage = fields.Float(string="Porcentaje %", required=True)
    amount = fields.Monetary(string="Valor Retenido", compute="_compute_amount")
    currency_id = fields.Many2one(related="wizard_id.invoice_id.currency_id")

    @api.depends("base", "percentage")
    def _compute_amount(self):
        for line in self:
            line.amount = line.base * (line.percentage / 100.0)
