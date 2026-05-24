# -*- coding: utf-8 -*-
from odoo import fields, models


class DasEmailInterest(models.Model):
    _name = 'das.email.interest'
    _description = 'Interés / gusto del usuario (Email Marketing)'
    _order = 'sequence, name'

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    color = fields.Integer(string='Color índice')
    description = fields.Text(translate=True)
