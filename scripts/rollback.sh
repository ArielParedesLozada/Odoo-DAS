#!/usr/bin/env bash
# ============================================================
# rollback.sh — Revertir al tag de imagen anterior
# Uso: ./scripts/rollback.sh [prod|staging] [tag_opcional]
# Sin tag: usa el guardado en .last_tag_<entorno>
# ============================================================
set -euo pipefail

ENVIRONMENT="${1:-prod}"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

RED='\033[0;31m'; YELLOW='\033[1;33m'; GREEN='\033[0;32m'; NC='\033[0m'
log()  { echo -e "${GREEN}[ROLLBACK]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
fail() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# Determinar tag al que volver
if [[ -n "${2:-}" ]]; then
    ROLLBACK_TAG="$2"
else
    LAST_TAG_FILE="$REPO_DIR/.last_tag_${ENVIRONMENT}"
    [[ -f "$LAST_TAG_FILE" ]] || fail "No se encontró .last_tag_${ENVIRONMENT} — especifica el tag manualmente"
    ROLLBACK_TAG=$(cat "$LAST_TAG_FILE")
    [[ "$ROLLBACK_TAG" != "none" ]] || fail "El tag guardado es 'none' — no hay versión anterior registrada"
fi

warn "ROLLBACK a tag '$ROLLBACK_TAG' en entorno '$ENVIRONMENT'"
read -rp "¿Confirmar? (s/N): " CONFIRM
[[ "$CONFIRM" == "s" || "$CONFIRM" == "S" ]] || { log "Rollback cancelado"; exit 0; }

log "Ejecutando deploy con imagen: $ROLLBACK_TAG"
exec "$REPO_DIR/scripts/deploy.sh" "$ENVIRONMENT" "$ROLLBACK_TAG"
