# 🔑 Manual de Integración, APIs y Catálogo de Endpoints (Ecosistema Odoo-DAS)

Este manual técnico proporciona la documentación criptográfica, algoritmos de validación e informática detallada para los procesos de validación de identidad, facturación electrónica offline y el catálogo completo de controladores y rutas HTTP/JSON implementados en la **Academia Virtual de Tecnología** (Odoo-DAS v18.0).

---

## 🇪🇨 1. Algoritmos de Validación de Identidad (`l10n_ec_base`)

Ecuador emplea tres tipos principales de documentos fiscales. El módulo `l10n_ec_base` los valida mediante algoritmos matemáticos específicos antes de procesar cotizaciones o facturas.

### Algoritmo 1.1: Cédula de Identidad y RUC de Persona Natural (Módulo 10)
*   **Longitud**: 10 dígitos (Cédula) o 13 dígitos (RUC, finalizado en `001`).
*   **Lógica Matemática**:
    1.  Los primeros dos dígitos corresponden a la provincia emisora (de `01` a `24`, o `30` para consulados).
    2.  El tercer dígito debe ser menor a `6` (indica persona natural).
    3.  Se extraen los primeros 9 dígitos. Cada dígito en posición impar se multiplica por `2`, y cada dígito en posición par se multiplica por `1`.
    4.  Si el producto de cualquier multiplicación es mayor o igual a `10`, se le resta `9`.
    5.  Se suman todos los productos resultantes.
    6.  **Cálculo del Dígito Verificador**: Se resta la suma obtenida de la decena superior inmediata. Si el residuo es `10`, el dígito verificador es `0`.
    7.  El resultado debe coincidir con el décimo dígito del documento.
*   **Representación en Código**:
    ```python
    def validar_cedula(numero):
        if len(numero) != 10 or not numero.isdigit():
            return False
        provincia = int(numero[0:2])
        if not (1 <= provincia <= 24 or provincia == 30):
            return False
        tercer_digito = int(numero[2])
        if tercer_digito >= 6:
            return False
        coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        suma = 0
        for i in range(9):
            val = int(numero[i]) * coeficientes[i]
            suma += val - 9 if val >= 10 else val
        verificador = (10 - (suma % 10)) % 10
        return verificador == int(numero[9])
    ```

### Algoritmo 1.2: RUC de Sociedades Privadas y Extranjeros (Módulo 11)
*   **Longitud**: 13 dígitos, finalizado en `001`.
*   **Lógica Matemática**:
    1.  El tercer dígito debe ser exactamente `9`.
    2.  Se multiplican los primeros 9 dígitos por los coeficientes fijos ponderados: `[4, 3, 2, 7, 6, 5, 4, 3, 2]`.
    3.  Se suman los productos. El residuo de dividir la suma para `11` se resta de `11` para obtener el dígito verificador (décimo dígito). Si el residuo es `0`, el verificador es `0`.

### Algoritmo 1.3: RUC de Entidades Públicas (Módulo 11)
*   **Longitud**: 13 dígitos, finalizado en `001`.
*   **Lógica Matemática**:
    1.  El tercer dígito debe ser exactamente `6`.
    2.  Se multiplican los primeros 8 dígitos por los coeficientes fijos ponderados: `[3, 2, 7, 6, 5, 4, 3, 2]`.
    3.  Se suman los productos. El residuo de dividir la suma para `11` se resta de `11` para obtener el dígito verificador (noveno dígito). El décimo dígito siempre es `0`.

---

## ✒️ 2. Especificación Criptográfica de la Firma XAdES-BES

Ecuador exige que los comprobantes electrónicos sigan el estándar de firma avanzada **XAdES-BES (Basic Electronic Signature)**, el cual incrusta la firma digital dentro del propio XML de la factura.

### Estructura del Nodo de Firma `<ds:Signature>` inyectado en el XML:

