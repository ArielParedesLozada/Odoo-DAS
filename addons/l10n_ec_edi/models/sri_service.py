# -*- coding: utf-8 -*-
from odoo import models, _
from odoo.exceptions import UserError
import logging
from xml.sax.saxutils import escape

# Trusted External Libs
try:
    from zeep import Client, Settings
    from zeep.transports import Transport
    from zeep.exceptions import Fault
    import requests
except ImportError:
    logging.getLogger(__name__).warning("Zeep library not installed")

_logger = logging.getLogger(__name__)


class SriService(models.AbstractModel):
    _name = "l10n_ec.sri.service"
    _description = "SRI SOAP Web Service Client"

    def _get_client(self, url):
        """
        Factory method to create a Zeep Client with proper timeouts and settings.
        """
        try:
            settings = Settings(strict=False, xml_huge_tree=True)
            transport = Transport(timeout=30, operation_timeout=30)
            return Client(wsdl=url, settings=settings, transport=transport)
        except Exception as e:
            raise UserError(
                _("Could not connect to SRI WSDL at %s. Error: %s") % (url, str(e))
            )

    def send_document(self, signed_xml_bytes, environment="1"):
        """
        Send signed XML to SRI 'Recepcion' service.
        :param signed_xml_bytes: The XAdES-BES signed XML (bytes)
        :param environment: '1' (Test) or '2' (Prod)
        :return: Dict {status, message, details}
        """
        company = self.env.company
        url = company.l10n_ec_sri_reception_url

        client = self._get_client(url)

        try:
            # SRI expects the XML content as a byte array (base64 encoded automatically by Zeep usually,
            # but SRI WSDL defines it as base64Binary).
            response = client.service.validarComprobante(xml=signed_xml_bytes)

            # Parse Response
            state = response.estado  # 'RECIBIDA' or 'DEVUELTA'

            result = {"status": state, "messages": []}

            if state == "DEVUELTA":
                # Extract error messages
                if hasattr(response, "comprobantes") and response.comprobantes:
                    for comp in response.comprobantes.comprobante:
                        for msg in comp.mensajes.mensaje:
                            result["messages"].append(
                                f"{msg.identificador}: {msg.mensaje} - {msg.informacionAdicional or ''}"
                            )

            return result

        except Fault as e:
            return {"status": "ERROR", "messages": [f"SOAP Fault: {str(e)}"]}
        except Exception as e:
            _logger.exception("SRI Connection Error")
            return {"status": "ERROR", "messages": [f"Connection Fail: {str(e)}"]}

    def check_authorization(self, access_key):
        """
        Check authorization status in SRI 'Autorizacion' service.
        :param access_key: 49-digit key
        :return: Dict {status, date, xml}
        """
        company = self.env.company
        url = company.l10n_ec_sri_authorization_url

        client = self._get_client(url)

        try:
            # NOTE: Parameter is 'claveAccesoComprobante' NOT 'claveAcceso'
            # Discovered via E2E testing against real SRI WSDL
            response = client.service.autorizacionComprobante(
                claveAccesoComprobante=access_key
            )

            # SRI returns a list of authorizations (usually 1)
            if not response.autorizaciones or not response.autorizaciones.autorizacion:
                return {
                    "status": "PENDING",
                    "messages": ["No matching authorization found yet."],
                }

            auth = response.autorizaciones.autorizacion[0]
            state = auth.estado  # 'AUTORIZADO', 'NO AUTORIZADO', 'EN PROCESO'

            result = {
                "status": state,
                "date": auth.fechaAutorizacion,  # Check if this is datetime or str
                "xml": auth.comprobante,  # The authorized XML (with authorization tag)
                "authorized_xml": self._build_authorized_xml(auth),
                "messages": [],
            }

            if state != "AUTORIZADO" and getattr(auth, "mensajes", None):
                for msg in auth.mensajes.mensaje:
                    result["messages"].append(
                        f"{msg.mensaje} - {msg.informacionAdicional or ''}"
                    )

            return result

        except Exception as e:
            return {"status": "ERROR", "messages": [f"Connection Fail: {str(e)}"]}

    def _build_authorized_xml(self, authorization):
        date_value = authorization.fechaAutorizacion or ""
        if hasattr(date_value, "isoformat"):
            date_value = date_value.isoformat()
        comprobante = authorization.comprobante or ""
        comprobante = comprobante.replace("]]>", "]]]]><![CDATA[>")
        return (
            '<?xml version="1.0" encoding="UTF-8"?>'
            "<autorizacion>"
            f"<estado>{escape(str(authorization.estado or ''))}</estado>"
            f"<numeroAutorizacion>{escape(str(authorization.numeroAutorizacion or ''))}</numeroAutorizacion>"
            f"<fechaAutorizacion>{escape(str(date_value))}</fechaAutorizacion>"
            "<comprobante><![CDATA["
            f"{comprobante}"
            "]]></comprobante>"
            "</autorizacion>"
        )
