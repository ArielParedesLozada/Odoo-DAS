# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
# Copyright 2026 Somatech.dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

"""
Payroll Manager - Gestión de Nómina Ecuador vía MCP

Este módulo proporciona operaciones para nómina IESS,
décimos, utilidades y beneficios sociales.
"""

import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

_logger = logging.getLogger(__name__)

# Constantes IESS 2026
SBU_2026 = 482.00
IESS_PERSONAL = 0.0945  # 9.45%
IESS_PATRONAL = 0.1115  # 11.15%
IESS_SECAP = 0.005  # 0.5%
IESS_IECE = 0.005  # 0.5%
IESS_TOTAL_PATRONAL = IESS_PATRONAL + IESS_SECAP + IESS_IECE  # 12.15%
FONDOS_RESERVA = 0.0833  # 8.33%
TECHO_IESS = SBU_2026 * 25  # $12,050

# Horas extras
RECARGO_SUPLEMENTARIA = 1.50  # +50%
RECARGO_EXTRAORDINARIA = 2.00  # +100%
RECARGO_NOCTURNA = 1.25  # +25%


class PayrollManager:
    """
    Gestor de nómina Ecuador vía MCP.

    Proporciona cálculos de IESS, décimos, utilidades
    y todos los beneficios sociales según ley ecuatoriana.
    """

    def __init__(self, env):
        """
        Inicializa el gestor con el environment de Odoo.

        Args:
            env: Odoo environment
        """
        self.env = env
        self.Employee = env['hr.employee']
        self.Payslip = env.get('l10n_ec.payslip')

    def calculate_iess(self, gross_salary: float) -> dict:
        """
        Calcula aportes IESS.

        Args:
            gross_salary: Salario bruto mensual

        Returns:
            dict: Desglose de aportes IESS
        """
        # Aplicar techo
        base = min(gross_salary, TECHO_IESS)

        personal = round(base * IESS_PERSONAL, 2)
        patronal = round(base * IESS_PATRONAL, 2)
        secap = round(base * IESS_SECAP, 2)
        iece = round(base * IESS_IECE, 2)

        return {
            'base_aportacion': base,
            'aporte_personal': personal,
            'aporte_patronal': patronal,
            'secap': secap,
            'iece': iece,
            'total_empleado': personal,
            'total_empleador': round(patronal + secap + iece, 2),
            'techo_aplicado': gross_salary > TECHO_IESS
        }

    def calculate_payslip(
        self,
        employee_id: int,
        period: str,
        gross_salary: float = None,
        overtime_hours: dict = None,
        deductions: dict = None
    ) -> dict:
        """
        Calcula rol de pagos completo.

        Args:
            employee_id: ID del empleado
            period: Período (YYYY-MM)
            gross_salary: Salario bruto (si diferente del contrato)
            overtime_hours: {suplementarias, extraordinarias, nocturnas}
            deductions: {anticipos, prestamos, otros}

        Returns:
            dict: Rol de pagos completo
        """
        try:
            employee = self.Employee.browse(employee_id)
            if not employee.exists():
                return {'success': False, 'message': 'Empleado no encontrado'}

            # Obtener salario del contrato o usar el proporcionado
            salary = gross_salary or SBU_2026  # Default SBU

            # Calcular hora de trabajo
            hour_rate = salary / 240  # 30 días * 8 horas

            # Calcular horas extras
            overtime = overtime_hours or {}
            overtime_pay = 0

            suplementarias = overtime.get('suplementarias', 0)
            extraordinarias = overtime.get('extraordinarias', 0)
            nocturnas = overtime.get('nocturnas', 0)

            overtime_pay += suplementarias * hour_rate * RECARGO_SUPLEMENTARIA
            overtime_pay += extraordinarias * hour_rate * RECARGO_EXTRAORDINARIA
            overtime_pay += nocturnas * hour_rate * RECARGO_NOCTURNA
            overtime_pay = round(overtime_pay, 2)

            # Total ingresos
            total_ingresos = salary + overtime_pay

            # Calcular IESS
            iess = self.calculate_iess(total_ingresos)

            # Deducciones adicionales
            deductions = deductions or {}
            anticipos = deductions.get('anticipos', 0)
            prestamos = deductions.get('prestamos', 0)
            otros = deductions.get('otros', 0)
            total_deducciones = iess['aporte_personal'] + anticipos + prestamos + otros

            # Neto a pagar
            neto = round(total_ingresos - total_deducciones, 2)

            return {
                'success': True,
                'employee': employee.name,
                'period': period,
                'ingresos': {
                    'salario_base': salary,
                    'horas_extras': overtime_pay,
                    'total_ingresos': total_ingresos
                },
                'deducciones': {
                    'iess_personal': iess['aporte_personal'],
                    'anticipos': anticipos,
                    'prestamos': prestamos,
                    'otros': otros,
                    'total_deducciones': round(total_deducciones, 2)
                },
                'iess': iess,
                'neto_pagar': neto,
                'provisiones': {
                    'decimo_tercero': round(total_ingresos / 12, 2),
                    'decimo_cuarto': round(SBU_2026 / 12, 2),
                    'vacaciones': round(total_ingresos / 24, 2),
                    'fondos_reserva': round(total_ingresos * FONDOS_RESERVA, 2)
                }
            }

        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    def calculate_decimo_tercero(
        self,
        employee_id: int,
        year: int,
        earnings: list = None
    ) -> dict:
        """
        Calcula décimo tercer sueldo (aguinaldo).

        Período: 1 Diciembre año anterior - 30 Noviembre año actual
        Pago: Hasta 24 de Diciembre

        Args:
            employee_id: ID del empleado
            year: Año de cálculo
            earnings: Lista de ingresos mensuales (opcional)

        Returns:
            dict: Cálculo del décimo tercero
        """
        try:
            employee = self.Employee.browse(employee_id)
            if not employee.exists():
                return {'success': False, 'message': 'Empleado no encontrado'}

            # Si no se proporcionan ingresos, usar SBU * 12
            if not earnings:
                earnings = [SBU_2026] * 12

            total_earnings = sum(earnings)
            decimo_tercero = round(total_earnings / 12, 2)

            return {
                'success': True,
                'employee': employee.name,
                'year': year,
                'periodo': f'Dic {year-1} - Nov {year}',
                'total_ingresos': total_earnings,
                'decimo_tercero': decimo_tercero,
                'fecha_limite_pago': f'{year}-12-24'
            }

        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    def calculate_decimo_cuarto(
        self,
        employee_id: int,
        year: int,
        region: str = 'sierra'
    ) -> dict:
        """
        Calcula décimo cuarto sueldo (bono escolar).

        Costa/Galápagos: 1 Marzo - 28 Febrero, pago 15 Marzo
        Sierra/Oriente: 1 Agosto - 31 Julio, pago 15 Agosto

        Args:
            employee_id: ID del empleado
            year: Año de cálculo
            region: 'costa' o 'sierra'

        Returns:
            dict: Cálculo del décimo cuarto
        """
        try:
            employee = self.Employee.browse(employee_id)
            if not employee.exists():
                return {'success': False, 'message': 'Empleado no encontrado'}

            if region.lower() == 'costa':
                periodo = f'Mar {year-1} - Feb {year}'
                fecha_pago = f'{year}-03-15'
            else:  # sierra
                periodo = f'Ago {year-1} - Jul {year}'
                fecha_pago = f'{year}-08-15'

            return {
                'success': True,
                'employee': employee.name,
                'year': year,
                'region': region,
                'periodo': periodo,
                'decimo_cuarto': SBU_2026,  # Siempre 1 SBU
                'fecha_pago': fecha_pago
            }

        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    def calculate_utilidades(
        self,
        year: int,
        net_profit: float,
        employees_data: list
    ) -> dict:
        """
        Calcula participación de utilidades (15%).

        10% según días trabajados
        5% según cargas familiares

        Args:
            year: Año fiscal
            net_profit: Utilidad neta del ejercicio
            employees_data: Lista de {employee_id, days_worked, dependents}

        Returns:
            dict: Distribución de utilidades
        """
        try:
            if net_profit <= 0:
                return {
                    'success': True,
                    'message': 'No hay utilidades a distribuir',
                    'total': 0
                }

            total_15 = round(net_profit * 0.15, 2)
            portion_10 = round(total_15 * (10/15), 2)
            portion_5 = round(total_15 * (5/15), 2)

            total_days = sum(e.get('days_worked', 0) for e in employees_data)
            total_dependents = sum(e.get('dependents', 0) for e in employees_data)

            distribution = []
            for emp in employees_data:
                days = emp.get('days_worked', 0)
                deps = emp.get('dependents', 0)

                share_10 = round(portion_10 * (days / total_days), 2) if total_days > 0 else 0
                share_5 = round(portion_5 * (deps / total_dependents), 2) if total_dependents > 0 else 0

                distribution.append({
                    'employee_id': emp.get('employee_id'),
                    'days_worked': days,
                    'dependents': deps,
                    'share_10_percent': share_10,
                    'share_5_percent': share_5,
                    'total': round(share_10 + share_5, 2)
                })

            return {
                'success': True,
                'year': year,
                'utilidad_neta': net_profit,
                'total_15_percent': total_15,
                'portion_10_percent': portion_10,
                'portion_5_percent': portion_5,
                'fecha_limite_pago': f'{year + 1}-04-15',
                'distribution': distribution
            }

        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    def calculate_fondos_reserva(
        self,
        employee_id: int,
        gross_salary: float,
        months_worked: int
    ) -> dict:
        """
        Calcula fondos de reserva (8.33%).

        Disponible después de 13 meses de trabajo.

        Args:
            employee_id: ID del empleado
            gross_salary: Salario bruto
            months_worked: Meses trabajados

        Returns:
            dict: Cálculo de fondos de reserva
        """
        try:
            employee = self.Employee.browse(employee_id)
            if not employee.exists():
                return {'success': False, 'message': 'Empleado no encontrado'}

            eligible = months_worked >= 13
            amount = round(gross_salary * FONDOS_RESERVA, 2) if eligible else 0

            return {
                'success': True,
                'employee': employee.name,
                'months_worked': months_worked,
                'eligible': eligible,
                'percentage': FONDOS_RESERVA * 100,
                'amount': amount,
                'message': 'Elegible para fondos de reserva' if eligible else 'Requiere 13 meses de trabajo'
            }

        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    def get_parameters_2026(self) -> dict:
        """
        Obtiene todos los parámetros de nómina 2026.

        Returns:
            dict: Parámetros vigentes
        """
        return {
            'success': True,
            'year': 2026,
            'sbu': SBU_2026,
            'hora_trabajo': round(SBU_2026 / 240, 2),
            'iess': {
                'personal': IESS_PERSONAL * 100,
                'patronal': IESS_PATRONAL * 100,
                'secap': IESS_SECAP * 100,
                'iece': IESS_IECE * 100,
                'total_empleador': IESS_TOTAL_PATRONAL * 100,
                'techo': TECHO_IESS
            },
            'fondos_reserva': FONDOS_RESERVA * 100,
            'horas_extras': {
                'suplementaria': '+50%',
                'extraordinaria': '+100%',
                'nocturna': '+25%'
            }
        }


def get_payroll_manager(env) -> PayrollManager:
    """Factory function para obtener instancia de PayrollManager."""
    return PayrollManager(env)
