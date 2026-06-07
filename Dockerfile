FROM odoo:18.0

USER root

# Dependencias del sistema para XAdES-BES (l10n_ec_sri) y SOAP (l10n_ec_edi)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Dependencias Python requeridas por los módulos personalizados:
#   zeep          → l10n_ec_edi (cliente SOAP para SRI)
#   cryptography  → l10n_ec_sri (firma XAdES-BES, RSA-2048)
#   lxml          → generación y validación de XML SRI
RUN pip3 install --no-cache-dir \
    zeep==4.2.1 \
    cryptography==42.0.8 \
    lxml==5.2.2

# Copiar addons personalizados (excluye das_tareas_prueba en prod via .dockerignore)
COPY addons/ /mnt/extra-addons/

RUN chown -R odoo:odoo /mnt/extra-addons

USER odoo

EXPOSE 8069 8072
