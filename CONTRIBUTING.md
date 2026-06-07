# 🤝 Guía de Contribución para Odoo-DAS

¡Gracias por tu interés en contribuir al ecosistema **Odoo-DAS**! Para mantener la calidad de la base de código y la consistencia en el desarrollo del proyecto, te pedimos que sigas las siguientes pautas.

---

## 🚦 Reglas de Desarrollo y Flujo de Trabajo

### 1. Gestión de Ramas (Git Branching)
Utilizamos un flujo simplificado basado en GitFlow. Toda rama nueva debe crearse a partir de `main` y seguir la nomenclatura adecuada:
*   **Funcionalidades**: `feature/nombre-de-la-funcionalidad`
*   **Corrección de Errores**: `bugfix/descripcion-corta-del-error`
*   **Refactorización**: `refactor/nombre-del-componente`
*   **Documentación**: `docs/seccion-documentada`

*Ejemplo: `git checkout -b feature/das-lms-restricted-cart`*

### 2. Normas de Estilo de Código (Python & Odoo)
*   **PEP 8**: Todo el código Python debe cumplir con el estándar PEP 8.
*   **Formateador**: Recomendamos el uso de `black` para formatear el código de manera consistente.
*   **Nomenclatura Odoo**:
    *   Los nombres de modelos deben usar notación de punto (ej. `das.email.preference`).
    *   Los campos relacionales deben terminar con `_id` (many2one) o `_ids` (one2many, many2many).
    *   Evite el uso de variables globales y mantenga las funciones de controlador y modelo lo más atómicas posibles.

### 3. Commits y Mensajes descriptivos
Los mensajes de commit deben ser claros y estructurados en español. Se sugiere seguir el formato Conventional Commits de forma simplificada:
*   `feat:` para nuevas funcionalidades.
*   `fix:` para corregir errores.
*   `docs:` para cambios en la documentación.
*   `refactor:` para cambios de código que no corrigen bugs ni agregan funciones.

*Ejemplo: `feat(das_lms): agregar restriccion de cantidad de cursos en el carrito de compras`*

---

## 🧪 Pruebas Obligatorias antes del Pull Request

Antes de enviar cualquier Pull Request (PR) o realizar un push a `main`, **es obligatorio ejecutar y pasar la suite de pruebas unitarias**:
```bash
python odoo-bin -c config/odoo.conf -i das_lms,das_email_preferences,das_email_campaigns,l10n_ec_base,l10n_ec_sri --test-enable --stop-after-init
```
Cualquier PR que rompa los tests existentes o disminuya la cobertura será rechazado automáticamente por el equipo de revisión.

---

## 📝 Documentación en Notion y Código
Si agregas un nuevo campo o cambias una regla de negocio en Odoo:
1.  Actualiza el docstring en el código del modelo.
2.  Refleja los cambios en las especificaciones correspondientes en la wiki del proyecto en **Notion**.
3.  Agrega el caso de prueba correspondiente en la carpeta `tests/` del módulo afectado.
