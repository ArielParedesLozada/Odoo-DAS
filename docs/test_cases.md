# 📋 Registro y Fichas de Casos de Prueba Funcionales - Academia Virtual de Tecnología

Este documento recopila las fichas de pruebas funcionales exhaustivas y de negocio ejecutadas para validar el ecosistema de la **Academia Virtual de Tecnología** (Odoo-DAS v18.0). Todas las pruebas están vinculadas a la suite de tests en Python.

---

## 🗂️ 1. Módulo: Gestión Académica LMS y Tienda (`das_lms`)

### Ficha de Caso de Prueba: TC-LMS-01
*   **Identificador**: `TC-LMS-01`
*   **Nombre del Caso**: Validación de Inscripción Académica Idempotente.
*   **Módulo / Componente**: `das_lms` / Modelo `slide.channel` / Función `_das_lms_enroll_partner`.
*   **Precondiciones**:
    *   Existe un curso e-Learning creado (ej. *Auditoría de Sistemas de Información*).
    *   Existe un contacto del estudiante registrado con cuenta de portal activa.
*   **Datos de Entrada**:
    *   Socio ID: `res.partner(name='Alumno enroll')`
    *   Canal ID: `slide.channel(name='Canal LMS enroll')`
*   **Pasos de Ejecución**:
    1.  Invocar el método de inscripción interna: `channel._das_lms_enroll_partner(partner)`.
    2.  Verificar en la base de datos la creación del registro en la tabla `slide.channel.partner` en estado activo.
    3.  Volver a invocar exactamente el mismo método `channel._das_lms_enroll_partner(partner)` para el mismo socio y canal.
    4.  Realizar una búsqueda por conteo (`search_count`) de membresías activas para este estudiante.
*   **Resultado Esperado**:
    *   La primera invocación crea el registro.
    *   La segunda invocación no duplica la fila en base de datos.
    *   El conteo final de registros activos para el estudiante en el curso debe ser exactamente **1**.
*   **Resultado Obtenido**: Pasa. Conteo final igual a 1 sin duplicaciones en la base de datos (Ejecuta `test_das_lms_enroll_partner_idempotent`).
*   **Estado Final**: **PASA**

---

### Ficha de Caso de Prueba: TC-LMS-02
*   **Identificador**: `TC-LMS-02`
*   **Nombre del Caso**: Restricción de Compra de Múltiples Cursos LMS en el Carrito.
*   **Módulo / Componente**: `das_lms` / Modelo de línea de venta `sale.order.line` / Control de carrito.
*   **Precondiciones**:
    *   Existen dos productos de tipo curso LMS publicados en la tienda en línea.
*   **Datos de Entrada**:
    *   Producto A: *Auditoría de Sistemas de Información* (vinculado a canal LMS).
    *   Producto B: *Inteligencia Artificial* (vinculado a canal LMS).
*   **Pasos de Ejecución**:
    1.  Iniciar sesión en el portal web como estudiante.
    2.  Navegar a la tienda, seleccionar el Producto A y pulsar **"Agregar al carrito"**.
    3.  Regresar al catálogo, seleccionar el Producto B e intentar pulsar **"Agregar al carrito"**.
*   **Resultado Esperado**:
    *   El Producto A se agrega correctamente.
    *   Al intentar agregar el Producto B, la petición HTTP es interceptada por el backend en la validación del modelo `sale.order.line` y se interrumpe la transacción arrojando una excepción `UserError` en la interfaz.
