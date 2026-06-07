# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
# Copyright 2026 Somatech.dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

"""
Ecuador Government Services Registry - Registro de Servicios Gubernamentales

Este módulo centraliza todas las integraciones con servicios
del gobierno ecuatoriano: SRI, MDT, IESS, SENAE, BCE, etc.

Proporciona herramientas MCP reutilizables para todos los módulos.
"""

import logging
from typing import Optional, Dict, Any

_logger = logging.getLogger(__name__)


# =============================================================================
# REGISTRO DE ENDPOINTS GUBERNAMENTALES
# =============================================================================

ECUADOR_GOV_SERVICES = {
    # -------------------------------------------------------------------------
    # SRI - SERVICIO DE RENTAS INTERNAS
    # -------------------------------------------------------------------------
    'sri': {
        'name': 'Servicio de Rentas Internas',
        'website': 'https://www.sri.gob.ec',
        'services': {
            # Facturación Electrónica - Ambiente Pruebas
            'recepcion_pruebas': {
                'url': 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline',
                'wsdl': 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl',
                'type': 'SOAP',
                'description': 'Recepción de comprobantes electrónicos (pruebas)',
            },
            'autorizacion_pruebas': {
                'url': 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline',
                'wsdl': 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl',
                'type': 'SOAP',
                'description': 'Autorización de comprobantes electrónicos (pruebas)',
            },
            # Facturación Electrónica - Ambiente Producción
            'recepcion_produccion': {
                'url': 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline',
                'wsdl': 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl',
                'type': 'SOAP',
                'description': 'Recepción de comprobantes electrónicos (producción)',
            },
            'autorizacion_produccion': {
                'url': 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline',
                'wsdl': 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl',
                'type': 'SOAP',
                'description': 'Autorización de comprobantes electrónicos (producción)',
            },
            # Consulta RUC (Web - requiere scraping o API terceros)
            'consulta_ruc_web': {
                'url': 'https://srienlinea.sri.gob.ec/sri-en-linea/SriRucWeb/ConsultaRuc/Consultas/consultaRuc',
                'type': 'WEB',
                'description': 'Consulta RUC vía portal web (no API directa)',
                'notes': 'Requiere integración vía web scraping o servicios terceros',
            },
            # Datos Abiertos
            'datos_abiertos': {
                'url': 'https://www.sri.gob.ec/datos-abiertos',
                'type': 'CSV',
                'description': 'Datasets públicos: catastro, recaudación, etc.',
            },
        },
    },

    # -------------------------------------------------------------------------
    # MDT - MINISTERIO DEL TRABAJO
    # -------------------------------------------------------------------------
    'mdt': {
        'name': 'Ministerio del Trabajo',
        'website': 'https://www.trabajo.gob.ec',
        'services': {
            # SUT - Sistema Único de Trabajo
            'sut_contratos': {
                'url': 'https://sut.trabajo.gob.ec/mrl/loginContratos.xhtml',
                'type': 'WEB',
                'description': 'Registro de contratos de trabajo',
                'notes': 'Portal web, sin API pública disponible',
            },
            'sut_actas_finiquito': {
                'url': 'https://sut.trabajo.gob.ec/mrl/actas',
                'type': 'WEB',
                'description': 'Actas de finiquito',
            },
            'sut_decimo_tercero': {
                'url': 'https://sut.trabajo.gob.ec/decimotercero',
                'type': 'WEB',
                'description': 'Registro de pago décimo tercero',
            },
            'sut_decimo_cuarto': {
                'url': 'https://sut.trabajo.gob.ec/decimocuarto',
                'type': 'WEB',
                'description': 'Registro de pago décimo cuarto',
            },
            'sut_utilidades': {
                'url': 'https://sut.trabajo.gob.ec/utilidades',
                'type': 'WEB',
                'description': 'Registro de pago de utilidades',
            },
            # Datos Abiertos MDT
            'datos_abiertos': {
                'url': 'https://www.trabajo.gob.ec/datos-abiertos/',
                'type': 'CSV',
                'description': 'Datasets: contratos, actas, salarios',
            },
        },
    },

    # -------------------------------------------------------------------------
    # IESS - INSTITUTO ECUATORIANO DE SEGURIDAD SOCIAL
    # -------------------------------------------------------------------------
    'iess': {
        'name': 'Instituto Ecuatoriano de Seguridad Social',
        'website': 'https://www.iess.gob.ec',
        'services': {
            'portal_empleador': {
                'url': 'https://www.iess.gob.ec/empleador-web/',
                'type': 'WEB',
                'description': 'Portal del empleador para avisos entrada/salida',
            },
            'historia_laboral': {
                'url': 'https://www.iess.gob.ec/afiliado-web/',
                'type': 'WEB',
                'description': 'Consulta historia laboral afiliado',
            },
            'planillas': {
                'url': 'https://www.iess.gob.ec/PortalEmpleador/comprobante/planillas.do',
                'type': 'WEB',
                'description': 'Generación y pago de planillas',
            },
        },
    },

    # -------------------------------------------------------------------------
    # SENAE - SERVICIO NACIONAL DE ADUANA DEL ECUADOR
    # -------------------------------------------------------------------------
    'senae': {
        'name': 'Servicio Nacional de Aduana del Ecuador',
        'website': 'https://www.aduana.gob.ec',
        'services': {
            'ecuapass': {
                'url': 'https://portal.aduana.gob.ec',
                'type': 'WEB',
                'description': 'Portal ECUAPASS para operaciones aduaneras',
            },
            'consulta_arancel': {
                'url': 'https://mesadeservicios.aduana.gob.ec/arancel/',
                'type': 'WEB',
                'description': 'Consulta de partidas arancelarias',
            },
        },
    },

    # -------------------------------------------------------------------------
    # BCE - BANCO CENTRAL DEL ECUADOR
    # -------------------------------------------------------------------------
    'bce': {
        'name': 'Banco Central del Ecuador',
        'website': 'https://www.bce.fin.ec',
        'services': {
            'tipo_cambio': {
                'url': 'https://www.bce.fin.ec/cotizacion-y-tasas/informacion/cotizaciones',
                'type': 'WEB',
                'description': 'Cotizaciones de monedas',
            },
            'inflacion': {
                'url': 'https://www.bce.fin.ec/estadisticas-economicas/',
                'type': 'WEB',
                'description': 'Estadísticas económicas',
            },
        },
    },

    # -------------------------------------------------------------------------
    # SUPERCIAS - SUPERINTENDENCIA DE COMPAÑÍAS
    # -------------------------------------------------------------------------
    'supercias': {
        'name': 'Superintendencia de Compañías',
        'website': 'https://www.supercias.gob.ec',
        'services': {
            'consulta_companias': {
                'url': 'https://appscvs.supercias.gob.ec/portalInformacion/sector_societario.zul',
                'type': 'WEB',
                'description': 'Consulta información de compañías',
            },
            'portal_empresas': {
                'url': 'https://www.supercias.gob.ec/portalext/',
                'type': 'WEB',
                'description': 'Portal de empresas',
            },
        },
    },

    # -------------------------------------------------------------------------
    # REGISTRO CIVIL
    # -------------------------------------------------------------------------
    'registro_civil': {
        'name': 'Dirección General de Registro Civil',
        'website': 'https://www.registrocivil.gob.ec',
        'services': {
            'consulta_cedula': {
                'url': 'https://www.registrocivil.gob.ec/cedulacion/',
                'type': 'WEB',
                'description': 'Validación de cédulas de identidad',
            },
        },
    },
}


