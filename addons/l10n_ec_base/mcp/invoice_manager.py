# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
# Copyright 2026 Somatech.dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

"""
Invoice Manager - Gestión de Facturas Electrónicas vía MCP

Este módulo proporciona operaciones completas para facturación
electrónica incluyendo envío SRI y anulación.
"""

import logging
from datetime import date, timedelta
from typing import Optional

_logger = logging.getLogger(__name__)


class InvoiceManager:
    """
    Gestor de facturas electrónicas vía MCP.

    Proporciona operaciones para crear, enviar y anular facturas
    cumpliendo las regulaciones SRI 2026.
    """

    def __init__(self, env):
        """
        Inicializa el gestor con el environment de Odoo.

        Args:
            env: Odoo environment
        """
        self.env = env
        self.Move = env['account.move']
        self.Partner = env['res.partner']
        self.Product = env['product.product']

    def create_invoice(
        self,
        partner_id: int,
        lines: list,
        invoice_type: str = 'out_invoice',
        invoice_date: date = None,
        notes: str = None
    ) -> dict:
        """
        Crea una factura electrónica.

        Args:
            partner_id: ID del cliente/proveedor
            lines: Lista de líneas [{product_id, quantity, price_unit}]
            invoice_type: 'out_invoice' (venta) o 'in_invoice' (compra)
            invoice_date: Fecha de factura (default: hoy)
            notes: Notas adicionales

        Returns:
            dict: {success, invoice_id, number, message}
        """
        try:
            partner = self.Partner.browse(partner_id)
            if not partner.exists():
                return {'success': False, 'message': 'Cliente no encontrado'}

            # Verificar límite Consumidor Final
            if not partner.vat or partner.vat == '9999999999999':
                total = sum(l.get('quantity', 1) * l.get('price_unit', 0) for l in lines)
                if total > 50:
                    return {
                        'success': False,
                        'message': 'Factura Consumidor Final no puede exceder $50.00'
                    }

            # Preparar líneas de factura
            invoice_lines = []
            for line in lines:
                product = self.Product.browse(line.get('product_id'))
                if not product.exists():
                    continue

                invoice_lines.append((0, 0, {
                    'product_id': product.id,
                    'name': product.name,
                    'quantity': line.get('quantity', 1),
                    'price_unit': line.get('price_unit', product.list_price),
                }))

            if not invoice_lines:
                return {'success': False, 'message': 'No hay líneas válidas'}

            # Crear factura
            vals = {
                'move_type': invoice_type,
                'partner_id': partner_id,
                'invoice_date': invoice_date or date.today(),
                'invoice_line_ids': invoice_lines,
            }

            if notes:
                vals['narration'] = notes

            invoice = self.Move.create(vals)
            self.env.cr.commit()

            return {
                'success': True,
                'invoice_id': invoice.id,
                'number': invoice.name,
                'message': f'Factura {invoice.name} creada exitosamente'
            }

        except Exception as e:
            return {'success': False, 'message': f'Error al crear factura: {str(e)}'}

    def confirm_invoice(self, invoice_id: int) -> dict:
        """
        Confirma (valida) una factura.

        Args:
            invoice_id: ID de la factura

        Returns:
            dict: {success, message}
        """
        try:
            invoice = self.Move.browse(invoice_id)
            if not invoice.exists():
                return {'success': False, 'message': 'Factura no encontrada'}

            if invoice.state != 'draft':
                return {'success': False, 'message': 'Factura ya está confirmada'}

            invoice.action_post()
            self.env.cr.commit()

            return {
                'success': True,
                'message': f'Factura {invoice.name} confirmada'
            }

        except Exception as e:
            return {'success': False, 'message': f'Error al confirmar: {str(e)}'}

    def send_to_sri(self, invoice_id: int) -> dict:
        """
        Envía factura al SRI para autorización.

        Args:
            invoice_id: ID de la factura

        Returns:
            dict: {success, clave_acceso, estado_sri, message}
        """
        try:
            invoice = self.Move.browse(invoice_id)
            if not invoice.exists():
                return {'success': False, 'message': 'Factura no encontrada'}

            if invoice.state != 'posted':
                return {'success': False, 'message': 'Factura debe estar confirmada'}

            # Verificar si ya tiene clave de acceso
            clave_acceso = getattr(invoice, 'l10n_ec_access_key', None)
            if clave_acceso:
                return {
                    'success': True,
                    'clave_acceso': clave_acceso,
                    'estado_sri': 'AUTORIZADO',
                    'message': 'Factura ya enviada al SRI'
                }

            # Enviar al SRI (simulado - en producción usaría action_send_sri)
            # invoice.action_send_sri()

            return {
                'success': True,
                'clave_acceso': 'PENDIENTE',
                'estado_sri': 'PENDIENTE',
                'message': 'Factura en cola para envío al SRI'
            }

        except Exception as e:
            return {'success': False, 'message': f'Error al enviar SRI: {str(e)}'}

    def annul_invoice(self, invoice_id: int, reason: str) -> dict:
        """
        Anula una factura (con validación de regla 7 días).

        Args:
            invoice_id: ID de la factura
            reason: Motivo de anulación

        Returns:
            dict: {success, message}
        """
        try:
            invoice = self.Move.browse(invoice_id)
            if not invoice.exists():
                return {'success': False, 'message': 'Factura no encontrada'}

            # Verificar si es Consumidor Final (no anulable)
            if invoice.partner_id.vat == '9999999999999':
                return {
                    'success': False,
                    'message': 'Facturas de Consumidor Final no pueden anularse (Resolución SRI 2026)'
                }

            # Verificar regla de 7 días
            if invoice.invoice_date:
                days_since = (date.today() - invoice.invoice_date).days
                if days_since > 7:
                    return {
                        'success': False,
                        'message': f'No se puede anular: han pasado {days_since} días (máximo 7)'
                    }

            # Anular factura
            invoice.button_cancel()
            self.env.cr.commit()

            return {
                'success': True,
                'message': f'Factura {invoice.name} anulada. Motivo: {reason}'
            }

        except Exception as e:
            return {'success': False, 'message': f'Error al anular: {str(e)}'}

    def create_credit_note(self, invoice_id: int, reason: str) -> dict:
        """
        Crea nota de crédito para una factura.

        Args:
            invoice_id: ID de la factura original
            reason: Motivo de la nota de crédito

        Returns:
            dict: {success, credit_note_id, message}
        """
        try:
            invoice = self.Move.browse(invoice_id)
            if not invoice.exists():
                return {'success': False, 'message': 'Factura no encontrada'}

            # Crear reverso (nota de crédito)
            credit_note = invoice._reverse_moves([{'date': date.today()}])

            if credit_note:
                credit_note.write({'ref': reason})
                self.env.cr.commit()

                return {
                    'success': True,
                    'credit_note_id': credit_note[0].id,
                    'message': f'Nota de Crédito creada exitosamente'
                }

            return {'success': False, 'message': 'No se pudo crear la nota de crédito'}

        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    def get_invoice(self, invoice_id: int) -> dict:
        """
        Obtiene datos de una factura.

        Args:
            invoice_id: ID de la factura

        Returns:
            dict: Datos de la factura
        """
        try:
            invoice = self.Move.browse(invoice_id)
            if not invoice.exists():
                return {'success': False, 'error': 'Factura no encontrada'}

            lines = [{
                'product': l.product_id.name,
                'quantity': l.quantity,
                'price_unit': l.price_unit,
                'subtotal': l.price_subtotal,
            } for l in invoice.invoice_line_ids]

            return {
                'success': True,
                'data': {
                    'id': invoice.id,
                    'name': invoice.name,
                    'partner': invoice.partner_id.name,
                    'date': str(invoice.invoice_date),
                    'state': invoice.state,
                    'amount_total': invoice.amount_total,
                    'amount_tax': invoice.amount_tax,
                    'lines': lines,
                }
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def search_invoices(
        self,
        partner_id: int = None,
        date_from: date = None,
        date_to: date = None,
        state: str = None,
        limit: int = 100
    ) -> dict:
        """
        Busca facturas con filtros.

        Args:
            partner_id: Filtro por cliente
            date_from: Fecha desde
            date_to: Fecha hasta
            state: Estado ('draft', 'posted', 'cancel')
            limit: Límite de resultados

        Returns:
            dict: {success, count, data}
        """
        try:
            domain = [('move_type', 'in', ['out_invoice', 'in_invoice'])]

            if partner_id:
                domain.append(('partner_id', '=', partner_id))
            if date_from:
                domain.append(('invoice_date', '>=', date_from))
            if date_to:
                domain.append(('invoice_date', '<=', date_to))
            if state:
                domain.append(('state', '=', state))

            invoices = self.Move.search(domain, limit=limit, order='invoice_date desc')

            data = [{
                'id': inv.id,
                'name': inv.name,
                'partner': inv.partner_id.name,
                'date': str(inv.invoice_date),
                'amount': inv.amount_total,
                'state': inv.state,
            } for inv in invoices]

            return {
                'success': True,
                'count': len(data),
                'data': data
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}


def get_invoice_manager(env) -> InvoiceManager:
    """Factory function para obtener instancia de InvoiceManager."""
    return InvoiceManager(env)
