#!/usr/bin/env bash
# ============================================================
# update-prod.sh — Actualizar Odoo en producción (Azure VM)
# Ejecutar directamente EN LA VM: ./scripts/update-prod.sh
#
# Uso básico:   ./scripts/update-prod.sh
# Con módulos:  ./scripts/update-prod.sh -u das_lms,das_email_preferences
# ============================================================
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$REPO_DIR/docker/docker-compose.prod.yml"
ENV_FILE="$REPO_DIR/.env.prod"
CONTAINER_ODOO="odoo18-prod"
CONTAINER_DB="odoo18-prod-db"
MODULES_TO_UPDATE="${MODULES:-das_email_preferences,das_email_campaigns,das_lms,das_lms_certificates,das_lms_satisfaction_survey}"
UPDATE_FLAG=""

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
log()  { echo -e "${GREEN}[DEPLOY]${NC} $*"; }
warn() { echo -e "${YELLOW}[ WARN ]${NC} $*"; }
fail() { echo -e "${RED}[ERROR ]${NC} $*"; exit 1; }

# ── Opciones ─────────────────────────────────────────────────
while getopts "u:h" opt; do
    case $opt in
        u) MODULES_TO_UPDATE="$OPTARG"; UPDATE_FLAG="yes" ;;
        h) echo "Uso: $0 [-u modulo1,modulo2]"; exit 0 ;;
        *) fail "Opción inválida" ;;
    esac
done

# ── Validaciones ─────────────────────────────────────────────
[[ -f "$ENV_FILE" ]]     || fail "No existe $ENV_FILE"
[[ -f "$COMPOSE_FILE" ]] || fail "No existe $COMPOSE_FILE"

# ── 1. Obtener últimos cambios ────────────────────────────────
log "Obteniendo cambios de main..."
cd "$REPO_DIR"
git fetch origin main
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [[ "$LOCAL" == "$REMOTE" ]]; then
    warn "No hay cambios nuevos en main. ¿Forzar igualmente? (Ctrl+C para cancelar)"
    sleep 5
fi

git pull origin main
log "Código actualizado a: $(git log -1 --format='%h %s')"

# ── 2. Reconstruir imagen ────────────────────────────────────
log "Construyendo imagen Docker con los cambios nuevos..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build --no-cache odoo-prod
log "Imagen construida."

# ── 3. Reiniciar solo el contenedor de Odoo ──────────────────
# (la DB NO se reinicia para no interrumpir conexiones)
log "Reiniciando contenedor Odoo..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --no-deps odoo-prod

# ── 4. Esperar que Odoo responda ─────────────────────────────
log "Esperando que Odoo esté listo..."
for i in $(seq 1 30); do
    if docker exec "$CONTAINER_ODOO" curl -sf http://localhost:8069/web/health >/dev/null 2>&1; then
        log "Odoo activo (intento $i)"
        break
    fi
    if [[ $i -eq 30 ]]; then
        fail "Odoo no respondió tras 5 minutos. Ver: docker logs $CONTAINER_ODOO"
    fi
    echo "  Esperando... $i/30"
    sleep 10
done

# ── 5. Actualizar módulos si se especificó -u ────────────────
source "$ENV_FILE"
DB="${DB_NAME:-odoo_prod}"
DB_USER_VAL="${DB_USER:-odoo}"

if [[ -n "$UPDATE_FLAG" ]]; then
    log "Actualizando módulos: $MODULES_TO_UPDATE en DB: $DB"
    # Primero verificar que la DB existe
    if docker exec "$CONTAINER_DB" psql -U "$DB_USER_VAL" -lqt 2>/dev/null | cut -d'|' -f1 | grep -qw "$DB"; then
        docker exec "$CONTAINER_ODOO" odoo \
            --config /etc/odoo/odoo.conf \
            --database "$DB" \
            --update "$MODULES_TO_UPDATE" \
            --stop-after-init \
            --log-level=warn
        # Volver a levantar después del --stop-after-init
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --no-deps odoo-prod
        log "Módulos actualizados. Odoo reiniciado."
    else
        warn "DB '$DB' no encontrada. Saltando actualización de módulos."
    fi
fi

log "Despliegue completado."
log "URL: https://odoo-das-g4.westus3.cloudapp.azure.com"