```xml
<factura id="comprobante" version="2.1.0">
    <!-- Datos de la Factura (infoTributaria, infoFactura, detalles) -->
    
    <ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#" Id="Signature-SRI">
        <ds:SignedInfo>
            <!-- Algoritmo de normalización XML C14N -->
            <ds:CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>
            <!-- Algoritmo de firmado asimétrico -->
            <ds:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>
            
            <!-- Referencia al documento XML principal (Factura) -->
            <ds:Reference URI="#comprobante">
                <ds:Transforms>
                    <ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
                </ds:Transforms>
                <ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
                <!-- Hash SHA1 del XML canonicalizado en Base64 -->
                <ds:DigestValue>mP5B6cDe4v...=</ds:DigestValue>
            </ds:Reference>
            
            <!-- Referencia a las propiedades de firma XAdES -->
            <ds:Reference URI="#SignedProperties-ID">
                <ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
                <ds:DigestValue>jKhD83...=</ds:DigestValue>
            </ds:Reference>
        </ds:SignedInfo>
        
        <!-- Firma digital encriptada en Base64 de la sección SignedInfo -->
        <ds:SignatureValue Id="SignatureValue-ID">
            aB7d9f...[RSA-2048-Signature-Value-256bytes]...==
        </ds:SignatureValue>
        
        <!-- Certificado público X.509 en Base64 para validación del SRI -->
        <ds:KeyInfo Id="KeyInfo-ID">
            <ds:X509Data>
                <ds:X509Certificate>
                    MIIEuzCCA6OgAwIBAgI...[Base64-DER-X509-Certificate]...
                </ds:X509Certificate>
            </ds:X509Data>
        </ds:KeyInfo>
        
        <!-- Bloque de Propiedades Específicas de XAdES (Marca de tiempo, algoritmo, etc.) -->
        <ds:Object Id="XadesObject-ID">
            <xades:QualifyingProperties xmlns:xades="http://uri.etsi.org/01903/v1.3.2#" Target="#Signature-SRI">
                <xades:SignedProperties Id="SignedProperties-ID">
                    <xades:SignedSignatureProperties>
                        <xades:SigningTime>2026-05-29T15:15:00-05:00</xades:SigningTime>
                        <xades:SigningCertificate>
                            <xades:Cert>
                                <xades:CertDigest>
                                    <ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
                                    <ds:DigestValue>y9Fk3...=</ds:DigestValue>
                                </xades:CertDigest>
                                <xades:IssuerSerial>
                                    <ds:X509IssuerName>CN=UANATACA, O=Uanataca S.A.</ds:X509IssuerName>
                                    <ds:X509SerialNumber>12345678</ds:X509SerialNumber>
                                </xades:IssuerSerial>
                            </xades:Cert>
                        </xades:SigningCertificate>
                    </xades:SignedSignatureProperties>
                </xades:SignedProperties>
            </xades:QualifyingProperties>
        </ds:Object>
    </ds:Signature>
</factura>
```

---

## 🔌 3. Catálogo de Endpoints y APIs por Módulo

Esta sección detalla de manera exhaustiva cada una de las rutas web HTTP y JSON expuestas por los controladores de los módulos de la plataforma académica.

### 🗺️ 3.1. Onboarding de Preferencias (`das_email_preferences`)
Este módulo intercepta y maneja el flujo de registro y segmentación obligatoria de los estudiantes del portal.

#### Tabla Resumen de Rutas
| Ruta (URI) | Método HTTP | Tipo Odoo | Autenticación | Descripción |
| :--- | :---: | :---: | :---: | :--- |
| `/my/email-preferences` | `GET` | `http` | `user` | Renderiza el formulario interactivo de preferencias/onboarding. |
| `/my/email-preferences/edit` | `GET` | `http` | `user` | Alias de visualización o edición de preferencias. |
| `/my/email-preferences/submit` | `POST` | `http` | `user` | Procesa y valida el envío del formulario de preferencias. |

#### Detalle Técnico de Endpoints
*   **Formulario de Onboarding / Edición** (`/my/email-preferences` y `/my/email-preferences/edit`):
    1. Valida si el usuario actual es un estudiante registrado en el portal (`_das_is_portal_student_user()`). Si es un usuario interno o administrador, lo redirige a la vista administrativa `/web`.
    2. Obtiene o crea un borrador de preferencias (`das.email.preference`) para el socio actual.
    3. Pasa las listas de intereses activos (`das.email.interest`), categorías de cursos preferidos (`das.email.course.category`) y niveles de experiencia al motor QWeb para renderizar el formulario.
