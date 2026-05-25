# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
# Copyright 2026 Somatech.dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

"""
Demo Data Generator - Generador de Datos Demo Realistas vía MCP

Este módulo genera datos sintéticos pero realistas para
probar todos los flujos del ERP Ecuador.
"""

import logging
import random
from datetime import date, timedelta
from typing import Optional

_logger = logging.getLogger(__name__)

# Nombres ecuatorianos realistas
NOMBRES_MASCULINOS = [
    'Roberto', 'Carlos', 'Diego', 'Sebastián', 'Luis', 'Andrés', 'Fernando',
    'José', 'Juan', 'Miguel', 'Francisco', 'Gabriel', 'Daniel', 'Esteban'
]

NOMBRES_FEMENINOS = [
    'María', 'Andrea', 'Camila', 'Valentina', 'Sofía', 'Gabriela', 'Carolina',
    'Patricia', 'Mónica', 'Lucía', 'Isabel', 'Ana', 'Rosa', 'Carmen'
]

APELLIDOS = [
    'González', 'Rodríguez', 'Martínez', 'López', 'García', 'Hernández',
    'Pérez', 'Sánchez', 'Ramírez', 'Torres', 'Flores', 'Rivera', 'Gómez',
    'Díaz', 'Reyes', 'Morales', 'Jiménez', 'Ruiz', 'Vargas', 'Mendoza',
    'Paredes', 'Andrade', 'Mejía', 'Castro', 'Ortiz', 'Vega', 'Bravo'
]

CIUDADES_ECUADOR = [
    'Quito', 'Guayaquil', 'Cuenca', 'Manta', 'Machala', 'Ambato',
    'Loja', 'Esmeraldas', 'Santo Domingo', 'Ibarra', 'Riobamba'
]

CALLES = [
    'Av. Amazonas', 'Av. 6 de Diciembre', 'Av. República', 'Av. Eloy Alfaro',
    'Av. 10 de Agosto', 'Av. Patria', 'Calle Bolívar', 'Calle Sucre',
    'Av. Francisco de Orellana', 'Av. 9 de Octubre', 'Malecón 2000'
]


