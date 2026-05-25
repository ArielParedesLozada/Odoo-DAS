# Flujo de inscripción DAS LMS (eLearning)

## Resumen

La inscripción comercial en cursos eLearning se controla por **fechas académicas** del canal (`slide.channel`) y un **corte configurable antes del inicio**. No se usan coincidencias por nombre: el vínculo producto↔curso es estructural (`das_lms_channel_id` o `slide.channel.product_id`).

## Campos en el curso

| Campo | Descripción |
|-------|-------------|
| `das_start_date` | Inicio académico (desbloqueo de lecciones para inscritos). |
| `das_end_date` | Fin académico del curso. |
| `registration_cutoff_days` | Días antes del **inicio** en que se cierra la inscripción (por defecto **2**). |
| `das_registration_deadline` | Calculado: `das_start_date − registration_cutoff_days`. |
| `das_registration_open` | `True` si hoy ≤ último día de inscripción y el curso no finalizó. |

## Reglas de inscripción

1. **Último día de inscripción** = fecha de inicio − días de corte.
2. Si `fecha_actual > último día de inscripción` → **no se puede inscribir** (mensaje: *La inscripción para este curso ha cerrado.*).
3. Si `fecha_actual >= fecha de inicio` → el curso **no se muestra** en tienda ni catálogo eLearning para visitantes no inscritos.
4. **Ya inscrito** → acceso normal al curso; botón «Acceder al curso» en tienda; sin «Agregar al carrito».
5. **Lecciones** → inscritos acceden cuando `das_can_study` (no antes de `das_start_date`).
6. **Alta efectiva** → al validar factura (`account.move._post`) o flujo PayPal LMS; idempotente vía `_das_lms_enroll_partner`.

## Mensajes en tienda / portal

| Estado | Mensaje |
|--------|---------|
| Antes del inicio (inscripción abierta) | El curso aún no ha comenzado. Inscríbete hasta el DD/MM/AAAA. |
| Corte superado o curso iniciado | La inscripción para este curso ha cerrado. |

- **Verde**: alumno inscrito.
- **Amarillo**: visitante, inscripción aún permitida.
- **Gris**: inscripción cerrada.

## Portal `/slides`

Usuarios portal solo ven cursos donde son miembros (`slide.channel.partner`). El catálogo público `/slides/all` oculta cursos cuya fecha de inicio ya pasó (salvo inscritos). El acceso a lecciones respeta el calendario académico.

## Ficha de producto en `/shop`

Aunque el curso no aparezca en el listado de la tienda (o se acceda por enlace directo), **la página del producto sí se abre** y muestra un aviso informativo (inscripción cerrada / curso ya iniciado) sin botón de compra.

## Migración

Al actualizar el módulo, los cursos existentes conservan `registration_cutoff_days` (por defecto **2** si no tenían valor). A partir de v18.0.4.32.0 el corte se calcula respecto a la **fecha de inicio**, no a la fecha de fin.