class EcuadorGovServiceRegistry:
    """
    Registro centralizado de servicios gubernamentales de Ecuador.

    Proporciona métodos para obtener URLs, configuración
    y estado de los servicios.
    """

    def __init__(self, env=None):
        """
        Inicializa el registro de servicios.

        Args:
            env: Odoo environment (opcional)
        """
        self.env = env
        self.services = ECUADOR_GOV_SERVICES

    def get_service(self, entity: str, service_name: str) -> dict:
        """
        Obtiene información de un servicio específico.

        Args:
            entity: Código de entidad ('sri', 'mdt', 'iess', etc.)
            service_name: Nombre del servicio

        Returns:
            dict: Información del servicio
        """
        entity_data = self.services.get(entity.lower())
        if not entity_data:
            return {'error': f'Entidad {entity} no encontrada'}

        service = entity_data.get('services', {}).get(service_name)
        if not service:
            return {'error': f'Servicio {service_name} no encontrado en {entity}'}

        return {
            'success': True,
            'entity': entity_data['name'],
            'service': service_name,
            **service
        }

    def get_sri_endpoint(self, environment: str = 'pruebas', service: str = 'recepcion') -> dict:
        """
        Obtiene endpoint SRI para facturación electrónica.

        Args:
            environment: 'pruebas' o 'produccion'
            service: 'recepcion' o 'autorizacion'

        Returns:
            dict: URLs y WSDL del servicio
        """
        service_key = f'{service}_{environment}'
        return self.get_service('sri', service_key)

    def list_entities(self) -> list:
        """
        Lista todas las entidades registradas.

        Returns:
            list: Lista de entidades con nombre y servicios
        """
        return [
            {
                'code': code,
                'name': data['name'],
                'website': data['website'],
                'services_count': len(data.get('services', {}))
            }
            for code, data in self.services.items()
        ]

    def list_services(self, entity: str) -> list:
        """
        Lista todos los servicios de una entidad.

        Args:
            entity: Código de entidad

        Returns:
            list: Lista de servicios
        """
        entity_data = self.services.get(entity.lower())
        if not entity_data:
            return []

        return [
            {
                'name': name,
                'type': data.get('type'),
                'description': data.get('description'),
                'url': data.get('url')
            }
            for name, data in entity_data.get('services', {}).items()
        ]

    def check_service_status(self, entity: str, service_name: str) -> dict:
        """
        Verifica si un servicio está disponible.

        Args:
            entity: Código de entidad
            service_name: Nombre del servicio

        Returns:
            dict: Estado del servicio
        """
        import requests

        service = self.get_service(entity, service_name)
        if service.get('error'):
            return service

        url = service.get('url') or service.get('wsdl')
        if not url:
            return {'status': 'unknown', 'message': 'No URL disponible'}

        try:
            response = requests.head(url, timeout=10, allow_redirects=True)

            return {
                'status': 'online' if response.status_code < 400 else 'error',
                'http_code': response.status_code,
                'url': url
            }
        except requests.RequestException as e:
            return {
                'status': 'offline',
                'error': str(e),
                'url': url
            }