*   **Procesamiento de Preferencias** (`/my/email-preferences/submit`):
    *   **Parámetros Recibidos**: `interest_ids` (List[int]), `course_category_ids` (List[int]), `birthday` (string `YYYY-MM-DD`), `experience_level` (selection), `terms_accepted` (bool), `privacy_accepted` (bool).
    *   **Lógica de Validación**: Fuerza la ejecución en modo administrador seguro (`sudo()`). Si falta algún campo obligatorio, intercepta el `ValidationError` y vuelve a renderizar el formulario inyectando un mensaje de error legible en el frontend. Al guardar exitosamente, registra la dirección IP (`completed_ip`) y su fecha de confirmación (`completed_on`), lo suscribe a los segmentos de Email Marketing y libera la intercepción del portal.

---

### 🛍️ 3.2. Tienda Virtual y eCommerce (`das_lms`)
Este controlador extiende el flujo estándar de `website_sale` de Odoo para inyectar las reglas del carrito y validación académica.

#### Tabla Resumen de Rutas
| Ruta (URI) | Método HTTP | Tipo Odoo | Autenticación | Descripción |
| :--- | :---: | :---: | :---: | :--- |
| `/shop/cart/update` | `POST` | `http` | `public` | Añade o modifica la cantidad de un producto (redirección QWeb). |
| `/shop/cart/update_json` | `POST` | `json` | `public` | Añade o modifica la cantidad de un producto (llamada síncrona JS). |

#### Detalle Técnico de Endpoints
*   **Actualización de Carrito con Redirección** (`/shop/cart/update`):
    *   Intercepta la adición estándar de artículos a la cotización activa en Odoo (`sale.order`). Si se intenta violar las reglas de carrito único o límite de 1 unidad para un curso LMS, el ORM arroja un `UserError`. El controlador captura esta excepción, realiza un `rollback` de la transacción SQL en base de datos para evitar contaminar la cotización, escribe el mensaje de error en la cotización actual (`shop_warning`) y redirige limpiamente al carrito `/shop/cart` en lugar de romper el hilo HTTP del navegador.
*   **Actualización de Carrito Asíncrona (JSON-RPC)** (`/shop/cart/update_json`):
    *   Endpoint utilizado por los botones `+` y `-` y la pasarela interactiva de eCommerce de Odoo. Si el ORM lanza un `UserError` de validación académica, ejecuta `request.env.cr.rollback()`, guarda el mensaje de advertencia en el registro contable de Odoo (`shop_warning`) y retorna un objeto JSON con la llave `warning` para que el script JS del cliente alerte en rojo al estudiante.

---

### 🏫 3.3. Aulas Virtuales y Lecciones eLearning (`das_lms` / Slides)
Maneja el portal de eLearning, restringiendo contenidos según inscripciones de facturas y fechas del calendario académico oficial del estudiante.

#### Tabla Resumen de Rutas
| Ruta (URI) | Método HTTP | Tipo Odoo | Autenticación | Descripción |
| :--- | :---: | :---: | :---: | :--- |
| `/slides` | `GET` | `http` | `public` | Página principal de e-Learning (simplificada para estudiantes). |
| `/slides/all` | `GET` | `http` | `public` | Catálogo de todos los cursos (filtrado según visibilidad). |
| `/slides/<int:channel_id>` | `GET` | `http` | `public` | Visualiza la portada y lecciones estructuradas del curso. |
| `/slides/slide/<int:slide_id>` | `GET` | `http` | `public` | Abre e inicia el reproductor de la lección (diapositiva/video). |
| `/slides/slide/<int:slide_id>/pdf_content` | `GET` | `http` | `public` | Obtiene el flujo binario del PDF o documento adjunto. |
| `/slides/slide/get_html_content` | `POST` | `json` | `public` | Obtiene el contenido HTML de lecciones de tipo artículo de texto. |
| `/slides/slide/quiz/submit` | `POST` | `json` | `public` | Envía y califica las respuestas del cuestionario de la lección. |

#### Detalle Técnico de Endpoints y Reglas de Seguridad
*   **Home e-Learning Unificado** (`/slides`):
    *   Simplifica la visualización para los portal estudiantes en el frontend. Descarta secciones automáticas ("Popular", "Novedades") y renderiza únicamente la grilla de sus cursos matriculados (`channels_my`) para evitar distracciones en el portal.
