# 🛠️ Guía de Desarrollo y Arquitectura - Academia Virtual de Tecnología (Odoo-DAS)

Esta guía técnica proporciona las especificaciones de arquitectura, diccionarios de datos, configuraciones de seguridad por roles y pautas de mantenimiento necesarias para administrar y extender el ecosistema de la **Academia Virtual de Tecnología** (Odoo-DAS v18.0).

---

## 🏗️ 1. Modelo de Datos y Diccionario de Base de Datos (PostgreSQL)

El ecosistema de Odoo-DAS interactúa con varios modelos personalizados y heredados del framework Odoo. A continuación se detallan las tablas y campos clave inyectados en la base de datos:

### Tabla: `das.email.preference` (Preferencias de Estudiante)
Esta tabla almacena las respuestas recolectadas durante el formulario de onboarding obligatorio del portal.

| Nombre Técnico Campo | Tipo Odoo | Restricciones / Atributos | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Clave Primaria (Auto-incremental) | Identificador único del registro. |
| `partner_id` | Many2one | `res.partner`, `ondelete='cascade'`, `required=True` | Relación con el socio de contacto de Odoo asociado al estudiante. |
| `completed` | Boolean | `default=False`, `index=True` | Indica si el estudiante completó exitosamente su formulario de onboarding. |
| `completed_on` | Datetime | `readonly=True` | Sello de tiempo exacto del envío de preferencias. |
| `completed_ip` | Char | `size=45` | Dirección IP del cliente registrada durante el envío (soporta IPv4 e IPv6). |
| `interest_ids` | Many2many | Tabla relacional `das_preference_interest_rel` | Intereses temáticos elegidos por el estudiante (vinculado a `das.email.interest`). |
| `birthday` | Date | `required=True` | Fecha de nacimiento para la campaña automatizada de felicitación. |
| `experience_level` | Selection | `('beginner', 'intermediate', 'expert', 'none')` | Nivel de conocimiento auto-declarado. |
| `communication_frequency` | Selection | `('weekly', 'monthly', 'never')`, `default='weekly'` | Frecuencia de envío de correos masivos configurada por el alumno. |
| `terms_accepted` | Boolean | `required=True`, debe ser `True` | Consentimiento explícito de los términos del portal de la Academia. |
| `privacy_accepted` | Boolean | `required=True`, debe ser `True` | Consentimiento de la política de privacidad de datos. |

---

### Tabla: `course.enrollment` (Matrículas Académicas)
Esta tabla registra y audita el historial de inscripciones asociadas a miembros de canales de e-Learning.

| Nombre Técnico Campo | Tipo Odoo | Restricciones / Atributos | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Clave Primaria | Identificador único de matrícula. |
| `channel_partner_id` | Many2one | `slide.channel.partner`, `required=True`, `ondelete='cascade'` | Relación con el miembro del canal académico. |
| `student_id` | Many2one | `res.partner`, `related='channel_partner_id.partner_id'`, `store=True` | Socio (Estudiante) matriculado (campo guardado para optimizar búsquedas). |
| `channel_id` | Many2one | `slide.channel`, `related='channel_partner_id.channel_id'`, `store=True` | Canal (Curso) de e-Learning asociado a la matrícula. |
| `modality` | Selection | `('grabado', 'en_vivo', 'mixto')` | Copia la modalidad académica del curso correspondiente al matricular. |
| `enrollment_date` | Date | `default=fields.Date.today` | Fecha en la que se generó y validó la matrícula del estudiante. |
| `status` | Selection | `('active', 'suspended', 'completed')`, `default='active'` | Estado administrativo de la matrícula. |

---

### Tabla: `das.email.campaign.log` (Bitácora e Idempotencia de Envío)
Tabla central para el control de duplicaciones y auditoría del motor de Email Marketing.

| Nombre Técnico Campo | Tipo Odoo | Restricciones / Atributos | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Clave Primaria | Identificador único de log. |
| `config_id` | Many2one | `das.email.campaign.config`, `required=True` | Campaña de marketing que generó el envío. |
| `partner_id` | Many2one | `res.partner`, `required=True`, `index=True` | Estudiante destinatario del correo. |
| `period_key` | Char | `size=100`, `required=True`, `index=True` | Clave única generada por periodo (ej. `daily_20260529` para cumpleaños, o `course_4_partner_12` para curso próximo). Evita envíos duplicados en la misma ventana de tiempo. |
| `channel_ref_id` | Integer | `default=0` | Relación con el curso que motivó la alerta (usado en campañas "Upcoming"). |
| `mailing_id` | Many2one | `mailing.mailing`, `readonly=True` | Enlace al envío de correo masivo específico generado por Odoo. |
| `state` | Selection | `('queued', 'sent', 'failed')`, `default='queued'` | Estado del ciclo de vida del envío del correo. |
| `trace_status` | Selection | `('open', 'click', 'reply', 'bounce', 'received')` | Estado del rastreo del correo sincronizado desde `mailing.trace`. |

---

## 👥 2. Configuración de Seguridad y Asignación de Roles (Odoo Backend)

Para cumplir con los estándares empresariales de la **Academia Virtual de Tecnología**, se han definido reglas de seguridad a nivel de registros (`ir.model.access.csv`) y grupos de seguridad (`security/`) para los **5 roles** del sistema:

