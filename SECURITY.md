# 🛡️ Política de Seguridad (SECURITY.md)

En el proyecto **Odoo-DAS**, nos tomamos muy en serio la protección de los datos de nuestros estudiantes, desarrolladores y la integridad criptográfica de las transacciones fiscales con el SRI.

---

## 🔒 Medidas de Seguridad Implementadas

1.  **Protección de Datos en Onboarding**:
    Las preferencias e información de cumpleaños recopiladas a través de `das_email_preferences` se almacenan bajo controles de acceso restringidos en la base de datos de Odoo. Solo los administradores con privilegios de marketing tienen visibilidad sobre estas preferencias.
2.  **Criptografía y Firma Electrónica**:
    Las firmas digitales XAdES-BES se generan localmente en el servidor (`l10n_ec_sri`) utilizando criptografía de clave pública de alto rendimiento. Las claves privadas contenidas en los certificados `.p12` se desencriptan en memoria de forma temporal y sus contraseñas deben ser almacenadas de manera cifrada en la base de datos de Odoo o mediante variables de entorno en producción.
3.  **Aislamiento en Docker**:
    El despliegue con Docker aísla el servidor de base de datos PostgreSQL de la red externa, permitiendo conexiones únicamente desde el contenedor de Odoo para evitar fugas de información.

---

## 🚨 Reporte de Vulnerabilidades

Si descubres algún fallo de seguridad, por favor **no abras un issue público en GitHub**. En su lugar, envía un reporte por correo electrónico a los encargados del proyecto detallando:
*   El módulo y el archivo afectado.
*   Los pasos detallados para reproducir la vulnerabilidad.
*   Un ejemplo o prueba de concepto si es posible.

---

## 🔄 Parches de Seguridad
Las correcciones de seguridad se realizarán de manera prioritaria y se publicarán directamente en la rama principal (`main`) detallando la corrección en los releases del proyecto.
