FROM odoo:18.0

# ── Dependencias Python ──────────────────────────────────────
# La imagen base odoo:18.0 (Debian Trixie/Sid, Python 3.12) ya incluye
# via apt-get todas las dependencias requeridas por los módulos l10n_ec_*:
#
#   lxml         5.2.1   → sri_signer.py (XAdES-BES XML tree, C14N)
#   cryptography 41.0.7  → sri_signer.py, l10n_ec_certificate.py (PKCS12, RSA)
#   zeep         4.2.1   → sri_service.py (cliente SOAP SRI)
#   requests     *       → sri_service.py (transporte HTTP de zeep)
#   markupsafe   *       → das_lms, das_email_campaigns (Jinja2 markup)
#
# NO se instalan con pip3 por dos razones:
#   1. PEP 668: Debian Trixie marca el entorno como EXTERNALLY-MANAGED,
#      pip rechaza instalar sin --break-system-packages.
#   2. Son innecesarias: ya están disponibles en el intérprete del sistema.

USER root

# Dependencias del sistema para compilación de extensiones C (por si algún
# paquete futuro las requiere) y curl para los health checks del compose.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Addons personalizados ────────────────────────────────────
# das_tareas_prueba se excluye via .dockerignore (módulo de prueba, no va a prod)
COPY addons/ /mnt/extra-addons/

RUN chown -R odoo:odoo /mnt/extra-addons

USER odoo

EXPOSE 8069 8072
