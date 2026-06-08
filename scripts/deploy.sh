#!/usr/bin/env bash
# ============================================================
# deploy.sh — Despliegue de Odoo DAS en Azure VM
# Uso: ./scripts/deploy.sh [prod|staging] [image_tag]
# Ejemplo: ./scripts/deploy.sh prod v1.2.3
# ============================================================
set -euo pipefail

ENVIRONMENT="${1:-prod}"
IMAGE_TAG="${2:-latest}"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
log()  { echo -e "${GREEN}[DEPLOY]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC}  $*"; }
fail() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# ── Validaciones ─────────────────────────────────────────────
[[ "$ENVIRONMENT" == "prod" || "$ENVIRONMENT" == "staging" ]] || \
    fail "Entorno inválido: '$ENVIRONMENT'. Usar 'prod' o 'staging'"

ENV_FILE="$REPO_DIR/.env.${ENVIRONMENT}"
[[ -f "$ENV_FILE" ]] || fail "No existe $ENV_FILE — copia .env.example y completa los valores"

COMPOSE_FILE="$REPO_DIR/docker/docker-compose.${ENVIRONMENT}.yml"
[[ -f "$COMPOSE_FILE" ]] || fail "No existe $COMPOSE_FILE"

log "Iniciando despliegue en entorno: $ENVIRONMENT — imagen: $IMAGE_TAG"

# ── Crear red compartida si no existe ────────────────────────
if ! docker network inspect nginx-proxy >/dev/null 2>&1; then
    log "Creando red Docker 'nginx-proxy'..."
    docker network create nginx-proxy
fi

# ── Login en GHCR ────────────────────────────────────────────
if [[ -n "${GHCR_TOKEN:-}" ]]; then
    log "Autenticando en GitHub Container Registry..."
    echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin
fi

# ── Pull de la nueva imagen ──────────────────────────────────
source "$ENV_FILE"
FULL_IMAGE="${DOCKER_IMAGE:-odoo-das}:${IMAGE_TAG}"
log "Pulling imagen: $FULL_IMAGE"
docker pull "$FULL_IMAGE" || warn "No se pudo hacer pull (usando imagen local si existe)"

# ── Exportar variables para docker compose ───────────────────
export IMAGE_TAG
set -a; source "$ENV_FILE"; set +a

# ── Guardar imagen anterior para rollback ───────────────────
CURRENT_TAG=$(docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" \
    images --format json 2>/dev/null | \
    python3 -c "import sys,json; imgs=json.load(sys.stdin); print(imgs[0]['Tag'] if imgs else 'none')" 2>/dev/null || echo "none")

log "Imagen actual antes del deploy: $CURRENT_TAG"
echo "$CURRENT_TAG" > "$REPO_DIR/.last_tag_${ENVIRONMENT}"

# ── Detener contenedores actuales ───────────────────────────
log "Deteniendo contenedores de $ENVIRONMENT..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down --remove-orphans || true

# ── Levantar nueva versión ───────────────────────────────────
log "Levantando nueva versión..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d

# ── Health check ─────────────────────────────────────────────
log "Esperando que Odoo responda..."
ODOO_CONTAINER="odoo18-${ENVIRONMENT}"
for i in $(seq 1 30); do
    if docker exec "$ODOO_CONTAINER" curl -sf http://localhost:8069/web/health >/dev/null 2>&1; then
        log "Odoo $ENVIRONMENT está activo (intento $i)"
        break
    fi
    if [[ $i -eq 30 ]]; then
        fail "Odoo no respondió después de 5 minutos — revisa: docker logs $ODOO_CONTAINER"
    fi
    echo "  Intento $i/30 — esperando 10s..."
    sleep 10
done

# ── Actualizar módulos si la DB existe ──────────────────────
DB_CONTAINER="odoo18-${ENVIRONMENT}-db"
DB_NAME_VAR="${DB_NAME:-odoo_${ENVIRONMENT}}"

if docker exec "$DB_CONTAINER" psql -U "${DB_USER:-odoo}" -lqt 2>/dev/null | \
        cut -d'|' -f1 | grep -qw "$DB_NAME_VAR"; then
    log "Actualizando módulos personalizados en $DB_NAME_VAR..."
    docker exec "$ODOO_CONTAINER" odoo \
        --config /etc/odoo/odoo.${ENVIRONMENT}.conf \
        --database "$DB_NAME_VAR" \
        --update das_email_preferences,das_email_campaigns,das_lms,das_lms_certificates,das_lms_satisfaction_survey \
        --stop-after-init \
        --log-level=warn || warn "Actualización de módulos completada con advertencias"
else
    warn "Base de datos '$DB_NAME_VAR' no existe todavía — se creará en el primer acceso web"
fi

log "Deploy de $ENVIRONMENT completado exitosamente con imagen $IMAGE_TAG"