*   **Visualización y Acceso al Curso** (`/slides/<model("slide.channel"):channel>`):
    *   Verifica si el curso es públicamente visible en la tienda (`_das_lms_is_public_catalog_visible()`). Si el usuario actual es de tipo portal y el curso no permite el autoestudio o el alumno no está matriculado, corta el flujo y redirige al estudiante a la tienda o le renderiza una plantilla de acceso denegado (`das_lms.portal_slide_channel_access_denied`).
*   **Reproducción de Lecciones** (`/slides/slide/<model("slide.slide"):slide>`):
    *   Antes de delegar la visualización a Odoo, invoca el método `_das_lms_portal_guard_lesson_http()`. Si el curso tiene estado académico `proximo` (fecha de inicio futura), el estudiante no puede ver el contenido y es redirigido a la portada del curso adjuntando el parámetro `?das_lms_lesson_pending=1` en la URL para renderizar una advertencia.
*   **Descarga de Material Adjunto** (`/slides/slide/<model("slide.slide"):slide>/pdf_content`):
    *   Verifica mediante `_das_lms_portal_guard_lesson_binary()` si el estudiante cuenta con membresía activa y si el curso ya inició. Si el alumno intenta descargar el PDF ingresando el ID directo de la lección en la barra de direcciones del navegador, el servidor intercepta la descarga y le retorna una respuesta **HTTP 403 Forbidden**.

---

### 🎓 3.4. Módulo: Gestión de Certificados y Evaluaciones (`das_lms_certificates`)
Este módulo implementa el flujo de finalización de cursos, validación pública de códigos criptográficos y generación dinámica de certificados académicos firmados.

#### Tabla Resumen de Rutas
| Ruta (URI) | Método HTTP | Tipo Odoo | Autenticación | Descripción |
| :--- | :---: | :---: | :---: | :--- |
| `/validar/certificado/<string:token>` | `GET` | `http` | `public` | Valida públicamente la autenticidad de un certificado. |
| `/my/certificate/<int:channel_id>` | `GET` | `http` | `user` | Genera y descarga el PDF del certificado del curso. |
| `/survey/<int:survey_id>/get_certification` | `GET` | `http` | `user` | Intercepta la descarga nativa tras aprobar la evaluación. |
| `/survey/submit/<string:survey_token>/<string:answer_token>` | `POST` | `json` | `public` | Intercepta el envío de exámenes y encuestas para enrutamiento. |
| `/survey/start/<string:survey_token>` | `GET` | `http` | `public` | Controla el inicio del examen final o encuesta de satisfacción. |
| `/survey/results/<string:answer_token>` | `GET` | `http` | `public` | Autodescarga el PDF del certificado al finalizar la encuesta. |

#### Detalle Técnico de Endpoints y Lógica de Flujo
*   **Validación Pública de Certificados** (`/validar/certificado/<string:token>`):
    *   Realiza una búsqueda segura en base de datos (`sudo()`) en el modelo `course.enrollment` buscando la coincidencia exacta de la firma criptográfica `das_lms_certificate_token == token`. Si no existe, renderiza `das_lms_certificates.certificate_invalid_page`. Si es legítimo, renderiza `das_lms_certificates.certificate_valid_page`.
*   **Descarga Directa de Certificado** (`/my/certificate/<int:channel_id>`):
    *   Si no existe una matrícula (`course.enrollment`) para el estudiante autenticado en el curso `channel_id`, se le redirige automáticamente a `/slides`. Si existe pero el estado es `pending`, se interrumpe y se devuelve error `http_routing.403` ("Debes completar el examen final"). Si no ha completado la encuesta obligatoria (`das_lms_survey_completed == False`), se devuelve error `http_routing.403` ("Debes completar la encuesta de satisfacción"). Al cumplir los requisitos, genera el informe PDF formal `das_lms_certificates.action_report_course_certificate` y se envía como descarga.
*   **Interceptor de Certificación Nativa** (`/survey/<int:survey_id>/get_certification`):
    *   Si la encuesta terminada es de tipo Examen Final o Encuesta de Satisfacción, verifica si la encuesta de satisfacción ya fue respondida. Si falta por realizar, localiza el slide correspondiente y redirige síncronamente al estudiante a ella en pantalla completa (`/slides/slide/<sat_slide_id>?fullscreen=1`). De lo contrario, genera el certificado personalizado.
