# -*- coding: utf-8 -*-
from odoo import _, fields, models


class DasLmsLinkAuditLine(models.TransientModel):
    _name = 'das.lms.link.audit.line'
    _description = 'Línea de auditoría producto ↔ curso DAS LMS'

    wizard_id = fields.Many2one('das.lms.link.audit.wizard', required=True, ondelete='cascade')
    severity = fields.Selection(
        [('info', 'Información'), ('warning', 'Advertencia'), ('error', 'Error')],
        required=True,
        default='warning',
    )
    issue_type = fields.Char(string='Tipo', required=True)
    description = fields.Text(string='Descripción')
    product_template_id = fields.Many2one('product.template', string='Producto')
    slide_channel_id = fields.Many2one('slide.channel', string='Curso')


class DasLmsLinkAuditWizard(models.TransientModel):
    _name = 'das.lms.link.audit.wizard'
    _description = 'Validar vínculos producto-curso'

    line_ids = fields.One2many('das.lms.link.audit.line', 'wizard_id', string='Hallazgos')

    def action_run_audit(self):
        self.ensure_one()
        Channel = self.env['slide.channel'].sudo()
        Product = self.env['product.template'].sudo()
        lines_commands = []

        def add(level, issue_type, desc, tmpl=None, channel=None):
            lines_commands.append(
                (
                    0,
                    0,
                    {
                        'severity': level,
                        'issue_type': issue_type,
                        'description': desc,
                        'product_template_id': tmpl.id if tmpl else False,
                        'slide_channel_id': channel.id if channel else False,
                    },
                )
            )

        for ch in Channel.search([('product_id', '=', False)]):
            add(
                'warning',
                'canal_sin_producto',
                _('Canal sin «Producto» de tienda (product_id vacío).'),
                channel=ch,
            )

        variant_to_channels = {}
        for ch in Channel.search([('product_id', '!=', False)]):
            variant_to_channels.setdefault(ch.product_id.id, []).append(ch)

        for variant_id, ch_list in variant_to_channels.items():
            variant = self.env['product.product'].browse(variant_id).exists()
            if not variant:
                continue
            tmpl = variant.product_tmpl_id
            if tmpl.das_lms_channel_id and tmpl.das_lms_channel_id.id not in {c.id for c in ch_list}:
                add(
                    'error',
                    'explicito_distinto_variante_canal',
                    _(
                        'El producto «%s» fija explícitamente «%s», pero otros canales usan esta variante («%s»).'
                    )
                    % (
                        tmpl.display_name,
                        tmpl.das_lms_channel_id.display_name,
                        ', '.join(c.display_name for c in ch_list),
                    ),
                    tmpl=tmpl,
                    channel=ch_list[0],
                )
            if len(ch_list) > 1 and not tmpl.das_lms_channel_id:
                names = ', '.join(c.display_name for c in ch_list)
                add(
                    'warning',
                    'canales_ambiguos',
                    _(
                        'Varios canales enlazan la variante «%s»: %s. Indique '
                        '«Curso eLearning relacionado» en la plantilla «%s».'
                    )
                    % (variant.display_name, names, tmpl.display_name),
                    tmpl=tmpl,
                    channel=ch_list[0],
                )

        for tmpl in Product.search([]):
            if not tmpl.product_variant_ids:
                continue
            variant_ids = tmpl.product_variant_ids.ids
            auto_count = Channel.search_count([('product_id', 'in', variant_ids)])
            explicit = tmpl.das_lms_channel_id
            if auto_count > 1 and not explicit:
                add(
                    'warning',
                    'plantilla_sin_enlace_explicito_ambiguo',
                    _(
                        'La plantilla «%s» tiene %s canales con sus variantes. Defina '
                        '«Curso eLearning relacionado» (variantes ids: %s).'
                    )
                    % (
                        tmpl.display_name,
                        auto_count,
                        ', '.join(str(v) for v in variant_ids),
                    ),
                    tmpl=tmpl,
                )

            if auto_count == 0 and explicit:
                if explicit.product_id and explicit.product_id.id not in variant_ids:
                    add(
                        'warning',
                        'explicito_sin_variante_coincidente',
                        _(
                            'La plantilla «%s» apunta explícitamente a «%s», cuyo producto Odoo '
                            'no es una variante de esta plantilla.'
                        )
                        % (tmpl.display_name, explicit.display_name),
                        tmpl=tmpl,
                        channel=explicit,
                    )

        for tmpl in Product.search([('sale_ok', '=', True), ('website_published', '=', True)]):
            if not tmpl.product_variant_ids:
                continue
            if not tmpl._das_lms_get_related_channel():
                add(
                    'info',
                    'publicado_sin_curso_resuelto',
                    _(
                        'Producto «%s» publicado en web sin curso resoluble '
                        '(sin «Curso eLearning relacionado» ni canal con product_id en variantes).'
                    )
                    % (tmpl.display_name,),
                    tmpl=tmpl,
                )

        self.line_ids.unlink()
        self.line_ids = lines_commands
        return True