### Asignación de Grupos y Permisos Técnicos:

1.  **Estudiante (Portal)**:
    *   **Grupo Asociado**: `base.group_portal`.
    *   **Permisos de Lectura (`read`)**: Modelos `slide.channel`, `slide.channel.partner`, `product.template`, `das.email.preference` (solo su propio registro).
    *   **Permisos de Escritura (`write`)**: Crear y modificar su ficha de preferencias `das.email.preference` en su onboarding.
    *   **Acceso en Backend**: Totalmente bloqueado. Navega únicamente a través de la interfaz web del Portal.

2.  **Instructor**:
    *   **Grupo Asociado**: `das_lms.group_instructor` (hereda de `base.group_user`).
    *   **Permisos**: Acceso completo de lectura y escritura sobre `slide.channel` y `slide.channel.partner`. Puede subir contenidos de lecciones y ver progresos de alumnos. Permiso de lectura sobre facturas de clientes vinculadas a sus cursos.

3.  **Coordinador Académico**:
    *   **Grupo Asociado**: `das_lms.group_coordinator` (hereda de `das_lms.group_instructor`).
    *   **Permisos**: Acceso total (CRUD) sobre `slide.channel` y `course.enrollment`. Puede crear nuevos cursos, vincularlos con productos, cambiar modalidades y modificar fechas académicas.

4.  **Asesor Comercial**:
    *   **Grupo Asociado**: `sales_team.group_sale_salesman` (Ventas / Comercial).
    *   **Permisos**: Acceso completo a pedidos de venta (`sale.order`), cotizaciones y control sobre las listas de Email Marketing (`mailing.list` y `das.email.campaign.config`). Puede disparar envíos manuales de campañas.

5.  **Analista Financiero**:
    *   **Grupo Asociado**: `account.group_account_invoice` (Facturación / Contabilidad básica).
    *   **Permisos**: Acceso total sobre facturas de clientes (`account.move`) y control de la pasarela local de pagos. Es el único perfil habilitado para interactuar con los logs de firma digital del SRI y autorizaciones de facturas electrónicas.

---

## 📧 3. Configuración de Servidores de Correo Saliente (SMTP)

Las campañas automáticas de marketing (Birthday, boletines por nivel, boletín semanal) dependen críticamente de la configuración del servidor de correo saliente en Odoo. 

### Parámetros de Configuración del Servidor SMTP (`ir.mail_server`):
Para dar de alta el servidor saliente en producción o pruebas, acceda a **Ajustes ──► Servidores de Correo Saliente** y configure:

*   **Descripción / Nombre**: `Odoo-Learning-DAS-SMTP`
*   **Prioridad**: `10`
*   **Servidor SMTP (Host)**: `smtp.gmail.com` (o el servidor SMTP corporativo de la Academia).
*   **Puerto**: `465` (o `587` para TLS).
*   **Seguridad de la Conexión**: `SSL/TLS` (Recomendado).
*   **Nombre de Usuario (Username)**: `grupophpasw@gmail.com` (Correo remitente configurado por el equipo).
*   **Contraseña**: Contraseña de aplicación generada en la cuenta de Google para conexiones seguras externas.

> [!TIP]
> **Prueba de Conexión**: Siempre presione el botón **"Probar conexión"** tras la configuración. Odoo debe retornar un mensaje de éxito: *"¡Conexión SMTP exitosa!"*. Si no se configura correctamente, todos los correos generados por las campañas automáticas diarias se acumularán en estado encolado (`delivery_step='ready'`) en la cola de correos de Odoo (`mail.mail`).

---

## ⚓ 4. Ganchos de Herencia Técnica (Python Hooks)

El ecosistema expande la lógica de Odoo mediante herencia clásica (`_inherit`). A continuación se detallan los ganchos técnicos más importantes implementados en los addons:

### Hook 4.1: Intercepción de Rutas en Portal para Onboarding Obligatorio
*   **Módulo**: `das_email_preferences`
*   **Archivo**: `controllers/portal.py`
*   **Clase**: `CustomerPortal` (hereda de `portal.CustomerPortal`)
*   **Método**: `_prepare_portal_layout_values` y ganchos de carga de ruta del home del portal.
*   **Lógica**:
    ```python
    @http.route()
    def home(self, **kw):
        user = request.env.user
        if user._das_must_complete_email_preferences():
            return request.redirect('/das_email_preferences/onboarding')
        return super().home(**kw)
    ```

### Hook 4.2: Restricción de Carrito Académico en Líneas de Pedido
*   **Módulo**: `das_lms`
*   **Archivo**: `models/sale_order_line.py`
*   **Clase**: `SaleOrderLine` (hereda de `sale.order.line`)
*   **Lógica**: Sobrescribe el método `create` e implementa un decorator `@api.constrains('product_id', 'product_uom_qty')`.
    1.  Evalúa si el producto asignado está vinculado a un canal de eLearning (`product_id.das_lms_channel_id` o `slide_channel_ids`).
    2.  Si la cantidad es superior a 1, lanza un `ValidationError`.
    3.  Busca si en las otras líneas del carrito (`order_id.order_line`) ya existe otra línea con un producto de tipo curso LMS. Si se encuentra, aborta la creación lanzando un `UserError` en español.
