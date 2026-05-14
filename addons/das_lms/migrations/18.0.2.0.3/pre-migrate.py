# -*- coding: utf-8 -*-
"""Migrar course.enrollment antiguo (student_id + course_id) al esquema con channel_partner_id.

Solo aplica en actualización de bases que aún no tienen la columna o tienen NULLs.
La base `odoo` puede estar al día mientras `odoo_academia` sigue en esquema previo.
"""
import logging

_logger = logging.getLogger(__name__)

STUDENT_COURSE_UNIQUE = 'course_enrollment_course_enrollment_student_course_unique'
CHANNEL_PARTNER_FK = 'course_enrollment_channel_partner_id_fkey'
CHANNEL_PARTNER_UNIQUE = 'course_enrollment_course_enrollment_channel_partner_unique'
CERTIFICATE_FK = 'course_enrollment_certificate_id_fkey'


def _table_exists(cr, relname):
    cr.execute(
        "SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
        "WHERE n.nspname = 'public' AND c.relkind = 'r' AND c.relname = %s",
        (relname,),
    )
    return bool(cr.fetchone())


def _column_exists(cr, table, column):
    cr.execute(
        """
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s AND column_name = %s
        """,
        (table, column),
    )
    return bool(cr.fetchone())


def _constraint_exists(cr, name):
    cr.execute("SELECT 1 FROM pg_constraint WHERE conname = %s", (name,))
    return bool(cr.fetchone())


def migrate(cr, version):
    if not _table_exists(cr, 'course_enrollment'):
        return

    if not _column_exists(cr, 'course_enrollment', 'student_id') or not _column_exists(
        cr, 'course_enrollment', 'course_id'
    ):
        _logger.info('das_lms pre-migrate: course_enrollment sin student_id/course_id, omitiendo.')
        return

    added_column = False
    if not _column_exists(cr, 'course_enrollment', 'channel_partner_id'):
        _logger.info('das_lms pre-migrate: añadiendo columna channel_partner_id.')
        cr.execute('ALTER TABLE course_enrollment ADD COLUMN channel_partner_id INTEGER NULL')
        added_column = True

    cr.execute(
        """
        SELECT id, student_id, course_id
        FROM course_enrollment
        WHERE channel_partner_id IS NULL
          AND student_id IS NOT NULL
          AND course_id IS NOT NULL
        """
    )
    pending = cr.fetchall()
    if pending:
        _logger.info(
            'das_lms pre-migrate: enlazando %s fila(s) a slide.channel.partner.',
            len(pending),
        )
    for eid, partner_id, channel_id in pending:
        cr.execute(
            """
            SELECT id FROM slide_channel_partner
            WHERE channel_id = %s AND partner_id = %s
            LIMIT 1
            """,
            (channel_id, partner_id),
        )
        row = cr.fetchone()
        if row:
            scp_id = row[0]
        else:
            cr.execute(
                """
                INSERT INTO slide_channel_partner (
                    channel_id, partner_id, member_status, active, completion,
                    create_date, write_date
                )
                VALUES (
                    %s, %s, 'joined', TRUE, 0,
                    (NOW() AT TIME ZONE 'UTC'), (NOW() AT TIME ZONE 'UTC')
                )
                RETURNING id
                """,
                (channel_id, partner_id),
            )
            scp_id = cr.fetchone()[0]
        cr.execute(
            'UPDATE course_enrollment SET channel_partner_id = %s WHERE id = %s',
            (scp_id, eid),
        )

    cr.execute(
        'SELECT id FROM course_enrollment WHERE channel_partner_id IS NULL'
    )
    orphans = [r[0] for r in cr.fetchall()]
    if orphans:
        raise RuntimeError(
            'das_lms pre-migrate: imposible rellenar channel_partner_id para los ids %s '
            '(falta student_id o course_id). Corrija o elimine esas filas y vuelva a actualizar el módulo.'
            % orphans
        )

    if added_column or _column_exists(cr, 'course_enrollment', 'channel_partner_id'):
        cr.execute(
            """
            SELECT a.attnotnull
            FROM pg_attribute a
            JOIN pg_class c ON a.attrelid = c.oid
            JOIN pg_namespace n ON c.relnamespace = n.oid
            WHERE n.nspname = 'public'
              AND c.relname = 'course_enrollment'
              AND a.attname = 'channel_partner_id'
              AND NOT a.attisdropped
            """
        )
        row = cr.fetchone()
        if row and not row[0]:
            _logger.info('das_lms pre-migrate: channel_partner_id NOT NULL.')
            cr.execute(
                'ALTER TABLE course_enrollment ALTER COLUMN channel_partner_id SET NOT NULL'
            )

    if _constraint_exists(cr, STUDENT_COURSE_UNIQUE):
        _logger.info('das_lms pre-migrate: eliminando restricción única antigua (student_id, course_id).')
        cr.execute(
            'ALTER TABLE course_enrollment DROP CONSTRAINT %s' % STUDENT_COURSE_UNIQUE
        )

    if _constraint_exists(cr, CERTIFICATE_FK):
        _logger.info('das_lms pre-migrate: eliminando FK certificate_id obsoleta.')
        cr.execute('ALTER TABLE course_enrollment DROP CONSTRAINT %s' % CERTIFICATE_FK)

    if _column_exists(cr, 'course_enrollment', 'certificate_id'):
        _logger.info('das_lms pre-migrate: eliminando columna certificate_id obsoleta.')
        cr.execute('ALTER TABLE course_enrollment DROP COLUMN certificate_id')

    if not _constraint_exists(cr, CHANNEL_PARTNER_FK):
        _logger.info('das_lms pre-migrate: añadiendo FK channel_partner_id.')
        cr.execute(
            """
            ALTER TABLE course_enrollment
            ADD CONSTRAINT %s
            FOREIGN KEY (channel_partner_id)
            REFERENCES slide_channel_partner(id)
            ON DELETE CASCADE
            """
            % CHANNEL_PARTNER_FK
        )

    if not _constraint_exists(cr, CHANNEL_PARTNER_UNIQUE):
        _logger.info('das_lms pre-migrate: añadiendo UNIQUE(channel_partner_id).')
        cr.execute(
            """
            ALTER TABLE course_enrollment
            ADD CONSTRAINT %s UNIQUE (channel_partner_id)
            """
            % CHANNEL_PARTNER_UNIQUE
        )
