# -*- coding: utf-8 -*-
from odoo import models, _
from odoo.tools import html2plaintext
from collections import defaultdict
import base64
import logging

_logger = logging.getLogger(__name__)


class AccountEdiFormat(models.Model):
    _inherit = "account.edi.format"

    def _get_l10n_ec_fallback_payment_code(self, invoice):
        journal_type = invoice.journal_id.type
        if journal_type == "cash":
            return "01"
        return "20"

    def _get_l10n_ec_payment_code_from_method(self, payment_method):
        if (
            payment_method
            and "l10n_ec_sri_payment_id" in payment_method._fields
            and payment_method.l10n_ec_sri_payment_id
        ):
            return payment_method.l10n_ec_sri_payment_id.code
        return False

    def _get_l10n_ec_payment_code_from_payment(self, payment):
        if payment.payment_transaction_id:
            code = self._get_l10n_ec_payment_code_from_method(
                payment.payment_transaction_id.payment_method_id
            )
            if code:
                return code
        if payment.journal_id.type == "cash":
            return "01"
        if payment.journal_id.type == "bank":
            return "20"
        return False

    def _get_l10n_ec_payment_lines(self, invoice):
        """
        Return SRI payment lines for <pagos>.

        Priority:
        1. Explicit Ecuador SRI payment method on the invoice.
        2. eCommerce/payment transaction method mapping.
        3. Reconciled account payment/journal type.
        4. Conservative SRI fallback: 20 (financial system) or 01 for cash journals.
        """
        if (
            "l10n_ec_sri_payment_id" in invoice._fields
            and invoice.l10n_ec_sri_payment_id
            and invoice.l10n_ec_sri_payment_id.code
        ):
            return [{"code": invoice.l10n_ec_sri_payment_id.code, "amount": invoice.amount_total}]

        transactions = invoice.transaction_ids | invoice.authorized_transaction_ids
        transactions = transactions.filtered(lambda tx: tx.state in ("authorized", "done")) or transactions
        transaction_codes = transactions.mapped("payment_method_id.l10n_ec_sri_payment_id.code")
        transaction_codes = [code for code in transaction_codes if code]
        if transaction_codes:
            unique_codes = sorted(set(transaction_codes))
            if len(unique_codes) == 1:
                return [{"code": unique_codes[0], "amount": invoice.amount_total}]

        payment_codes = []
        for payment in invoice.reconciled_payment_ids | invoice.payment_ids:
            code = self._get_l10n_ec_payment_code_from_payment(payment)
            if code:
                payment_codes.append(code)
        if payment_codes:
            unique_codes = sorted(set(payment_codes))
            if len(unique_codes) == 1:
                return [{"code": unique_codes[0], "amount": invoice.amount_total}]

        return [
            {
                "code": self._get_l10n_ec_fallback_payment_code(invoice),
                "amount": invoice.amount_total,
            }
        ]

    def _get_l10n_ec_tax_percentage_code(self, tax):
        tax_name = str(tax.name or "")
        if tax.amount == 15 or "15%" in tax_name:
            return "4"
        if tax.amount == 0 or "0%" in tax_name:
            return "0"
        return "0"

    def _get_l10n_ec_identifier_code(self, partner):
        """
        Maps Partner Identifier type to SRI Table 07:
        RUC = 04, Cedula = 05, Pasaporte = 06, Consumidor Final = 07, Exterior = 08
        """
        # Get CF RUC from config (not hardcoded)
        cf_ruc = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("l10n_ec.consumidor_final_ruc", "9999999999999")
        )

        if partner.vat == cf_ruc:
            return "07"
        type_map = {"ruc": "04", "cedula": "05", "pasaporte": "06"}
        return type_map.get(partner.l10n_ec_identifier_type, "08")

    def _compute_tax_aggregates(self, invoice):
        """
        Groups taxes by SRI Table 16 (Codigo) and Table 17 (Porcentaje).
        Returns list of dicts for <totalImpuesto>.
        """
        tax_grouped = defaultdict(lambda: {"base": 0.0, "amount": 0.0})

        for line in invoice.invoice_line_ids:
            if line.display_type in ("line_section", "line_note"):
                continue
            if not line.tax_ids:
                if line.price_subtotal:
                    tax_grouped[("2", "0")]["base"] += line.price_subtotal
                    tax_grouped[("2", "0")]["amount"] += 0.0
                continue

            price_reduce = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

            # Compute taxes
            taxes_res = line.tax_ids.compute_all(
                price_reduce,
                quantity=line.quantity,
                product=line.product_id,
                partner=invoice.partner_id,
            )

            for tax_val in taxes_res["taxes"]:
                tax_obj = self.env["account.tax"].browse(tax_val["id"])

                # Logic to determine SRI Code/Percentage
                # Specialist Implementation: Infer from name if specific fields missing.
                sri_code = "2"  # IVA default
                sri_perc = "0"

                if "ICE" in str(tax_obj.name or ""):
                    sri_code = "3"
                    sri_perc = "3023"
                else:
                    sri_perc = self._get_l10n_ec_tax_percentage_code(tax_obj)

                key = (sri_code, sri_perc)
                tax_grouped[key]["base"] += tax_val["base"]
                tax_grouped[key]["amount"] += tax_val["amount"]

        results = []
        for (code, perc), vals in tax_grouped.items():
            results.append(
                {
                    "codigo": code,
                    "codigo_porcentaje": perc,
                    "base": vals["base"],
                    "amount": vals["amount"],
                }
            )
        return results

    def _get_l10n_ec_line_taxes(self, line):
        if not line.tax_ids:
            return [
                {
                    "codigo": "2",
                    "codigo_porcentaje": "0",
                    "tarifa": 0.0,
                    "base": line.price_subtotal,
                    "amount": 0.0,
                }
            ]

        price_reduce = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
        taxes_res = line.tax_ids.compute_all(
            price_reduce,
            quantity=line.quantity,
            product=line.product_id,
            partner=line.move_id.partner_id,
        )
        line_taxes = []
        for tax_val in taxes_res["taxes"]:
            tax_obj = self.env["account.tax"].browse(tax_val["id"])
            if "ICE" in str(tax_obj.name or ""):
                sri_code = "3"
                sri_perc = "3023"
            else:
                sri_code = "2"
                sri_perc = self._get_l10n_ec_tax_percentage_code(tax_obj)
            line_taxes.append(
                {
                    "codigo": sri_code,
                    "codigo_porcentaje": sri_perc,
                    "tarifa": tax_obj.amount,
                    "base": tax_val["base"],
                    "amount": tax_val["amount"],
                }
            )
        return line_taxes or [
            {
                "codigo": "2",
                "codigo_porcentaje": "0",
                "tarifa": 0.0,
                "base": line.price_subtotal,
                "amount": 0.0,
            }
        ]

    def _get_l10n_ec_edi_values(self, invoice):
        """
        Prepares the dictionary of values for the QWeb template.
        """
        total_discount = 0.0
        for line in invoice.invoice_line_ids:
            if line.discount:
                untaxed = line.price_unit * line.quantity
                discount_amt = untaxed * (line.discount / 100.0)
                total_discount += discount_amt

        vals = {
            "move": invoice,
            "company": invoice.company_id,
            "partner": invoice.partner_id,
            "environment": (
                "2" if invoice.company_id.l10n_ec_sri_environment == "production" else "1"
            ),
            "access_key": invoice.l10n_ec_sri_access_key,
            "format_monetary": lambda x: "%.2f" % x,
            "format_float": lambda x, p: ("%." + str(p) + "f") % x,
            "l10n_ec_identifier_code": self._get_l10n_ec_identifier_code(
                invoice.partner_id
            ),
            "vals": {
                "total_sin_impuestos": invoice.amount_untaxed,
                "total_descuento": total_discount,
                "taxes": self._compute_tax_aggregates(invoice),
                "line_taxes": {
                    line.id: self._get_l10n_ec_line_taxes(line)
                    for line in invoice.invoice_line_ids
                    if line.display_type not in ("line_section", "line_note")
                },
                "pagos": self._get_l10n_ec_payment_lines(invoice),
                "additional_info": [
                    info
                    for info in [
                        {
                            "name": "Email",
                            "value": (invoice.partner_id.email or "")[:300],
                        },
                        {
                            "name": "Notas",
                            "value": html2plaintext(invoice.narration or "").strip()[:300],
                        },
                    ]
                    if info["value"]
                ],
            },
            "tax_map": {
                tax.id: self._get_l10n_ec_tax_percentage_code(tax)
                for tax in invoice.invoice_line_ids.tax_ids
            },
        }
        return vals

    def _export_l10n_ec_edi(self, invoice):
        """
        Generates the XML content.
        """
        values = self._get_l10n_ec_edi_values(invoice)
        xml_content = self.env["ir.qweb"]._render(
            "l10n_ec_edi.l10n_ec_edi_factura", values
        )
        return xml_content

    def _post_invoice_edi(self, invoices):
        """
        Main entry point for EDI transmission.
        """
        ec_invoices = invoices.filtered(lambda i: i.company_id.country_id.code == "EC")
        if not ec_invoices:
            return super()._post_invoice_edi(invoices)

        res = {}
        for invoice in ec_invoices:
            if not invoice.l10n_ec_sri_access_key:
                invoice._generate_access_key()

            xml_content = self._export_l10n_ec_edi(invoice)

            # Check Active Certificate (New Model Link)
            certificate = invoice.company_id.l10n_ec_certificate_id
            if not certificate or certificate.state != "active":
                res[invoice] = {
                    "error": _("SRI Error: No active Signing Certificate configured.")
                }
                continue

            try:
                # Use AbstractModels from l10n_ec_edi
                signer = self.env["l10n_ec.sri.signer"]
                service = self.env["l10n_ec.sri.service"]

                # Sign
                # The signer expect bytes, xml_content is str
                signed_xml_bytes = signer.sign_xml(
                    xml_content.encode("utf-8"),
                    certificate.content,  # This is binary (base64)
                    certificate.password,
                )

                # Transmit
                env_code = (
                    "2" if invoice.company_id.l10n_ec_sri_environment == "production" else "1"
                )
                response_data = service.send_document(signed_xml_bytes, env_code)

                # Process Response
                if response_data.get("status") == "RECIBIDA":
                    invoice.l10n_ec_sri_status = "sent"
                    invoice.l10n_ec_sri_response = (
                        "RECIBIDA. Waiting for Authorization..."
                    )
                else:
                    invoice.l10n_ec_sri_status = "rejected"
                    msgs = "\n".join(response_data.get("messages", []))
                    invoice.l10n_ec_sri_response = (
                        f"{response_data.get('status')}: {msgs}"
                    )

                invoice.l10n_ec_xml_data = base64.b64encode(signed_xml_bytes)
                res[invoice] = {"success": True, "attachment": invoice.l10n_ec_xml_data}

            except Exception as e:
                _logger.error("EDI Logic Error: %s", str(e), exc_info=True)
                res[invoice] = {"error": _("SRI Transmission Error: %s") % str(e)}

        return res