class DemoDataGenerator:
    """
    Generador de datos demo realistas para Ecuador.

    Genera partners, empleados, facturas, retenciones y
    datos de nómina para probar todos los flujos.
    """

    def __init__(self, env):
        """
        Inicializa el generador con el environment de Odoo.

        Args:
            env: Odoo environment
        """
        self.env = env
        self.Partner = env['res.partner']
        self.Product = env['product.product']
        self.Employee = env['hr.employee']
        self.Leave = env.get('hr.leave')
        self.Loan = env.get('l10n_ec.employee.loan')
        self.ecuador = env.ref('base.ec')

    def _random_name(self, gender: str = 'any') -> str:
        """Genera nombre aleatorio."""
        if gender == 'male':
            nombre = random.choice(NOMBRES_MASCULINOS)
        elif gender == 'female':
            nombre = random.choice(NOMBRES_FEMENINOS)
        else:
            nombre = random.choice(NOMBRES_MASCULINOS + NOMBRES_FEMENINOS)

        return f"{nombre} {random.choice(APELLIDOS)} {random.choice(APELLIDOS)}"

    def _random_address(self) -> dict:
        """Genera dirección aleatoria."""
        return {
            'city': random.choice(CIUDADES_ECUADOR),
            'street': f"{random.choice(CALLES)} {random.randint(100, 9999)}"
        }

    def generate_partners(
        self,
        count: int = 20,
        partner_type: str = 'mixed'
    ) -> dict:
        """
        Genera partners (clientes/proveedores) aleatorios.

        Args:
            count: Cantidad a generar
            partner_type: 'customer', 'supplier', 'mixed'

        Returns:
            dict: Resumen de generación
        """
        result = {'created': 0, 'ids': []}

        for i in range(count):
            addr = self._random_address()
            is_company = random.choice([True, True, False])  # 66% empresas

            if is_company:
                name = f"{random.choice(['COMERCIAL', 'INDUSTRIAS', 'SERVICIOS', 'DISTRIBUIDORA', 'IMPORTADORA'])} {random.choice(APELLIDOS).upper()} S.A."
            else:
                name = self._random_name()

            vals = {
                'name': name,
                'city': addr['city'],
                'street': addr['street'],
                'country_id': self.ecuador.id,
                'is_company': is_company,
                'phone': f"09{random.randint(10000000, 99999999)}",
            }

            if partner_type == 'customer' or (partner_type == 'mixed' and i % 2 == 0):
                vals['customer_rank'] = 1
            else:
                vals['supplier_rank'] = 1

            try:
                partner = self.Partner.create(vals)
                result['created'] += 1
                result['ids'].append(partner.id)
            except Exception as e:
                _logger.warning(f"Error creando partner: {e}")

        self.env.cr.commit()
        return result

    def generate_employees_with_history(
        self,
        count: int = 10
    ) -> dict:
        """
        Genera empleados con historial completo.

        Incluye:
        - Diferentes antigüedades (1-15 años)
        - Diferentes salarios (SBU a $5000)
        - Ausencias/permisos
        - Préstamos (quirografarios/hipotecarios)
        - Anticipos

        Args:
            count: Cantidad de empleados

        Returns:
            dict: Resumen de generación
        """
        result = {
            'employees': [],
            'leaves': [],
            'loans': [],
            'advances': []
        }

        # Departamentos
        departments = [
            'Administración', 'Ventas', 'Contabilidad', 'Producción',
            'Tecnología', 'Recursos Humanos', 'Logística'
        ]

        # Cargos con salarios
        jobs = [
            {'name': 'Gerente General', 'salary_min': 3500, 'salary_max': 5000},
            {'name': 'Contador Senior', 'salary_min': 2000, 'salary_max': 3000},
            {'name': 'Ejecutivo de Ventas', 'salary_min': 800, 'salary_max': 1500},
            {'name': 'Desarrollador', 'salary_min': 1500, 'salary_max': 2500},
            {'name': 'Asistente Administrativo', 'salary_min': 500, 'salary_max': 800},
            {'name': 'Operador de Producción', 'salary_min': 482, 'salary_max': 700},
            {'name': 'Analista', 'salary_min': 1000, 'salary_max': 1800},
        ]

        for i in range(count):
            gender = random.choice(['male', 'female'])
            job = random.choice(jobs)

            # Antigüedad variable (1-15 años)
            years_exp = random.randint(1, 15)
            start_date = date.today() - timedelta(days=years_exp * 365 + random.randint(0, 364))

            # Salario según cargo y antigüedad
            base_salary = random.uniform(job['salary_min'], job['salary_max'])
            seniority_bonus = base_salary * (years_exp * 0.02)  # +2% por año
            salary = round(base_salary + seniority_bonus, 2)

            emp_data = {
                'name': self._random_name(gender),
                'department': random.choice(departments),
                'job': job['name'],
                'start_date': str(start_date),
                'years_experience': years_exp,
                'salary': salary,
                'gender': gender,
            }

            # Generar historial de ausencias (2-10 por año)
            leaves_count = random.randint(2, 10) * years_exp
            leaves = []
            for _ in range(min(leaves_count, 50)):  # Máximo 50
                leave_type = random.choice([
                    'Vacaciones', 'Permiso Médico', 'Permiso Personal',
                    'Calamidad Doméstica', 'Maternidad/Paternidad'
                ])
                leave_days = random.randint(1, 15) if leave_type != 'Vacaciones' else random.randint(5, 15)
                leave_start = start_date + timedelta(days=random.randint(30, years_exp * 365))

                leaves.append({
                    'type': leave_type,
                    'start_date': str(leave_start),
                    'days': leave_days
                })
            emp_data['leaves'] = leaves

            # Generar préstamos (0-3)
            loans_count = random.randint(0, 3) if years_exp >= 2 else 0
            loans = []
            for _ in range(loans_count):
                loan_type = random.choice(['quirografario', 'hipotecario'])
                if loan_type == 'quirografario':
                    amount = random.uniform(500, 5000)
                    term_months = random.randint(12, 48)
                else:
                    amount = random.uniform(20000, 100000)
                    term_months = random.randint(60, 240)

                monthly_payment = round(amount / term_months, 2)

                loans.append({
                    'type': loan_type,
                    'amount': round(amount, 2),
                    'term_months': term_months,
                    'monthly_payment': monthly_payment,
                    'status': random.choice(['activo', 'pagado'])
                })
            emp_data['loans'] = loans

            # Generar anticipos (0-12 por año)
            advances = []
            for _ in range(random.randint(0, min(years_exp * 6, 30))):
                advance_date = start_date + timedelta(days=random.randint(60, years_exp * 365))
                advance_amount = random.uniform(50, min(salary * 0.5, 500))

                advances.append({
                    'date': str(advance_date),
                    'amount': round(advance_amount, 2),
                    'status': 'descontado'
                })
            emp_data['advances'] = advances

            result['employees'].append(emp_data)

        return result

    def generate_transactions(
        self,
        months: int = 12,
        invoices_per_month: int = 20
    ) -> dict:
        """
        Genera transacciones (facturas, retenciones) para un período.

        Args:
            months: Cantidad de meses hacia atrás
            invoices_per_month: Facturas por mes

        Returns:
            dict: Resumen de transacciones generadas
        """
        result = {
            'invoices': [],
            'retentions': [],
            'credit_notes': []
        }

        # Obtener productos existentes
        products = self.Product.search([], limit=20)
        if not products:
            return {'error': 'No hay productos disponibles'}

        # Obtener customers
        customers = self.Partner.search([('customer_rank', '>', 0)], limit=20)
        suppliers = self.Partner.search([('supplier_rank', '>', 0)], limit=20)

        for month in range(months):
            invoice_date = date.today() - timedelta(days=month * 30)

            for _ in range(invoices_per_month):
                # Alterna entre ventas y compras
                if random.choice([True, False]):
                    # Venta
                    partner = random.choice(customers) if customers else None
                    move_type = 'out_invoice'
                else:
                    # Compra
                    partner = random.choice(suppliers) if suppliers else None
                    move_type = 'in_invoice'

                if not partner:
                    continue

                # Líneas de factura
                lines_count = random.randint(1, 5)
                lines = []
                total = 0

                for _ in range(lines_count):
                    product = random.choice(products)
                    qty = random.randint(1, 10)
                    price = product.list_price or random.uniform(10, 500)

                    lines.append({
                        'product_id': product.id,
                        'quantity': qty,
                        'price_unit': price
                    })
                    total += qty * price

                invoice_data = {
                    'type': move_type,
                    'partner_id': partner.id,
                    'date': str(invoice_date + timedelta(days=random.randint(0, 28))),
                    'lines': lines,
                    'total': round(total, 2)
                }

                result['invoices'].append(invoice_data)

                # Generar retención para compras (80% de probabilidad)
                if move_type == 'in_invoice' and random.random() < 0.8:
                    retention_codes = ['303', '304', '307', '312']
                    code = random.choice(retention_codes)
                    rates = {'303': 0.10, '304': 0.08, '307': 0.02, '312': 0.01}

                    result['retentions'].append({
                        'invoice_ref': len(result['invoices']) - 1,
                        'code': code,
                        'base': round(total, 2),
                        'amount': round(total * rates[code], 2)
                    })

                # Nota de crédito ocasional (5% de ventas)
                if move_type == 'out_invoice' and random.random() < 0.05:
                    result['credit_notes'].append({
                        'original_invoice_ref': len(result['invoices']) - 1,
                        'reason': random.choice([
                            'Devolución de mercadería',
                            'Error en facturación',
                            'Descuento posterior'
                        ])
                    })

        return result

    def generate_full_demo(self) -> dict:
        """
        Genera dataset completo para demo.

        Incluye:
        - 50 partners (clientes/proveedores)
        - 15 empleados con historial
        - 12 meses de transacciones

        Returns:
            dict: Resumen completo
        """
        _logger.info("Generando datos demo completos...")

        result = {
            'partners': self.generate_partners(count=50),
            'employees': self.generate_employees_with_history(count=15),
            'transactions': self.generate_transactions(months=12, invoices_per_month=25)
        }

        _logger.info(f"Demo generado: {result['partners']['created']} partners, "
                    f"{len(result['employees']['employees'])} empleados, "
                    f"{len(result['transactions']['invoices'])} facturas")

        return result


def get_demo_data_generator(env) -> DemoDataGenerator:
    """Factory function para obtener instancia de DemoDataGenerator."""
    return DemoDataGenerator(env)
