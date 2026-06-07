# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
# Copyright 2026 Somatech.dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

"""
MCP (Model Context Protocol) - Operaciones Odoo Ecuador

Este paquete proporciona herramientas MCP para todas las operaciones
del ERP incluyendo integración con SRI Datos Abiertos.
"""

from . import sri_data_loader
from . import partner_manager
from . import invoice_manager
from . import retention_manager
from . import payroll_manager
from . import demo_data_generator
from . import gov_services_registry
from . import open_data_sources