*   **Resultado Obtenido**: Pasa. Se bloquea la adición del segundo curso y se muestra la alerta en rojo en pantalla.
*   **Evidencia Visual**: *(Ver captura de error de carrito: [lms_cart_error.png](file:///c:/Users/johan/OneDrive/Documentos/Universidad/Desarrollo%20Asistido%20por%20Software/OdooLeonel/Odoo-DAS/docs/images/lms_cart_error.png))*
*   **Estado Final**: **PASA**

---

### Ficha de Caso de Prueba: TC-LMS-03
*   **Identificador**: `TC-LMS-03`
*   **Nombre del Caso**: Bloqueo de Acceso a Lecciones de Curso Próximo.
*   **Módulo / Componente**: `das_lms` / Modelo `slide.channel` / Función `_das_lms_portal_can_access_course_lessons`.
*   **Precondiciones**:
    *   Existe un curso e-Learning configurado con una fecha de inicio futura.
    *   El estudiante de portal está matriculado en el curso.
*   **Datos de Entrada**:
    *   `das_start_date` = Hoy + 5 días.
    *   Usuario: `portal_proximo_user`
*   **Pasos de Ejecución**:
    1.  Acceder al portal con la cuenta del estudiante.
    2.  Navegar al panel de **Mis Cursos** y hacer clic sobre el curso.
    3.  Intentar acceder a los contenidos de la lección haciendo clic sobre los botones de lectura.
*   **Resultado Esperado**:
    *   El estudiante figura como inscrito y puede ver la página del curso.
    *   La función `_das_lms_portal_can_access_course_lessons` devuelve `False`, bloqueando el renderizado de la diapositiva y las rutas de lectura de lecciones.
*   **Resultado Obtenido**: Pasa. Los contenidos figuran bloqueados con candado y se impide la reproducción de contenidos (Ejecuta `test_portal_lesson_access_proximo_member_blocked`).
*   **Estado Final**: **PASA**

---

### Ficha de Caso de Prueba: TC-LMS-04
*   **Identificador**: `TC-LMS-04`
*   **Nombre del Caso**: Bloqueo de Nuevos Miembros en Curso Académico Finalizado.
*   **Módulo / Componente**: `das_lms` / Modelo `slide.channel` / Función `_action_add_members`.
*   **Precondiciones**:
    *   Existe un curso cuya fecha de finalización ya expiró.
*   **Datos de Entrada**:
    *   `das_end_date` = Hoy - 2 días.
    *   Socio a matricular: `Nuevo alumno`
*   **Pasos de Ejecución**:
    1.  Intentar matricular (ya sea por compra o manual) al nuevo estudiante en el curso cerrado.
*   **Resultado Esperado**:
    *   El sistema evalúa el estado del curso como `finalizado`.
    *   El gancho intercepta la acción de agregar miembros y lanza un `UserError` impidiendo que nuevos alumnos se inscriban retrospectivamente en cursos cerrados.
*   **Resultado Obtenido**: Pasa. Se lanza el `UserError` impidiendo la matrícula síncrona (Ejecuta `test_das_academic_status_finalizado_blocks_new_member`).
*   **Estado Final**: **PASA**

---

### Ficha de Caso de Prueba: TC-LMS-05
*   **Identificador**: `TC-LMS-05`
*   **Nombre del Caso**: Confirmación de Pedido y Matrícula LMS Automática vía Pasarela PayPal.
*   **Módulo / Componente**: `das_lms` / Modelo de transacción `payment.transaction` / Integración PayPal.
*   **Precondiciones**:
    *   Existe un producto tipo LMS y su respectivo canal e-learning publicados en la tienda.
    *   La pasarela PayPal se encuentra configurada en estado de pruebas o producción.
*   **Datos de Entrada**:
    *   Pedido de Venta: `sale.order` con 1 unidad del curso.
    *   Transacción: `payment.transaction` asociada a PayPal con estado de pago `done` (exitoso) o `pending` (pendiente procesada).
*   **Pasos de Ejecución**:
    1.  El estudiante realiza el checkout web seleccionando PayPal como método de pago.
    2.  Procesar el retorno/callback del pago de la transacción llamando a la confirmación de transacción `_post_process()`.
    3.  Verificar que el pedido de venta (`sale.order`) cambie automáticamente a estado `sale` (venta firme).
    4.  Verificar que la factura del cliente (`account.move`) se publique en estado `posted`, se concilie con el pago de PayPal y quede marcada como **"Pagada"**.
    5.  Verificar que el estudiante quede matriculado de forma síncrona en el canal de diapositivas (`slide.channel.partner` en estado activo).
*   **Resultado Esperado**:
    *   El pedido se confirma.
    *   Se crea y publica la factura del cliente como pagada.
    *   El estudiante tiene acceso inmediato al material del e-learning.
*   **Resultado Obtenido**: Pasa. Toda la conciliación de facturas y la activación de matrículas académicas de LMS se ejecuta síncronamente al procesarse el callback de PayPal (Ejecuta `test_paypal_done_posts_invoice_and_enrolls_without_automatic_invoice` y `test_paypal_pending_confirms_posts_invoice_and_enrolls`).
*   **Estado Final**: **PASA**

---

## 🗃️ 2. Módulo: Onboarding de Preferencias (`das_email_preferences`)

### Ficha de Caso de Prueba: TC-PREF-01
*   **Identificador**: `TC-PREF-01`
*   **Nombre del Caso**: Intercepción y Redirección Forzada al Formulario de Onboarding.
*   **Módulo / Componente**: `das_email_preferences` / Rutas de Portal web.
*   **Precondiciones**:
    *   Se crea un nuevo usuario de tipo Portal (Estudiante). No posee preferencias registradas.
*   **Datos de Entrada**:
    *   Usuario: `pref_portal_new@test.example.com`
*   **Pasos de Ejecución**:
    1.  Iniciar sesión con la cuenta de portal.
    2.  Intentar navegar a la página de cursos `/slides` o a la cuenta personal `/my`.
*   **Resultado Esperado**:
    *   El sistema evalúa que el usuario de portal tiene el onboarding pendiente.
    *   Interrumpe la carga de la página solicitada y realiza una redirección HTTP 302 hacia `/das_email_preferences/onboarding`.
*   **Resultado Obtenido**: Pasa. Redirección forzada activa en todas las rutas del portal hasta completar el guardado.
*   **Evidencia Visual**: *(Ver captura del formulario de onboarding: [onboarding_form.png](file:///c:/Users/johan/OneDrive/Documentos/Universidad/Desarrollo%20Asistido%20por%20Software/OdooLeonel/Odoo-DAS/docs/images/onboarding_form.png))*
*   **Estado Final**: **PASA**

---

### Ficha de Caso de Prueba: TC-PREF-02
*   **Identificador**: `TC-PREF-02`
*   **Nombre del Caso**: Validación de Registro de Preferencias Académicas Exitoso.
*   **Módulo / Componente**: `das_email_preferences` / Modelo `das.email.preference` / Función `submit_from_portal`.
*   **Precondiciones**:
    *   El estudiante se encuentra en la pantalla de onboarding.
*   **Datos de Entrada**:
    *   IP del cliente: `127.0.0.1`
    *   Datos: `{'interest_ids': [Tecnología, Desarrollo], 'birthday': '1995-05-29', 'experience_level': 'intermediate', 'terms_accepted': True, 'privacy_accepted': True}`
*   **Pasos de Ejecución**:
    1.  Rellenar el formulario con los datos de entrada válidos.
    2.  Presionar el botón de envío (ejecuta `submit_from_portal`).
    3.  Verificar que el registro de preferencias se marque como completado en la base de datos y almacene la dirección IP.
    4.  Verificar que la ficha del socio (`res.partner`) asocie el cumpleaños, intereses y nivel de experiencia.
*   **Resultado Esperado**:
    *   El campo `completed` de la preferencia pasa a `True`.
    *   La dirección IP `127.0.0.1` queda registrada en `completed_ip`.
    *   La ficha del contacto de Odoo se sincroniza inmediatamente con los campos correspondientes.
*   **Resultado Obtenido**: Pasa. Todos los campos se sincronizan de forma síncrona en base de datos (Ejecuta `test_submit_preferences_success`).
*   **Estado Final**: **PASA**

---

## 📧 3. Módulo: Campañas de Email Marketing (`das_email_campaigns`)

### Ficha de Caso de Prueba: TC-CAMP-01
*   **Identificador**: `TC-CAMP-01`
*   **Nombre del Caso**: Idempotencia Diaria del Runner de Cumpleaños.
*   **Módulo / Componente**: `das_email_campaigns` / Runner `_run_birthday` / Tabla `das.email.campaign.log`.
*   **Precondiciones**:
    *   Existe un estudiante cuyo cumpleaños registrado es HOY.
    *   La campaña de correo automático de cumpleaños está activa.
*   **Datos de Entrada**:
    *   Estudiante: Born `29/05/1990` (Edad 36 años).
    *   Runner: `das.email.campaign.runner`
*   **Pasos de Ejecución**:
    1.  Ejecutar la campaña automática llamando a `Runner._run_birthday(config_birthday)`.
    2.  Verificar la creación de la bitácora `das.email.campaign.log` con la clave periódica `daily_20260529_partner_X`.
    3.  Volver a disparar de forma síncrona el mismo Runner `Runner._run_birthday(config_birthday)`.
*   **Resultado Esperado**:
    *   La primera corrida procesa al estudiante, genera el mailing y devuelve un conteo de envíos de al menos **1**.
    *   La segunda corrida evalúa que ya existe el log periódico para el socio de la fecha de hoy, saltando el envío y devolviendo un conteo de **0**.
*   **Resultado Obtenido**: Pasa. Prevención de envíos duplicados garantizada por la bitácora periódica (Ejecuta `test_birthday_campaign_idempotent`).
*   **Estado Final**: **PASA**

---

## 🇪🇨 4. Módulo: Validación de Identidad del Ecuador (`l10n_ec_base`)

### Ficha de Caso de Prueba: TC-BASE-01
*   **Identificador**: `TC-BASE-01`
*   **Nombre del Caso**: Validación Exitosa de Cédula de Identidad de Ecuador.
*   **Módulo / Componente**: `l10n_ec_base` / Campo `vat` de `res.partner`.
*   **Precondiciones**:
    *   Crear contacto en Odoo seleccionando país "Ecuador" y tipo "Cédula".
*   **Datos de Entrada**:
    *   Cédula Real: `1710034065`
*   **Pasos de Ejecución**:
    1.  Ingresar el número en el campo `vat`.
    2.  Presionar el botón de guardado en el ERP.
*   **Resultado Esperado**:
    *   El algoritmo ejecuta el módulo 10. La suma ponderada es divisible bajo la decena superior arrojando un residuo de `5`.
    *   Se valida el dígito verificador y se permite el guardado del contacto de forma exitosa.
*   **Resultado Obtenido**: Pasa. Contacto guardado sin excepciones de formulario (Ejecuta `test_valid_cedula`).
*   **Estado Final**: **PASA**

---

### Ficha de Caso de Prueba: TC-BASE-02
*   **Identificador**: `TC-BASE-02`
*   **Nombre del Caso**: Rechazo de Cédula de Identidad Inválida (Dígito Verificador Erróneo).
*   **Módulo / Componente**: `l10n_ec_base` / Validación matemática.
*   **Precondiciones**:
    *   Intentar crear un contacto en Odoo con tipo de identificación "Cédula".
*   **Datos de Entrada**:
    *   Cédula Inválida: `1710034069` (Último dígito modificado ad-hoc).
*   **Pasos de Ejecución**:
    1.  Ingresar el número en el campo `vat`.
    2.  Intentar presionar el botón de guardado.
*   **Resultado Esperado**:
    *   El validador detecta que el residuo calculado no coincide con el dígito verificador final `9`.
    *   Detiene el guardado en la base de datos lanzando una excepción `ValidationError` que se muestra al usuario.
*   **Resultado Obtenido**: Pasa. Odoo lanza el mensaje de error de validación y bloquea el guardado en la base de datos (Ejecuta `test_invalid_mod10`).
*   **Estado Final**: **PASA**

---

## ✒️ 5. Módulo: Facturación Electrónica y SRI (`l10n_ec_sri`)

### Ficha de Caso de Prueba: TC-SRI-01
*   **Identificador**: `TC-SRI-01`
*   **Nombre del Caso**: Firma Digital Completa XAdES-BES en XML.
*   **Módulo / Componente**: `l10n_ec_sri` / Motor de Firma / `test_sri_signer.py`.
*   **Precondiciones**:
    *   Cargar el archivo binario del certificado de pruebas y su clave en memoria.
*   **Datos de Entrada**:
    *   XML de factura base de la Academia.
    *   Certificado: `test_certificate.p12` / Contraseña: `test1234`
*   **Pasos de Ejecución**:
    1.  Lanzar el parser XML.
    2.  Aplicar canonicalización C14N exclusiva.
    3.  Calcular hash SHA1 y codificar digest.
    4.  Firmar digitalmente con clave privada RSA de 2048 bits usando padding PKCS#1 v1.5.
    5.  Incrustar los nodos `<ds:SignatureValue>` y el certificado Base64 en `<ds:X509Certificate>`.
*   **Resultado Esperado**:
    *   Se genera exitosamente el XML firmado cumpliendo con los estándares de la firma XAdES-BES.
    *   Se comprueba la presencia de todos los elementos obligatorios exigidos por el SRI ecuatoriano.
*   **Resultado Obtenido**: Pasa. El XML firmado se genera de forma íntegra sin deformar las etiquetas del comprobante original.
*   **Evidencia Visual**: *(Ver diagrama criptográfico de firma: [sri_signature_flow.png](file:///c:/Users/johan/OneDrive/Documentos/Universidad/Desarrollo%20Asistido%20por%20Software/OdooLeonel/Odoo-DAS/docs/images/sri_signature_flow.png))*
*   **Estado Final**: **PASA**

---

## 🧪 6. Guía y Evidencias de Ejecución de Pruebas Unitarias

Esta sección describe cómo ejecutar las pruebas unitarias y de integración de cada módulo desde la consola contenerizada e incluye los contenedores visuales para las capturas de pantalla de resultados de cada suite de pruebas.

### 🔌 Tabla de Comandos de Ejecución

Para ejecutar las pruebas de cada módulo de forma individual y aislada, use uno de los siguientes métodos (se recomienda cambiar el puerto HTTP con `--http-port` para evitar conflictos con el servidor Odoo activo en el puerto `8070`):

| Módulo Custom | Comando de Ejecución (Desde Windows / PowerShell) |
| :--- | :--- |
| **LMS y Tienda (`das_lms`)** | `docker exec -it odoo18-das odoo --test-enable --stop-after-init -d odoo_academia -u das_lms --http-port=8088` |
| **Preferencias (`das_email_preferences`)** | `docker exec -it odoo18-das odoo --test-enable --stop-after-init -d odoo_academia -u das_email_preferences --http-port=8088` |
| **Campañas (`das_email_campaigns`)** | `docker exec -it odoo18-das odoo --test-enable --stop-after-init -d odoo_academia -u das_email_campaigns --http-port=8088` |
| **Ecuador Base (`l10n_ec_base`)** | `docker exec -it odoo18-das odoo --test-enable --stop-after-init -d odoo_academia -u l10n_ec_base --http-port=8088` |
| **Firma y SRI (`l10n_ec_sri`)** | `docker exec -it odoo18-das odoo --test-enable --stop-after-init -d odoo_academia -u l10n_ec_sri --http-port=8088` |

---

### 📸 Evidencias Visuales de Ejecución por Módulo

> [!NOTE]
> Para completar las evidencias del proyecto, capture la consola al finalizar la suite de pruebas de cada módulo y guarde la imagen correspondiente en la carpeta `docs/images/` con el nombre indicado en cada sección.

#### 1. Módulo: Gestión Académica LMS (`das_lms`)
*   **Comando de Ejecución**:
    ```bash
    docker exec -it odoo18-das odoo --test-enable --stop-after-init -d odoo_academia -u das_lms --http-port=8088
    ```
*   **Captura de Pantalla (Guardar como `test_evidence_das_lms.png`)**:
    ![Evidencia das_lms](file:///c:/Users/johan/OneDrive/Documentos/Universidad/Desarrollo%20Asistido%20por%20Software/OdooLeonel/Odoo-DAS/docs/images/test_evidence_das_lms.png)

#### 2. Módulo: Onboarding de Preferencias (`das_email_preferences`)
*   **Comando de Ejecución**:
    ```bash
    docker exec -it odoo18-das odoo --test-enable --stop-after-init -d odoo_academia -u das_email_preferences --http-port=8088
    ```
*   **Captura de Pantalla (Guardar como `test_evidence_das_email_preferences.png`)**:
    ![Evidencia das_email_preferences](file:///c:/Users/johan/OneDrive/Documentos/Universidad/Desarrollo%20Asistido%20por%20Software/OdooLeonel/Odoo-DAS/docs/images/test_evidence_das_email_preferences.png)

#### 3. Módulo: Campañas de Email Marketing (`das_email_campaigns`)
*   **Comando de Ejecución**:
    ```bash
    docker exec -it odoo18-das odoo --test-enable --stop-after-init -d odoo_academia -u das_email_campaigns --http-port=8088
    ```
*   **Captura de Pantalla (Guardar como `test_evidence_das_email_campaigns.png`)**:
    ![Evidencia das_email_campaigns](file:///c:/Users/johan/OneDrive/Documentos/Universidad/Desarrollo%20Asistido%20por%20Software/OdooLeonel/Odoo-DAS/docs/images/test_evidence_das_email_campaigns.png)

#### 4. Módulo: Validación de Identidad del Ecuador (`l10n_ec_base`)
*   **Comando de Ejecución**:
    ```bash
    docker exec -it odoo18-das odoo --test-enable --stop-after-init -d odoo_academia -u l10n_ec_base --http-port=8088
    ```
*   **Captura de Pantalla (Guardar como `test_evidence_l10n_ec_base.png`)**:
    ![Evidencia l10n_ec_base](file:///c:/Users/johan/OneDrive/Documentos/Universidad/Desarrollo%20Asistido%20por%20Software/OdooLeonel/Odoo-DAS/docs/images/test_evidence_l10n_ec_base.png)

#### 5. Módulo: Facturación Electrónica y SRI (`l10n_ec_sri`)
*   **Comando de Ejecución**:
    ```bash
    docker exec -it odoo18-das odoo --test-enable --stop-after-init -d odoo_academia -u l10n_ec_sri --http-port=8088
    ```
*   **Captura de Pantalla (Guardar como `test_evidence_l10n_ec_sri.png`)**:
    ![Evidencia l10n_ec_sri](file:///c:/Users/johan/OneDrive/Documentos/Universidad/Desarrollo%20Asistido%20por%20Software/OdooLeonel/Odoo-DAS/docs/images/test_evidence_l10n_ec_sri.png)

