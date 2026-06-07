# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
# Copyright 2026 Somatech.dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

"""
Partner Manager - Gestión de Contactos vía MCP

Este módulo proporciona operaciones CRUD completas para partners
con validación de RUC y sincronización SRI.
"""

import logging
from typing import Optional

_logger = logging.getLogger(__name__)


class PartnerManager:
    """
    Gestor de partners (clientes/proveedores) vía MCP.

    Proporciona operaciones CRUD con validación de RUC ecuatoriano
    y sincronización automática con datos del SRI.
    """

    def __init__(self, env):
        """
        Inicializa el gestor con el environment de Odoo.

        Args:
            env: Odoo environment
        """
        self.env = env
        self.Partner = env['res.partner']
        self.ecuador = env.ref('base.ec')

    def create_partner(
        self,
        name: str,
        vat: str = None,
        partner_type: str = 'customer',
        city: str = None,
        street: str = None,
        phone: str = None,
        email: str = None,
        is_company: bool = True,
        auto_load_sri: bool = True
    ) -> dict:
        """
        Crea un nuevo partner con validación y carga SRI opcional.

        Args:
            name: Nombre o razón social
            vat: RUC/Cédula (13/10 dígitos)
            partner_type: 'customer' o 'supplier'
            city: Ciudad
            street: Dirección
            phone: Teléfono
            email: Correo electrónico
            is_company: Si es empresa (True) o persona (False)
            auto_load_sri: Si True, carga datos del SRI automáticamente

        Returns:
            dict: {success, partner_id, message}
        """
        try:
            vals = {
                'name': name,
                'city': city or '',
                'street': street or '',
                'phone': phone or '',
                'email': email or '',
                'country_id': self.ecuador.id,
                'is_company': is_company,
            }

            if vat:
                vals['vat'] = vat

            if partner_type == 'customer':
                vals['customer_rank'] = 1
            elif partner_type == 'supplier':
                vals['supplier_rank'] = 1

            # Auto-cargar datos del SRI si se proporciona RUC
            if auto_load_sri and vat and len(vat) == 13:
                try:
                    sri_service = self.env['l10n_ec.sri.ruc.service']
                    result = sri_service.consultar_ruc(vat)

                    if result.get('success'):
                        data = result['data']
                        vals['name'] = data.get('razon_social', name)
                        vals['street'] = data.get('direccion', street or '')
                        vals['city'] = data.get('canton', city or '')

                        if data.get('nombre_comercial'):
                            vals['company_registry'] = data['nombre_comercial']
                except Exception as e:
                    _logger.warning(f"No se pudo cargar datos SRI: {e}")

            partner = self.Partner.create(vals)
            self.env.cr.commit()

            return {
                'success': True,
                'partner_id': partner.id,
                'message': f'Contacto {partner.name} creado exitosamente'
            }

        except Exception as e:
            return {
                'success': False,
                'partner_id': None,
                'message': f'Error al crear contacto: {str(e)}'
            }

    def bulk_create_partners(self, partners: list, skip_existing: bool = True) -> dict:
        """
        Crea múltiples partners en lote.

        Args:
            partners: Lista de diccionarios con datos de partners
            skip_existing: Si True, omite RUCs existentes

        Returns:
            dict: {created, skipped, errors, details}
        """
        result = {
            'created': 0,
            'skipped': 0,
            'errors': 0,
            'details': []
        }

        for p in partners:
            try:
                vat = p.get('vat', '')

                # Verificar si existe
                if skip_existing and vat:
                    existing = self.Partner.search([('vat', '=', vat)], limit=1)
                    if existing:
                        result['skipped'] += 1
                        result['details'].append({
                            'name': p.get('name', 'N/A'),
                            'status': 'omitido',
                            'reason': 'RUC ya existe'
                        })
                        continue

                # Crear partner
                create_result = self.create_partner(
                    name=p.get('name', 'Sin Nombre'),
                    vat=vat,
                    partner_type=p.get('type', 'customer'),
                    city=p.get('city'),
                    street=p.get('street'),
                    phone=p.get('phone'),
                    email=p.get('email'),
                    is_company=p.get('is_company', True),
                    auto_load_sri=p.get('auto_load_sri', True)
                )

                if create_result['success']:
                    result['created'] += 1
                    result['details'].append({
                        'name': p.get('name', 'N/A'),
                        'status': 'creado',
                        'partner_id': create_result['partner_id']
                    })
                else:
                    result['errors'] += 1
                    result['details'].append({
                        'name': p.get('name', 'N/A'),
                        'status': 'error',
                        'reason': create_result['message']
                    })

            except Exception as e:
                result['errors'] += 1
                result['details'].append({
                    'name': p.get('name', 'N/A'),
                    'status': 'error',
                    'reason': str(e)
                })

        return result

    def update_partner(self, partner_id: int, vals: dict) -> dict:
        """
        Actualiza un partner existente.

        Args:
            partner_id: ID del partner
            vals: Diccionario con valores a actualizar

        Returns:
            dict: {success, message}
        """
        try:
            partner = self.Partner.browse(partner_id)
            if not partner.exists():
                return {'success': False, 'message': 'Contacto no encontrado'}

            partner.write(vals)
            self.env.cr.commit()

            return {
                'success': True,
                'message': f'Contacto {partner.name} actualizado exitosamente'
            }

        except Exception as e:
            return {'success': False, 'message': f'Error al actualizar: {str(e)}'}

    def get_partner(self, partner_id: int = None, vat: str = None) -> dict:
        """
        Obtiene datos de un partner.

        Args:
            partner_id: ID del partner
            vat: RUC/Cédula para búsqueda

        Returns:
            dict: Datos del partner o error
        """
        try:
            if partner_id:
                partner = self.Partner.browse(partner_id)
            elif vat:
                partner = self.Partner.search([('vat', '=', vat)], limit=1)
            else:
                return {'success': False, 'error': 'Debe proporcionar partner_id o vat'}

            if not partner.exists():
                return {'success': False, 'error': 'Contacto no encontrado'}

            return {
                'success': True,
                'data': {
                    'id': partner.id,
                    'name': partner.name,
                    'vat': partner.vat,
                    'city': partner.city,
                    'street': partner.street,
                    'phone': partner.phone,
                    'email': partner.email,
                    'is_company': partner.is_company,
                    'customer_rank': partner.customer_rank,
                    'supplier_rank': partner.supplier_rank,
                }
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def search_partners(
        self,
        name: str = None,
        vat: str = None,
        city: str = None,
        partner_type: str = None,
        limit: int = 100
    ) -> dict:
        """
        Busca partners con filtros.

        Args:
            name: Filtro por nombre (ilike)
            vat: Filtro por RUC
            city: Filtro por ciudad
            partner_type: 'customer' o 'supplier'
            limit: Límite de resultados

        Returns:
            dict: {success, count, data}
        """
        try:
            domain = []

            if name:
                domain.append(('name', 'ilike', name))
            if vat:
                domain.append(('vat', 'ilike', vat))
            if city:
                domain.append(('city', 'ilike', city))
            if partner_type == 'customer':
                domain.append(('customer_rank', '>', 0))
            elif partner_type == 'supplier':
                domain.append(('supplier_rank', '>', 0))

            partners = self.Partner.search(domain, limit=limit)

            data = [{
                'id': p.id,
                'name': p.name,
                'vat': p.vat,
                'city': p.city,
            } for p in partners]

            return {
                'success': True,
                'count': len(data),
                'data': data
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def validate_ruc(self, ruc: str) -> dict:
        """
        Valida un RUC ecuatoriano.

        Args:
            ruc: Número de RUC (13 dígitos)

        Returns:
            dict: {valid, message, sri_data}
        """
        # Validación básica
        if not ruc or len(ruc) != 13 or not ruc.isdigit():
            return {
                'valid': False,
                'message': 'RUC debe tener 13 dígitos numéricos'
            }

        # Validar dígito verificador (módulo 11)
        try:
            sri_service = self.env['l10n_ec.sri.ruc.service']
            result = sri_service.consultar_ruc(ruc)

            if result.get('success'):
                return {
                    'valid': True,
                    'message': 'RUC válido',
                    'sri_data': result['data']
                }
            else:
                return {
                    'valid': False,
                    'message': result.get('error', 'RUC no encontrado en SRI')
                }

        except Exception as e:
            return {
                'valid': False,
                'message': f'Error al validar: {str(e)}'
            }


def get_partner_manager(env) -> PartnerManager:
    """
    Factory function para obtener instancia de PartnerManager.

    Args:
        env: Odoo environment

    Returns:
        PartnerManager: Instancia configurada
    """
    return PartnerManager(env)
