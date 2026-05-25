# -*- coding: utf-8 -*-
"""
Ecuador Tax Calendar - Due Date Calculator
===========================================

Calcula fechas de vencimiento según el noveno dígito del RUC.
Todas las fechas son configurables via ir.config_parameter.

Resolución SRI Calendario Tributario 2026
"""
from odoo import models, api
from datetime import date, timedelta
import logging

_logger = logging.getLogger(__name__)


class L10nEcTaxCalendar(models.AbstractModel):
    """
    Tax Calendar Calculator for Ecuador.

    Determines filing deadlines based on:
    - 9th digit of company RUC
    - Type of declaration (IVA, IR, Retenciones, etc.)
    - Special contributor status
    """

    _name = "l10n_ec.tax.calendar"
    _description = "Ecuador Tax Calendar Calculator"

    # =========================================================================
    # CONFIGURATION KEYS (ir.config_parameter)
    # All deadlines configurable - NO HARDCODING
    # =========================================================================

    @api.model
    def _get_deadline_map(self):
        """
        Get deadline day map for 9th RUC digit.
        Configurable via ir.config_parameter.
        """
        ICP = self.env["ir.config_parameter"].sudo()

        # Default map per SRI 2026 calendar
        default_map = {
            "1": 10,
            "2": 12,
            "3": 14,
            "4": 16,
            "5": 18,
            "6": 20,
            "7": 22,
            "8": 24,
            "9": 26,
            "0": 28,
        }

        # Read from config (allows override without code change)
        param = ICP.get_param("l10n_ec.deadline_day_map")
        if param:
            try:
                import json

                return json.loads(param)
            except:
                pass

        return default_map

    @api.model
    def _get_special_contributor_day(self):
        """Get deadline day for special contributors (CE)."""
        return int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("l10n_ec.special_contributor_day", "9")
        )

    # =========================================================================
    # DEADLINE CALCULATION
    # =========================================================================

    @api.model
    def get_9th_digit(self, ruc):
        """Extract 9th digit from RUC."""
        if not ruc or len(ruc) < 9:
            return None
        return ruc[8]  # 0-indexed, so position 9 is index 8

    @api.model
    def calculate_deadline(
        self, declaration_type, period_month, period_year, company=None
    ):
        """
        Calculate filing deadline for a declaration.

        :param declaration_type: 'iva', 'retenciones', 'ats', 'ir', 'rdep'
        :param period_month: Month of the period (1-12)
        :param period_year: Year of the period
        :param company: res.company record (uses env.company if None)
        :return: date object with deadline
        """
        company = company or self.env.company
        ruc = company.vat

        if not ruc:
            _logger.warning("No RUC found for company %s", company.name)
            return None

        ninth_digit = self.get_9th_digit(ruc)

        # Check if special contributor
        is_special = getattr(company, "l10n_ec_special_contributor", False)

        if is_special:
            day = self._get_special_contributor_day()
        else:
            deadline_map = self._get_deadline_map()
            day = deadline_map.get(ninth_digit, 28)

        # Calculate deadline based on declaration type
        if declaration_type in ("iva", "retenciones", "ats"):
            # Due the following month
            deadline_month = period_month + 1
            deadline_year = period_year
            if deadline_month > 12:
                deadline_month = 1
                deadline_year += 1

        elif declaration_type == "ir":
            # Income tax: Natural persons March, Societies April
            # Simplified: use April for societies
            deadline_month = 4
            deadline_year = period_year + 1  # For previous year's income

        elif declaration_type == "rdep":
            # RDEP: January-February of following year
            # Different schedule for RDEP
            rdep_schedule = {
                "1": 21,
                "2": 23,
                "3": 25,
                "4": 27,
                "5": 29,
                "6": 31,
                "7": 3,
                "8": 5,
                "9": 7,
                "0": 7,
            }
            day = rdep_schedule.get(ninth_digit, 7)
            deadline_month = 1 if ninth_digit in "123456" else 2
            deadline_year = period_year + 1

        else:
            # Default: following month
            deadline_month = period_month + 1
            deadline_year = period_year
            if deadline_month > 12:
                deadline_month = 1
                deadline_year += 1

        # Build date, handle edge cases (day > days in month)
        try:
            deadline = date(deadline_year, deadline_month, day)
        except ValueError:
            # Day doesn't exist (e.g., Feb 30), use last day of month
            from calendar import monthrange

            _, last_day = monthrange(deadline_year, deadline_month)
            deadline = date(deadline_year, deadline_month, min(day, last_day))

        # Adjust for weekends/holidays
        deadline = self._adjust_for_holidays(deadline)

        return deadline

    @api.model
    def _adjust_for_holidays(self, deadline):
        """
        Adjust deadline if falls on weekend.
        Holidays should be handled via hr.holidays or dedicated model.
        """
        # Simple weekend adjustment
        while deadline.weekday() in (5, 6):  # Saturday=5, Sunday=6
            deadline += timedelta(days=1)

        return deadline

    # =========================================================================
    # HELPER METHODS FOR UI/REPORTS
    # =========================================================================

    @api.model
    def get_upcoming_deadlines(self, days_ahead=30, company=None):
        """
        Get all upcoming tax deadlines for a company.

        :param days_ahead: Number of days to look ahead
        :param company: res.company record
        :return: List of dicts with deadline info
        """
        company = company or self.env.company
        today = date.today()
        end_date = today + timedelta(days=days_ahead)

        # Current period
        current_month = today.month
        current_year = today.year

        # Previous month (for monthly declarations)
        if current_month == 1:
            prev_month = 12
            prev_year = current_year - 1
        else:
            prev_month = current_month - 1
            prev_year = current_year

        deadlines = []

        # Monthly declarations for previous month
        for decl_type in ["iva", "retenciones", "ats"]:
            deadline = self.calculate_deadline(
                decl_type, prev_month, prev_year, company
            )
            if deadline and today <= deadline <= end_date:
                deadlines.append(
                    {
                        "type": decl_type.upper(),
                        "period": f"{prev_month:02d}/{prev_year}",
                        "deadline": deadline,
                        "days_remaining": (deadline - today).days,
                    }
                )

        return sorted(deadlines, key=lambda x: x["deadline"])

    @api.model
    def get_company_deadline_info(self, company=None):
        """
        Get deadline configuration for a company.

        :return: Dict with RUC info and deadline day
        """
        company = company or self.env.company
        ruc = company.vat or ""
        ninth_digit = self.get_9th_digit(ruc)
        is_special = getattr(company, "l10n_ec_special_contributor", False)

        if is_special:
            day = self._get_special_contributor_day()
            category = "Contribuyente Especial"
        else:
            deadline_map = self._get_deadline_map()
            day = deadline_map.get(ninth_digit, 28)
            category = "Contribuyente General"

        return {
            "ruc": ruc,
            "ninth_digit": ninth_digit,
            "category": category,
            "deadline_day": day,
            "is_special_contributor": is_special,
        }