def get_service_registry(env=None) -> EcuadorGovServiceRegistry:
    """Factory function para obtener instancia del registro de servicios."""
    return EcuadorGovServiceRegistry(env)


# =============================================================================
# CONSTANTES ÚTILES
# =============================================================================

# Endpoints SRI por ambiente (acceso rápido)
SRI_ENDPOINTS = {
    'pruebas': {
        'recepcion': 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl',
        'autorizacion': 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl',
    },
    'produccion': {
        'recepcion': 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl',
        'autorizacion': 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl',
    },
}

# Tipos de comprobantes SRI
TIPOS_COMPROBANTE_SRI = {
    '01': 'Factura',
    '03': 'Liquidación de Compra',
    '04': 'Nota de Crédito',
    '05': 'Nota de Débito',
    '06': 'Guía de Remisión',
    '07': 'Comprobante de Retención',
}

# Estados de autorización SRI
ESTADOS_AUTORIZACION = {
    'AUTORIZADO': 'Comprobante autorizado',
    'NO AUTORIZADO': 'Comprobante rechazado',
    'EN PROCESO': 'Comprobante en proceso de autorización',
    'DEVUELTA': 'Comprobante devuelto por errores',
    'RECIBIDA': 'Comprobante recibido, pendiente autorización',
}
