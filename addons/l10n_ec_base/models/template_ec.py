# -*- coding: utf-8 -*-
from odoo import Command, models
from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    @template("ec")
    def _get_ec_template_data(self):
        return {
            "code_digits": 6,
            "property_account_receivable_id": "account_1020102",
            "property_account_payable_id": "account_2010102",
            "property_account_expense_categ_id": "account_5020101",
            "property_account_income_categ_id": "account_4010101",
            "name": "Ecuador - NEC 2026",
        }

    @template("ec", "res.company")
    def _get_ec_res_company(self):
        return {
            self.env.company.id: {
                "account_fiscal_country_id": "base.ec",
                "bank_account_code_prefix": "10102",
                "cash_account_code_prefix": "10101",
                "transfer_account_code_prefix": "10103",
                "account_default_pos_receivable_account_id": "account_1020102",
                "income_currency_exchange_account_id": "account_4020102",
                "expense_currency_exchange_account_id": "account_5020302",
                "account_journal_suspense_account_id": "account_1010201",
                "account_journal_payment_debit_account_id": "account_1010201",
                "account_journal_payment_credit_account_id": "account_1010201",
            }
        }

    @template("ec", "account.account")
    def _get_ec_account_account(self):
        accounts = {
            "1010101": {
                "name": "Caja General",
                "account_type": "asset_cash",
                "reconcile": True,
            },
            "1010102": {
                "name": "Caja Chica",
                "account_type": "asset_cash",
                "reconcile": True,
            },
            "1010201": {
                "name": "Bancos Nacionales",
                "account_type": "asset_cash",
                "reconcile": True,
            },
            "1010202": {
                "name": "Bancos del Exterior",
                "account_type": "asset_cash",
                "reconcile": True,
            },
            "1010301": {
                "name": "Inversiones Temporales",
                "account_type": "asset_current",
                "reconcile": False,
            },
            "1020101": {
                "name": "Cuentas por Cobrar Clientes Relacionados",
                "account_type": "asset_receivable",
                "reconcile": True,
            },
            "1020102": {
                "name": "Cuentas por Cobrar Clientes No Relacionados",
                "account_type": "asset_receivable",
                "reconcile": True,
            },
            "1020103": {
                "name": " Otras Cuentas por Cobrar",
                "account_type": "asset_receivable",
                "reconcile": True,
            },
            "1020201": {
                "name": "Provisión Cuentas Incobrables",
                "account_type": "asset_current",
                "reconcile": False,
            },
            "1030101": {
                "name": "Inventario de Mercaderías",
                "account_type": "asset_current",
                "reconcile": False,
            },
            "1030102": {
                "name": "Inventario de Materia Prima",
                "account_type": "asset_current",
                "reconcile": False,
            },
            "1030103": {
                "name": "Inventario de Productos en Proceso",
                "account_type": "asset_current",
                "reconcile": False,
            },
            "1030104": {
                "name": "Inventario de Productos Terminados",
                "account_type": "asset_current",
                "reconcile": False,
            },
            "1030105": {
                "name": "Inventario de Suministros y Materiales",
                "account_type": "asset_current",
                "reconcile": False,
            },
            "1040101": {
                "name": "IVA Compras (Crédito Tributario)",
                "account_type": "asset_current",
                "reconcile": False,
            },
            "1040102": {
                "name": "Retención en la Fuente Renta (Crédito)",
                "account_type": "asset_current",
                "reconcile": False,
            },
            "1040103": {
                "name": "Retención IVA (Crédito)",
                "account_type": "asset_current",
                "reconcile": False,
            },
            "1040104": {
                "name": "ISD Crédito Tributario",
                "account_type": "asset_current",
                "reconcile": False,
            },
            "1040105": {
                "name": "Anticipo Impuesto a la Renta",
                "account_type": "asset_current",
                "reconcile": False,
            },
            "1050101": {
                "name": "Seguros Prepagados",
                "account_type": "asset_prepayments",
                "reconcile": False,
            },
            "1050102": {
                "name": "Arriendos Prepagados",
                "account_type": "asset_prepayments",
                "reconcile": False,
            },
            "1060101": {
                "name": "Terrenos",
                "account_type": "asset_non_current",
                "reconcile": False,
            },
            "1060201": {
                "name": "Edificios",
                "account_type": "asset_non_current",
                "reconcile": False,
            },
            "1060202": {
                "name": "Depreciación Acumulada Edificios",
                "account_type": "asset_non_current",
                "reconcile": False,
            },
            "1060301": {
                "name": "Muebles y Enseres",
                "account_type": "asset_non_current",
                "reconcile": False,
            },
            "1060302": {
                "name": "Depreciación Acumulada Muebles",
                "account_type": "asset_non_current",
                "reconcile": False,
            },
            "1060401": {
                "name": "Maquinaria y Equipo",
                "account_type": "asset_non_current",
                "reconcile": False,
            },
            "1060402": {
                "name": "Depreciación Acumulada Maquinaria",
                "account_type": "asset_non_current",
                "reconcile": False,
            },
            "1060501": {
                "name": "Vehículos",
                "account_type": "asset_non_current",
                "reconcile": False,
            },
            "1060502": {
                "name": "Depreciación Acumulada Vehículos",
                "account_type": "asset_non_current",
                "reconcile": False,
            },
            "1060601": {
                "name": "Equipos de Computación",
                "account_type": "asset_non_current",
                "reconcile": False,
            },
            "1060602": {
                "name": "Depreciación Acumulada Computación",
                "account_type": "asset_non_current",
                "reconcile": False,
            },
            "1070101": {
                "name": "Software y Licencias",
                "account_type": "asset_non_current",
                "reconcile": False,
            },
            "1070102": {
                "name": "Amortización Acumulada Software",
                "account_type": "asset_non_current",
                "reconcile": False,
            },
            "2010101": {
                "name": "Cuentas por Pagar Proveedores Relacionados",
                "account_type": "liability_payable",
                "reconcile": True,
            },
            "2010102": {
                "name": "Cuentas por Pagar Proveedores No Relacionados",
                "account_type": "liability_payable",
                "reconcile": True,
            },
            "2010201": {
                "name": "Obligaciones Bancarias CP",
                "account_type": "liability_current",
                "reconcile": False,
            },
            "2010301": {
                "name": "IESS Aporte Personal por Pagar",
                "account_type": "liability_current",
                "reconcile": False,
            },
            "2010302": {
                "name": "IESS Aporte Patronal por Pagar",
                "account_type": "liability_current",
                "reconcile": False,
            },
            "2010303": {
                "name": "IESS Préstamos Quirografarios",
                "account_type": "liability_current",
                "reconcile": False,
            },
            "2010304": {
                "name": "Décimo Tercer Sueldo por Pagar",
                "account_type": "liability_current",
                "reconcile": False,
            },
            "2010305": {
                "name": "Décimo Cuarto Sueldo por Pagar",
                "account_type": "liability_current",
                "reconcile": False,
            },
            "2010306": {
                "name": "Fondos de Reserva por Pagar",
                "account_type": "liability_current",
                "reconcile": False,
            },
            "2010307": {
                "name": "Vacaciones por Pagar",
                "account_type": "liability_current",
                "reconcile": False,
            },
            "2010308": {
                "name": "Participación Trabajadores por Pagar (15%)",
                "account_type": "liability_current",
                "reconcile": False,
            },
            "2010401": {
                "name": "IVA Ventas",
                "account_type": "liability_current",
                "reconcile": False,
            },
            "2010402": {
                "name": "Retención Fuente Renta por Pagar",
                "account_type": "liability_current",
                "reconcile": False,
            },
            "2010403": {
                "name": "Retención IVA por Pagar",
                "account_type": "liability_current",
                "reconcile": False,
            },
            "2010501": {
                "name": "Impuesto a la Renta por Pagar",
                "account_type": "liability_current",
                "reconcile": False,
            },
            "2020101": {
                "name": "Obligaciones Bancarias LP",
                "account_type": "liability_non_current",
                "reconcile": False,
            },
            "2020201": {
                "name": "Jubilación Patronal",
                "account_type": "liability_non_current",
                "reconcile": False,
            },
            "3010101": {
                "name": "Capital Social",
                "account_type": "equity",
                "reconcile": False,
            },
            "3010201": {
                "name": "Reserva Legal",
                "account_type": "equity",
                "reconcile": False,
            },
            "3010202": {
                "name": "Reserva Facultativa",
                "account_type": "equity",
                "reconcile": False,
            },
            "3010301": {
                "name": "Utilidad de Ejercicios Anteriores",
                "account_type": "equity",
                "reconcile": False,
            },
            "3010302": {
                "name": "Pérdida de Ejercicios Anteriores",
                "account_type": "equity",
                "reconcile": False,
            },
            "3010401": {
                "name": "Utilidad del Ejercicio",
                "account_type": "equity",
                "reconcile": False,
            },
            "3010402": {
                "name": "Pérdida del Ejercicio",
                "account_type": "equity",
                "reconcile": False,
            },
            "4010101": {
                "name": "Ventas Tarifa 15%",
                "account_type": "income",
                "reconcile": False,
            },
            "4010102": {
                "name": "Ventas Tarifa 0%",
                "account_type": "income",
                "reconcile": False,
            },
            "4010103": {
                "name": "Ventas Tarifa 5%",
                "account_type": "income",
                "reconcile": False,
            },
            "4010104": {
                "name": "Ventas Exentas",
                "account_type": "income",
                "reconcile": False,
            },
            "4010105": {
                "name": "Prestación de Servicios 15%",
                "account_type": "income",
                "reconcile": False,
            },
            "4010106": {
                "name": "Exportaciones",
                "account_type": "income",
                "reconcile": False,
            },
            "4010201": {
                "name": "Descuentos en Ventas",
                "account_type": "income",
                "reconcile": False,
            },
            "4010202": {
                "name": "Devoluciones en Ventas",
                "account_type": "income",
                "reconcile": False,
            },
            "4020101": {
                "name": "Intereses Ganados",
                "account_type": "income_other",
                "reconcile": False,
            },
            "4020102": {
                "name": "Otros Ingresos Operacionales",
                "account_type": "income_other",
                "reconcile": False,
            },
            "5010101": {
                "name": "Costo de Ventas",
                "account_type": "expense_direct_cost",
                "reconcile": False,
            },
            "5010102": {
                "name": "Costo de Producción",
                "account_type": "expense_direct_cost",
                "reconcile": False,
            },
            "5020101": {
                "name": "Sueldos y Salarios",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020102": {
                "name": "Horas Extras",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020103": {
                "name": "Comisiones",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020104": {
                "name": "Aporte Patronal IESS",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020105": {
                "name": "Décimo Tercer Sueldo",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020106": {
                "name": "Décimo Cuarto Sueldo",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020107": {
                "name": "Fondos de Reserva",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020108": {
                "name": "Vacaciones",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020109": {
                "name": "Indemnizaciones Laborales",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020110": {
                "name": "Alimentación Personal",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020111": {
                "name": "Transporte Personal",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020112": {
                "name": "Capacitación Personal",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020113": {
                "name": "Uniformes",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020201": {
                "name": "Arriendo Oficina",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020202": {
                "name": "Honorarios Profesionales",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020203": {
                "name": "Mantenimiento y Reparaciones",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020204": {
                "name": "Combustibles y Lubricantes",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020205": {
                "name": "Promoción y Publicidad",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020206": {
                "name": "Suministros de Oficina",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020207": {
                "name": "Seguros",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020208": {
                "name": "Comunicaciones (Internet/Teléfono)",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020209": {
                "name": "Servicios Básicos (Agua/Luz)",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020210": {
                "name": "Seguridad y Vigilancia",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020211": {
                "name": "Gastos de Viaje",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020212": {
                "name": "Notariales y Legales",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020213": {
                "name": "Impuestos y Contribuciones",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020214": {
                "name": "Depreciación Propiedad Planta y Equipo",
                "account_type": "expense_depreciation",
                "reconcile": False,
            },
            "5020215": {
                "name": "Amortización Intangibles",
                "account_type": "expense_depreciation",
                "reconcile": False,
            },
            "5020216": {
                "name": "Cuentas Incobrables",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020301": {
                "name": "Intereses Pagados",
                "account_type": "expense",
                "reconcile": False,
            },
            "5020302": {
                "name": "Comisiones Bancarias",
                "account_type": "expense",
                "reconcile": False,
            },
            "9010101": {
                "name": "Cuentas de Orden Deudoras",
                "account_type": "off_balance",
                "reconcile": False,
            },
            "9010102": {
                "name": "Cuentas de Orden Acreedoras",
                "account_type": "off_balance",
                "reconcile": False,
            },
        }
        return {
            f"account_{code}": {
                "code": code,
                **values,
            }
            for code, values in accounts.items()
        }

    @template("ec", "account.tax")
    def _get_ec_account_tax(self):
        taxes = {
            "tax_iva_15_sale": {
                "name": "IVA 15% (Ventas)",
                "amount": 15.0,
                "amount_type": "percent",
                "type_tax_use": "sale",
                "tax_group_id": "tax_group_iva",
                "invoice_repartition_line_ids": [("4010101", 0.0), ("2010401", 100.0)],
                "refund_repartition_line_ids": [("4010101", 0.0), ("2010401", 100.0)],
            },
            "tax_iva_15_purchase": {
                "name": "IVA 15% (Compras)",
                "amount": 15.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "tax_group_id": "tax_group_iva",
                "invoice_repartition_line_ids": [("1040101", 0.0), ("1040101", 100.0)],
                "refund_repartition_line_ids": [("1040101", 0.0), ("1040101", 100.0)],
            },
            "tax_iva_5_sale": {
                "name": "IVA 5% (Construcción Ventas)",
                "amount": 5.0,
                "amount_type": "percent",
                "type_tax_use": "sale",
                "tax_group_id": "tax_group_iva",
                "invoice_repartition_line_ids": [("4010103", 0.0), ("2010401", 100.0)],
                "refund_repartition_line_ids": [("4010103", 0.0), ("2010401", 100.0)],
            },
            "tax_iva_5_purchase": {
                "name": "IVA 5% (Construcción Compras)",
                "amount": 5.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "tax_group_id": "tax_group_iva",
                "invoice_repartition_line_ids": [("1040101", 0.0), ("1040101", 100.0)],
                "refund_repartition_line_ids": [("1040101", 0.0), ("1040101", 100.0)],
            },
            "tax_iva_0_sale": {
                "name": "IVA 0% (Ventas)",
                "amount": 0.0,
                "amount_type": "percent",
                "type_tax_use": "sale",
                "tax_group_id": "tax_group_iva",
            },
            "tax_iva_0_purchase": {
                "name": "IVA 0% (Compras)",
                "amount": 0.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "tax_group_id": "tax_group_iva",
            },
            "tax_iva_exento_sale": {
                "name": "IVA Exento (Ventas)",
                "amount": 0.0,
                "amount_type": "percent",
                "type_tax_use": "sale",
                "tax_group_id": "tax_group_iva",
            },
            "tax_iva_exento_purchase": {
                "name": "IVA Exento (Compras)",
                "amount": 0.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "tax_group_id": "tax_group_iva",
            },
            "tax_iva_no_objeto_sale": {
                "name": "No Objeto de IVA (Ventas)",
                "amount": 0.0,
                "amount_type": "percent",
                "type_tax_use": "sale",
                "tax_group_id": "tax_group_iva",
            },
            "tax_iva_no_objeto_purchase": {
                "name": "No Objeto de IVA (Compras)",
                "amount": 0.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "tax_group_id": "tax_group_iva",
            },
            "tax_ret_ir_303": {
                "name": "Retención IR 10% (Honorarios)",
                "amount": -10.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "tax_group_id": "tax_group_ret_renta",
                "invoice_repartition_line_ids": [("2010402", 0.0), ("2010402", 100.0)],
                "refund_repartition_line_ids": [("2010402", 0.0), ("2010402", 100.0)],
            },
            "tax_ret_ir_304": {
                "name": "Retención IR 8% (Serv. Profesional)",
                "amount": -8.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "tax_group_id": "tax_group_ret_renta",
                "invoice_repartition_line_ids": [("2010402", 0.0), ("2010402", 100.0)],
                "refund_repartition_line_ids": [("2010402", 0.0), ("2010402", 100.0)],
            },
            "tax_ret_ir_307": {
                "name": "Retención IR 2% (Servicios/Bienes)",
                "amount": -2.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "tax_group_id": "tax_group_ret_renta",
                "invoice_repartition_line_ids": [("2010402", 0.0), ("2010402", 100.0)],
                "refund_repartition_line_ids": [("2010402", 0.0), ("2010402", 100.0)],
            },
            "tax_ret_ir_312": {
                "name": "Retención IR 1.75% (Bienes Muebles)",
                "amount": -1.75,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "tax_group_id": "tax_group_ret_renta",
                "invoice_repartition_line_ids": [("2010402", 0.0), ("2010402", 100.0)],
                "refund_repartition_line_ids": [("2010402", 0.0), ("2010402", 100.0)],
            },
            "tax_ret_ir_320": {
                "name": "Retención IR 2.75% (Inmuebles)",
                "amount": -2.75,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "tax_group_id": "tax_group_ret_renta",
                "invoice_repartition_line_ids": [("2010402", 0.0), ("2010402", 100.0)],
                "refund_repartition_line_ids": [("2010402", 0.0), ("2010402", 100.0)],
            },
            "tax_ret_ir_322": {
                "name": "Retención IR 1% (Seguros)",
                "amount": -1.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "tax_group_id": "tax_group_ret_renta",
                "invoice_repartition_line_ids": [("2010402", 0.0), ("2010402", 100.0)],
                "refund_repartition_line_ids": [("2010402", 0.0), ("2010402", 100.0)],
            },
            "tax_ret_ir_344": {
                "name": "Retención IR 1% (Transporte)",
                "amount": -1.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "tax_group_id": "tax_group_ret_renta",
                "invoice_repartition_line_ids": [("2010402", 0.0), ("2010402", 100.0)],
                "refund_repartition_line_ids": [("2010402", 0.0), ("2010402", 100.0)],
            },
            "tax_ret_iva_10": {
                "name": "Retención IVA 10% (Bienes)",
                "amount": -10.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "tax_group_id": "tax_group_ret_iva",
                "invoice_repartition_line_ids": [("2010403", 0.0), ("2010403", 100.0)],
                "refund_repartition_line_ids": [("2010403", 0.0), ("2010403", 100.0)],
            },
            "tax_ret_iva_20": {
                "name": "Retención IVA 20% (Servicios)",
                "amount": -20.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "tax_group_id": "tax_group_ret_iva",
                "invoice_repartition_line_ids": [("2010403", 0.0), ("2010403", 100.0)],
                "refund_repartition_line_ids": [("2010403", 0.0), ("2010403", 100.0)],
            },
            "tax_ret_iva_30": {
                "name": "Retención IVA 30% (Bienes CE)",
                "amount": -30.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "tax_group_id": "tax_group_ret_iva",
                "invoice_repartition_line_ids": [("2010403", 0.0), ("2010403", 100.0)],
                "refund_repartition_line_ids": [("2010403", 0.0), ("2010403", 100.0)],
            },
            "tax_ret_iva_50": {
                "name": "Retención IVA 50%",
                "amount": -50.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "tax_group_id": "tax_group_ret_iva",
                "invoice_repartition_line_ids": [("2010403", 0.0), ("2010403", 100.0)],
                "refund_repartition_line_ids": [("2010403", 0.0), ("2010403", 100.0)],
            },
            "tax_ret_iva_70": {
                "name": "Retención IVA 70% (Servicios CE)",
                "amount": -70.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "tax_group_id": "tax_group_ret_iva",
                "invoice_repartition_line_ids": [("2010403", 0.0), ("2010403", 100.0)],
                "refund_repartition_line_ids": [("2010403", 0.0), ("2010403", 100.0)],
            },
            "tax_ret_iva_100": {
                "name": "Retención IVA 100%",
                "amount": -100.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "tax_group_id": "tax_group_ret_iva",
                "invoice_repartition_line_ids": [("2010403", 0.0), ("2010403", 100.0)],
                "refund_repartition_line_ids": [("2010403", 0.0), ("2010403", 100.0)],
            },
            "tax_ice_generic": {
                "name": "ICE (Genérico)",
                "amount": 0.0,
                "amount_type": "percent",
                "type_tax_use": "sale",
                "tax_group_id": "tax_group_ice",
            },
            # =========================================================================
            # DIVIDEND WITHHOLDING TAXES (2026 Regulation)
            # Aplicable a distribución de dividendos
            # =========================================================================
            "tax_ret_div_10": {
                "name": "Retención Dividendos 10% (No Residentes)",
                "amount": -10.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "tax_group_id": "tax_group_ret_renta",
                "invoice_repartition_line_ids": [("2010402", 0.0), ("2010402", 100.0)],
                "refund_repartition_line_ids": [("2010402", 0.0), ("2010402", 100.0)],
            },
            "tax_ret_div_12": {
                "name": "Retención Dividendos 12% (Residentes)",
                "amount": -12.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "tax_group_id": "tax_group_ret_renta",
                "invoice_repartition_line_ids": [("2010402", 0.0), ("2010402", 100.0)],
                "refund_repartition_line_ids": [("2010402", 0.0), ("2010402", 100.0)],
            },
            "tax_ret_div_14": {
                "name": "Retención Dividendos 14% (Paraísos Fiscales)",
                "amount": -14.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "tax_group_id": "tax_group_ret_renta",
                "invoice_repartition_line_ids": [("2010402", 0.0), ("2010402", 100.0)],
                "refund_repartition_line_ids": [("2010402", 0.0), ("2010402", 100.0)],
            },
        }

        def repartition_lines(account_code=None):
            tax_line = {
                "repartition_type": "tax",
                "factor_percent": 100,
            }
            if account_code:
                tax_line["account_id"] = f"account_{account_code}"
            return [
                Command.create({
                    "repartition_type": "base",
                    "factor_percent": 100,
                }),
                Command.create(tax_line),
            ]

        for values in taxes.values():
            for field_name in ("invoice_repartition_line_ids", "refund_repartition_line_ids"):
                lines = values.get(field_name)
                if lines and isinstance(lines[0], tuple):
                    values[field_name] = repartition_lines(lines[1][0])
                elif not lines:
                    values[field_name] = repartition_lines()

        return taxes

    @template("ec", "account.tax.group")
    def _get_ec_account_tax_group(self):
        return {
            "tax_group_iva": {"name": "IVA", "sequence": 1},
            "tax_group_ret_renta": {"name": "Retención Renta", "sequence": 2},
            "tax_group_ret_iva": {"name": "Retención IVA", "sequence": 3},
            "tax_group_ice": {"name": "ICE", "sequence": 4},
        }
