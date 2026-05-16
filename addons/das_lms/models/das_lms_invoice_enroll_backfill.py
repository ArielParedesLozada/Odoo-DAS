# -*- coding: utf-8 -*-
from odoo import models


class DasLmsInvoiceEnrollBackfill(models.TransientModel):
    _name = 'das.lms.invoice.enroll.backfill'
    _description = 'Reparar inscripciones LMS desde facturas cliente publicadas'

    def action_execute(self):
        self.ensure_one()
        return self.env['account.move'].das_lms_action_backfill_enrollments_from_posted_invoices()
