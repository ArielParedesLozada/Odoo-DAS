# 📝 Historial de Versiones (Changelog) - Academia Virtual de Tecnología

Este registro detalla el historial de lanzamientos, adiciones funcionales, correcciones técnicas y adaptaciones del ERP para la **Academia Virtual de Tecnología** (Odoo-DAS v18.0).

---

## [18.0.4.33.0] - 2026-05-29 (Sprint LMS y Reglas de Control Académico)

### 🎯 Objetivos de la Versión
Optimizar el portal del estudiante y asegurar la integridad de la facturación en el eCommerce implementando restricciones de compra.

### Añadido
*   **das_lms**: Campo de modalidad de curso académica (`das_modality`) que mapea y traduce términos de base de datos a etiquetas amigables en el sitio web:
    *   `grabado` ──► **Virtual**
    *   `en_vivo` ──► **Presencial**
    *   `mixto` ──► **Híbrido**
*   **Restricciones de Carrito LMS (`sale.order` & `sale.order.line`)**:
    *   Lógica restrictiva que evalúa la adición de productos de tipo curso. Si el usuario intenta agregar un segundo curso LMS al carrito, se lanza un `UserError` de Odoo bloqueando el botón y la petición HTTP.
    *   Lógica restrictiva en el modelo de línea de venta para congelar la cantidad de compra en un máximo de una unidad (`product_uom_qty = 1`). Cualquier intento de alteración manual a través de la interfaz web arroja una excepción académica.
*   **Gestión de Acceso Temporizado**:
    *   Incorporación de la restricción de visibilidad de lecciones para cursos en estado "Próximo". La membresía se mantiene activa (`joined`) pero el botón de ingreso y las rutas internas de lectura devuelven error hasta que se cumpla la fecha de vigencia (`das_start_date`).
*   **Asistente de Sincronización Retroactiva (`das_lms_invoice_backfill_wizard`)**:
    *   Herramienta administrativa para realizar el backfill de matrículas en bloque. Asocia estudiantes históricos registrados como miembros con facturas reales que no activaron el webhook en Odoo debido a interrupciones en la pasarela.

### Corregido
*   Alineación de la vista de producto en la tienda web con el campo `is_member` del e-Learning nativo, evitando llamadas paralelas a SQL y mejorando el rendimiento de carga del catálogo.

---

## [18.0.2.3.0] - 2026-05-25 (Sprint Onboarding y Preferencias del Estudiante)

### 🎯 Objetivos de la Versión
Asegurar la segmentación inmediata de los estudiantes al registrarse e implementar controles de seguridad y consentimiento de datos (GDPR/LOPD).

### Añadido
*   **das_email_preferences**: Formulario de onboarding interactivo y mandatorio presentado de forma forzada a cualquier alumno con rol de portal (`base.group_portal`) tras su primer inicio de sesión.
*   **Controladores de Bloqueo**: Interceptores de ruta en el portal de Odoo que evalúan el booleano `das_preference_completed` de la ficha del socio, redirigiendo de manera permanente al formulario de onboarding en caso de ser falso.
*   **Estructura del Perfil Académico**:
    *   Campos obligatorios de fecha de nacimiento (`das_birthday`), intereses en áreas TI (`das_interest_ids`), nivel de experiencia previa en software (`das_experience_level`), categorías de cursos favoritos y aceptación obligatoria de términos y políticas.
*   **Sincronización Inmediata con Marketing**:
    *   Lógica de base de datos que asocia al socio en tiempo real con las listas de Email Marketing correspondientes en base a sus selecciones de onboarding.

### Corregido
*   Exención automática de usuarios del sistema y administradores internos (`base.group_user`) de la redirección forzada del portal.

---

## [18.0.1.5.2] - 2026-05-20 (Sprint Campañas de Fidelización por Correo)

### 🎯 Objetivos de la Versión
Lanzar la automatización de marketing segmentado y garantizar la idempotencia de los envíos diarios de correos masivos.

### Añadido
*   **das_email_campaigns**: Motor de Runners automáticos en Odoo.
*   **Runners Diarios (`ir.cron`)**:
    1.  `_run_birthday`: Envía un correo con plantillas dinámicas el día exacto de cumpleaños del estudiante.
    2.  `_run_upcoming`: Detecta cursos que iniciarán en los próximos 2 o 3 días y notifica a los estudiantes interesados.
    3.  `_run_new_courses`: Recopila cursos publicados en los últimos 7 días y los envía a las listas segmentadas.
    4.  `_run_experience`: Recomienda cursos específicos alineados con el nivel del estudiante (Principiante/Intermedio/Avanzado).
    5.  `_run_newsletter`: Envía resúmenes periódicos respetando la frecuencia (semanal/mensual) elegida en el onboarding.
*   **Garantía de Idempotencia (`das.email.campaign.log`)**:
    *   Estructura que almacena registros de envío con un campo clave compuesto (`period_key`) por socio, fecha y curso. Esto evita duplicaciones de correos incluso si el cron se ejecuta de forma repetida.

---

## [18.0.1.0.0] - 2026-04-15 (Sprint Localización Fiscal de Ecuador y SRI)

### 🎯 Objetivos de la Versión
Adaptar la facturación de Odoo a la normativa legal ecuatoriana mediante validaciones de identidad y firmas criptográficas autorizadas.

### Añadido
*   **l10n_ec_base**: Algoritmos matemáticos de validación de documentos nacionales en el campo `vat` del contacto:
    *   Módulo 10 para cédulas de identidad (10 dígitos).
    *   Módulo 11 para RUCs de Sociedades Privadas y Entidades Públicas (13 dígitos).
    *   Alfanumérico mayor a 5 caracteres para Pasaportes internacionales.
*   **l10n_ec_sri**: Firma criptográfica local XAdES-BES.
    *   Carga de llaves privadas RSA y certificados X.509 desde archivos PKCS12 (.p12).
    *   Canonicalización XML C14N e incrustación de la firma en los nodos de la factura XML.
*   **Gateway SOAP Offline del SRI**:
    *   Integración robusta con los Web Services Offline del SRI mediante cliente SOAP (Zeep) para los métodos `validarComprobante` y `autorizacionComprobante`.
