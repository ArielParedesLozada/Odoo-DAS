# DEVELOPER SETUP: DOCKER MANDATE

**Status**: MANDATORY
**Project**: Somatech Odoo Ecuador
**Context**: All development and verification MUST be performed within the approved Docker Cluster.

## 1. Cluster Configuration
- **Container Name**: `somatech_odoo_ec_web`
- **Port**: `24500` (Web), `24501` (Chat)
- **Database**: `somatech_odoo_ec_db`
- **Odoo Version**: 18.0

## 2. Launch Command
```bash
docker compose up -d
```

## 3. Verification Command (Smoke Test)
Before committing ANY code, you must run:
```bash
docker exec -it somatech_odoo_ec_web odoo -i l10n_ec_base,l10n_ec_edi,l10n_ec_withholding -d somatech_db --stop-after-init
```
*If this command fails, the code is broken.*

## 4. Debugging
Logs are available via:
```bash
docker compose logs -f web
```