*   **Envío Asíncrono de Respuestas** (`/survey/submit/<string:survey_token>/<string:answer_token>`):
    *   **Caso Examen Final**: Intercepta la respuesta JSON de finalización de Odoo e inyecta dinámicamente un destino de redirección al slide de la encuesta de satisfacción obligatoria.
    *   **Caso Encuesta de Satisfacción**: Si el alumno envía sus respuestas, actualiza el flag `das_lms_survey_completed = True`.
*   **Control de Inicio del Examen / Encuesta** (`/survey/start/<string:survey_token>`):
    *   Si se intenta iniciar la encuesta de satisfacción, verifica si el alumno tiene matrícula válida y si ya aprobó el examen final. Si no se cumple, niega el ingreso y devuelve una página HTTP 403.
*   **Auto-Descarga de Resultados** (`/survey/results/<string:answer_token>`):
    *   Al cargar los resultados de la encuesta de satisfacción, marca la encuesta como completada en la inscripción y genera directamente la descarga del certificado PDF personalizado.

---

### 🔒 3.5. Módulo: Reglas de Seguridad en Aulas y Exámenes (`das_lms_satisfaction_survey`)
Este módulo intercepta el renderizado de lecciones del portal eLearning de Odoo para blindar las rutas académicas.

#### Tabla Resumen de Rutas
| Ruta (URI) | Método HTTP | Tipo Odoo | Autenticación | Descripción |
| :--- | :---: | :---: | :---: | :--- |
| `/slides/slide/<model("slide.slide"):slide>` | `GET` | `http` | `public` | Interceptor de seguridad en la visualización de la lección. |

#### Detalle Técnico de las Guardias del Controlador
*   **Endpoint**: `/slides/slide/<model("slide.slide"):slide>`
*   **Método**: `GET`
*   **Controlador**: `SlideSecurityController.slide`
*   **Lógica de Protección**:
    *   **Guardia de Encuesta**: Si la diapositiva solicitada tiene `das_is_satisfaction_survey == True`, verifica que la matrícula exista y que `das_lms_final_status != 'pending'`. Si no se cumple, aborta la renderización y muestra una página **HTTP 403 Forbidden** exigiendo terminar primero el examen.
    *   **Guardia de Examen Final**: Si la diapositiva solicitada tiene `das_is_final_exam == True`, verifica que la matrícula exista (si no, devuelve HTTP 403 "Debes estar inscrito en el curso") y valida si ya rindió el examen final previamente (`das_lms_final_status != 'pending'`). Si ya fue completado, bloquea reintentos no autorizados devolviendo una página HTTP 403 ("Ya realizaste el examen final"). Si se superan las guardias, delega la renderización limpia con `super().slide(...)`.

---

### ✉️ 3.6. Módulo: Previsualización de Campañas de Email (`das_email_campaigns`)
Permite a los gestores de email marketing verificar el resultado visual de las plantillas y variables dinámicas.

#### Tabla Resumen de Rutas
| Ruta (URI) | Método HTTP | Tipo Odoo | Autenticación | Descripción |
| :--- | :---: | :---: | :---: | :--- |
| `/das_email/preview/list/<int:list_id>` | `GET` | `http` | `user` | Renderiza previsualización del boletín de una lista. |
| `/das_email/preview/mailing/<int:mailing_id>` | `GET` | `http` | `user` | Renderiza previsualización de un borrador de campaña. |

#### Detalle Técnico de Endpoints
*   **Previsualización de Plantilla de Lista de Correos** (`/das_email/preview/list/<int:list_id>`):
    1. Verifica la existencia de la lista de correos. Si no existe, devuelve una respuesta HTTP 404 Not Found.
    2. Si se proporciona `contact_id`, carga el contacto para procesar las variables de reemplazo dinámico.
    3. Invoca la lógica interna `_das_render_preview_html(contact)` para compilar la plantilla HTML y la devuelve con cabecera `Content-Type: text/html`.
*   **Previsualización de Borrador de Campaña** (`/das_email/preview/mailing/<int:mailing_id>`):
    1. Verifica la existencia de la campaña de correo. Si no existe, devuelve HTTP 404.
    2. Utiliza el motor de renderizado `_das_render_preview_html` de Odoo Mass Mailing pasando el contacto si está provisto para previsualizar el diseño exacto con datos reales en formato HTML síncrono.
