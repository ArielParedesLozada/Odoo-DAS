# -*- coding: utf-8 -*-
import base64
import logging
import os
import re

from odoo.tools.image import image_process

_logger = logging.getLogger(__name__)

LOGO_XML_ID = 'das_email_campaigns.das_email_logo_attachment'
LOGO_CID = 'das_email_logo@academia'
LOGO_CID_SRC = 'cid:%s' % LOGO_CID


def _logo_source_path():
    import odoo.addons.das_email_preferences as pref_mod
    return os.path.join(
        os.path.dirname(pref_mod.__file__),
        'static', 'src', 'img', 'Logo.png',
    )


def das_email_logo_bytes(env):
    """PNG optimizado del logo para adjuntar inline en cada correo."""
    logo_path = _logo_source_path()
    if not os.path.isfile(logo_path):
        _logger.warning('DAS email: no se encontró Logo.png en %s', logo_path)
        return b''
    with open(logo_path, 'rb') as logo_file:
        raw = logo_file.read()
    return image_process(raw, size=(280, 0), quality=85) or raw


def das_email_ensure_logo_attachment(env):
    """Adjunto público del logo (vista previa web / respaldo)."""
    Attachment = env['ir.attachment'].sudo()
    att = env.ref(LOGO_XML_ID, raise_if_not_found=False)
    logo_bytes = das_email_logo_bytes(env)
    if not logo_bytes:
        return att
    data = base64.b64encode(logo_bytes).decode()
    vals = {
        'name': 'das_email_logo.png',
        'type': 'binary',
        'datas': data,
        'mimetype': 'image/png',
        'public': True,
    }
    if att:
        att.write(vals)
    else:
        att = Attachment.create(vals)
        env['ir.model.data'].sudo().create({
            'name': 'das_email_logo_attachment',
            'model': 'ir.attachment',
            'module': 'das_email_campaigns',
            'res_id': att.id,
            'noupdate': True,
        })
    return att


def das_email_logo_src(env):
    """Referencia CID: el binario se adjunta al enviar cada mail.mail."""
    return LOGO_CID_SRC


def das_email_logo_attachment_tuple(env):
    """Tupla para ir.mail_server.build_email con Content-ID inline."""
    logo_bytes = das_email_logo_bytes(env)
    if not logo_bytes:
        return None
    return ('das_email_logo.png', logo_bytes, 'image/png', LOGO_CID)


def das_email_body_with_cid_logo(body):
    """Fuerza src CID en la etiqueta del logo DAS (src/alt en cualquier orden)."""
    if not body:
        return body

    def _replace_logo_src(match):
        tag = match.group(0)
        if LOGO_CID_SRC in tag:
            return tag
        return re.sub(r'src="[^"]*"', 'src="%s"' % LOGO_CID_SRC, tag, count=1)

    return re.sub(
        r'<img[^>]*alt="Academia Virtual DAS"[^>]*/?>',
        _replace_logo_src,
        body,
        count=1,
    )


def das_email_qwebify_body(body):
    """Convierte placeholders antiguos {{ object.x }} a sintaxis QWeb de Odoo 18."""
    if not body:
        return body
    return re.sub(
        r'\{\{\s*object\.(\w+)\s*\}\}',
        r'<t t-out="object.\1"/>',
        body,
    )


# Compatibilidad con código anterior
def das_email_refresh_logo_data_uri(env):
    das_email_ensure_logo_attachment(env)
    return LOGO_CID_SRC


def das_email_logo_data_uri(env):
    return LOGO_CID_SRC


def das_email_body_with_embedded_logo(env, body):
    return das_email_body_with_cid_logo(body)
