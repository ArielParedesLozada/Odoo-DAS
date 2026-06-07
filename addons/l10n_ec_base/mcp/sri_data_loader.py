# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
# Copyright 2026 Somatech.dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

"""
SRI Data Loader - Carga de Datos desde SRI Datos Abiertos

Este módulo permite:
- Descargar catastro de contribuyentes desde datos.sri.gob.ec
- Importar partners desde archivos CSV
- Sincronizar datos con el SRI en tiempo real
"""

import csv
import logging
import requests
from io import StringIO
from typing import Optional

_logger = logging.getLogger(__name__)

# URLs SRI Datos Abiertos
SRI_DATOS_ABIERTOS_BASE = "https://www.sri.gob.ec/o/sri-portlet-biblioteca-alfresco-internet/descargar"


class SRIDataLoader:
    """
    Cargador de datos desde SRI Datos Abiertos.

    Proporciona métodos para descargar y procesar datasets del SRI
    incluyendo el catastro de contribuyentes.
    """

    def __init__(self, env):
        """
        Inicializa el cargador con el environment de Odoo.

        Args:
            env: Odoo environment
        """
        self.env = env
        self.Partner = env['res.partner']
        self.ecuador = env.ref('base.ec')

    def download_catastro_csv(self, url: str = None) -> str:
        """
        Descarga archivo CSV del catastro de contribuyentes.

        Args:
            url: URL del archivo CSV (opcional)

        Returns:
            str: Contenido del CSV descargado
        """
        if not url:
            _logger.warning("URL de catastro no proporcionada")
            return ""

        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            _logger.error(f"Error descargando catastro: {e}")
            return ""

    def parse_catastro_csv(self, csv_content: str, delimiter: str = '|') -> list:
        """
        Parsea contenido CSV del catastro SRI.

        Args:
            csv_content: Contenido del archivo CSV
            delimiter: Delimitador (SRI usa '|')

        Returns:
            list: Lista de diccionarios con datos de contribuyentes
        """
        if not csv_content:
            return []

        contribuyentes = []
        reader = csv.DictReader(StringIO(csv_content), delimiter=delimiter)

        for row in reader:
            contribuyente = {
                'ruc': row.get('RUC', '').strip(),
                'razon_social': row.get('RAZON_SOCIAL', row.get('RAZON SOCIAL', '')).strip(),
                'nombre_comercial': row.get('NOMBRE_COMERCIAL', row.get('NOMBRE COMERCIAL', '')).strip(),
                'estado': row.get('ESTADO', '').strip(),
                'tipo_contribuyente': row.get('TIPO_CONTRIBUYENTE', row.get('TIPO CONTRIBUYENTE', '')).strip(),
                'clase_contribuyente': row.get('CLASE_CONTRIBUYENTE', row.get('CLASE CONTRIBUYENTE', '')).strip(),
                'actividad_economica': row.get('ACTIVIDAD_ECONOMICA', row.get('ACTIVIDAD ECONOMICA', '')).strip(),
                'direccion': row.get('DIRECCION', '').strip(),
                'provincia': row.get('PROVINCIA', '').strip(),
                'canton': row.get('CANTON', '').strip(),
            }

            if contribuyente['ruc'] and len(contribuyente['ruc']) == 13:
                contribuyentes.append(contribuyente)

        return contribuyentes

    def import_partners_from_catastro(
        self,
        contribuyentes: list,
        limit: int = 1000,
        skip_existing: bool = True
    ) -> dict:
        """
        Importa partners desde lista de contribuyentes del catastro.

        Args:
            contribuyentes: Lista de contribuyentes parseados
            limit: Límite de registros a importar
            skip_existing: Si True, omite RUCs que ya existen

        Returns:
            dict: Resumen de importación {created, skipped, errors}
        """
        result = {
            'created': 0,
            'skipped': 0,
            'errors': 0,
            'error_details': []
        }

        for i, contrib in enumerate(contribuyentes[:limit]):
            try:
                ruc = contrib.get('ruc', '')

                # Verificar si ya existe
                if skip_existing:
                    existing = self.Partner.search([('vat', '=', ruc)], limit=1)
                    if existing:
                        result['skipped'] += 1
                        continue

                # Crear partner
                vals = {
                    'name': contrib.get('razon_social', ruc),
                    'vat': ruc,
                    'street': contrib.get('direccion', ''),
                    'city': contrib.get('canton', ''),
                    'country_id': self.ecuador.id,
                    'is_company': True,
                    'customer_rank': 1,
                }

                # Agregar nombre comercial si existe
                if contrib.get('nombre_comercial'):
                    vals['company_registry'] = contrib['nombre_comercial']

                self.Partner.create(vals)
                result['created'] += 1

                # Commit cada 100 registros
                if (i + 1) % 100 == 0:
                    self.env.cr.commit()
                    _logger.info(f"Importados {i + 1} contribuyentes...")

            except Exception as e:
                result['errors'] += 1
                result['error_details'].append({
                    'ruc': contrib.get('ruc', 'N/A'),
                    'error': str(e)
                })

        # Commit final
        self.env.cr.commit()

        _logger.info(
            f"Importación completada: {result['created']} creados, "
            f"{result['skipped']} omitidos, {result['errors']} errores"
        )

        return result

    def sync_partner_with_sri(self, ruc: str) -> dict:
        """
        Sincroniza un partner con datos en tiempo real del SRI.

        Args:
            ruc: Número de RUC a consultar

        Returns:
            dict: Resultado de la sincronización
        """
        try:
            sri_service = self.env['l10n_ec.sri.ruc.service']
            result = sri_service.consultar_ruc(ruc)

            if not result.get('success'):
                return {'success': False, 'error': result.get('error', 'Error desconocido')}

            data = result['data']

            # Buscar o crear partner
            partner = self.Partner.search([('vat', '=', ruc)], limit=1)

            vals = {
                'name': data.get('razon_social', ruc),
                'street': data.get('direccion', ''),
                'city': data.get('canton', ''),
                'country_id': self.ecuador.id,
                'is_company': True,
            }

            if data.get('nombre_comercial'):
                vals['company_registry'] = data['nombre_comercial']

            if partner:
                partner.write(vals)
                action = 'actualizado'
            else:
                vals['vat'] = ruc
                partner = self.Partner.create(vals)
                action = 'creado'

            self.env.cr.commit()

            return {
                'success': True,
                'partner_id': partner.id,
                'action': action,
                'data': data
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def bulk_sync_partners(self, rucs: list) -> dict:
        """
        Sincroniza múltiples partners con el SRI.

        Args:
            rucs: Lista de RUCs a sincronizar

        Returns:
            dict: Resumen de sincronización
        """
        result = {
            'synced': 0,
            'errors': 0,
            'details': []
        }

        for ruc in rucs:
            sync_result = self.sync_partner_with_sri(ruc)

            if sync_result.get('success'):
                result['synced'] += 1
            else:
                result['errors'] += 1

            result['details'].append({
                'ruc': ruc,
                'result': sync_result
            })

        return result


def get_sri_data_loader(env) -> SRIDataLoader:
    """
    Factory function para obtener instancia de SRIDataLoader.

    Args:
        env: Odoo environment

    Returns:
        SRIDataLoader: Instancia configurada
    """
    return SRIDataLoader(env)
