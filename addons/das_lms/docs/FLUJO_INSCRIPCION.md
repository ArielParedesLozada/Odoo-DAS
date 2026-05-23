# Flujo de inscripción DAS LMS (eLearning)

## Resumen

La inscripción comercial en cursos eLearning se controla por **fechas académicas** del canal (`slide.channel`) y un **corte configurable** antes del fin del curso. No se usan coincidencias por nombre: el vínculo producto↔curso es estructural (`das_lms_channel_id` o `slide.channel.product_id`).

## Campos en el curso

| Campo | Descripción |
|-------|-------------|
| `das_start_date` | Inicio académico (desbloqueo de lecciones para inscritos). |
| `das_end_date` | Fin académico del curso. |
| `registration_cutoff_days` | Días antes del fin en que se cierra la inscripción (por defecto **2**). |
| `das_registration_deadline` | Calculado: `das_end_date − registration_cutoff_days`. |
| `das_registration_open` | `True` si hoy ≤ fecha límite y el curso no finalizó. |

## Reglas de inscripción

1. **Ya inscrito** → acceso normal al curso; botón «Acceder al curso» en tienda; sin «Agregar al carrito».
2. **No inscrito** → puede comprar/inscribirse solo si `das_registration_open` es verdadero.
3. **Lecciones** → inscritos acceden cuando `das_can_study` (no antes de `das_start_date`).
4. **Alta efectiva** → al validar factura (`account.move._post`) o flujo PayPal LMS; idempotente vía `_das_lms_enroll_partner`.

## Mensajes en tienda / portal

| Estado | Mensaje |
|--------|---------|
| Antes del inicio | El curso aún no ha comenzado. Inscríbete ahora. |
| Inscripción abierta | El curso está en curso. Inscríbete hasta N días antes de finalizar. |
| Corte superado | La inscripción ya no está disponible para este curso. |

- **Verde**: alumno inscrito.
- **Amarillo**: visitante, inscripción aún permitida.
- **Gris**: inscripción cerrada.

## Portal `/slides`

Usuarios portal solo ven cursos donde son miembros (`slide.channel.partner`). El acceso a lecciones respeta el calendario académico.

## Migración

Al actualizar el módulo, los cursos existentes reciben `registration_cutoff_days = 2` si no tenían valor. Se registran en log cursos con fechas inválidas o sin `das_end_date`.
