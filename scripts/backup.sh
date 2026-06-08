#!/usr/bin/env bash
# ============================================================
# backup.sh — Backup de PostgreSQL y filestore de Odoo
# Uso: ./scripts/backup.sh [prod|staging]
# Cron recomendado: 0 2 * * * /opt/odoo-das/scripts/backup.sh prod
# ============================================================
set -euo pipefail

ENVIRONMENT="${1:-prod}"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="${BACKUP_DIR:-/opt/backups/odoo-das}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"

GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'
log()  { echo -e "${GREEN}[BACKUP]${NC} $(date '+%Y-%m-%d %H:%M:%S') $*"; }
fail() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

ENV_FILE="$REPO_DIR/.env.${ENVIRONMENT}"
[[ -f "$ENV_FILE" ]] || fail "No existe $ENV_FILE"
set -a; source "$ENV_FILE"; set +a

DB_CONTAINER="odoo18-${ENVIRONMENT}-db"
ODOO_CONTAINER="odoo18-${ENVIRONMENT}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/${ENVIRONMENT}/${TIMESTAMP}"

mkdir -p "$BACKUP_PATH"

# ── Backup de PostgreSQL ─────────────────────────────────────
log "Haciendo backup de PostgreSQL ($DB_NAME)..."
docker exec "$DB_CONTAINER" pg_dump \
    -U "${DB_USER:-odoo}" \
    -d "${DB_NAME:-odoo_${ENVIRONMENT}}" \
    --format=custom \
    --compress=9 \
    > "$BACKUP_PATH/db_${DB_NAME}_${TIMESTAMP}.dump"

log "Backup de DB: $BACKUP_PATH/db_${DB_NAME}_${TIMESTAMP}.dump"

# ── Backup del filestore ─────────────────────────────────────
log "Haciendo backup del filestore..."
docker run --rm \
    --volumes-from "$ODOO_CONTAINER" \
    -v "$BACKUP_PATH:/backup" \
    alpine tar czf "/backup/filestore_${TIMESTAMP}.tar.gz" \
        -C /var/lib/odoo .local/share/Odoo/filestore 2>/dev/null || \
    log "Advertencia: filestore vacío o no encontrado (normal en primera ejecución)"

log "Backup del filestore: $BACKUP_PATH/filestore_${TIMESTAMP}.tar.gz"

# ── Eliminar backups antiguos ────────────────────────────────
log "Eliminando backups de más de $RETENTION_DAYS días..."
find "$BACKUP_DIR/${ENVIRONMENT}" -type f -mtime "+${RETENTION_DAYS}" -delete
find "$BACKUP_DIR/${ENVIRONMENT}" -type d -empty -delete

# ── Resumen ──────────────────────────────────────────────────
BACKUP_SIZE=$(du -sh "$BACKUP_PATH" | cut -f1)
log "Backup completado — Tamaño: $BACKUP_SIZE — Ruta: $BACKUP_PATH"
