import odoo
from odoo.tools import config

config.parse_config(['-c', '/etc/odoo/odoo.conf', '-d', 'odoo_academia'])
registry = odoo.registry('odoo_academia')
cr = registry.cursor()
env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})

tmpl = env.ref('das_email_campaigns.mail_template_das_list_interest')
body = tmpl.body_html or ''
idx = body.find('object')
print('SNIPPET:', body[max(0, idx - 20):idx + 40])
print('BASE URL:', env['ir.config_parameter'].sudo().get_param('web.base.url'))

# Test render with a mailing contact
contact = env['mailing.contact'].search([], limit=1)
if contact:
    rendered = env['mail.render.mixin']._render_template(
        body, 'mailing.contact', contact.ids, engine='inline_template',
    )
    print('CONTACT:', contact.name)
    print('RENDERED SNIPPET:', rendered[contact.id][rendered[contact.id].find('Hola'):rendered[contact.id].find('Hola')+80])

cr.close()
