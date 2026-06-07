# -*- coding: utf-8 -*-
from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _das_lms_is_academic_student_partner(self):
        """Alumno DAS: contacto sin usuario interno (share=False).

        Válido si no tiene usuarios o solo usuarios portal/compartidos.
        Excluye administradores, instructores, coordinadores y demás internos.
        """
        self.ensure_one()
        return not self.user_ids.filtered(lambda user: not user.share)
