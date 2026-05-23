import os
import zipfile
import shutil
import subprocess
import sys
from pathlib import Path

# ==============================
# CONFIG (ajusta si necesitas)
# ==============================

DB_NAME = "odoo"
DB_CONTAINER = "odoo18-das-db"
ODOO_CONTAINER = "odoo18-das"

BASE_DIR = Path(__file__).resolve().parent.parent
ODOO_FILESTORE = BASE_DIR / "docker/volumes/odoo/.local/share/Odoo/filestore"

TMP_DIR = BASE_DIR / "tmp_restore"

# ==============================


def run(cmd):
    print(f"👉 {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print("❌ Error ejecutando comando")
        sys.exit(1)


# ==============================


def extract_zip(zip_path):
    print("📦 Extrayendo ZIP...")

    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)

    TMP_DIR.mkdir()

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(TMP_DIR)


# ==============================


def find_files():
    dump = None
    filestore = None

    for root, dirs, files in os.walk(TMP_DIR):
        if "dump.sql" in files:
            dump = Path(root) / "dump.sql"
        if "filestore" in dirs:
            filestore = Path(root) / "filestore"

    if not dump:
        raise Exception("❌ dump.sql no encontrado")
    if not filestore:
        raise Exception("❌ filestore no encontrado")

    return dump, filestore


# ==============================


def stop_odoo():
    print("🛑 Deteniendo Odoo...")
    run(f"docker stop {ODOO_CONTAINER}")


# ==============================


def restore_db(dump_file):
    print("🧠 Restaurando base de datos...")

    # Terminar conexiones y recrear DB
    # 1. Matar conexiones
    run(f"""
    docker exec -i {DB_CONTAINER} psql -U odoo postgres -c "
    SELECT pg_terminate_backend(pid)
    FROM pg_stat_activity
    WHERE datname = '{DB_NAME}';
    "
    """)

    # 2. Drop DB
    run(f"""
    docker exec -i {DB_CONTAINER} psql -U odoo postgres -c "
    DROP DATABASE IF EXISTS {DB_NAME};
    "
    """)

    # 3. Create DB
    run(f"""
    docker exec -i {DB_CONTAINER} psql -U odoo postgres -c "
    CREATE DATABASE {DB_NAME};
    "
    """)

    # Copiar dump
    run(f"docker cp {dump_file} {DB_CONTAINER}:/dump.sql")

    # Restaurar
    run(f"docker exec -i {DB_CONTAINER} psql -U odoo -d {DB_NAME} -f /dump.sql")


# ==============================


def restore_filestore(filestore_src):
    print("🗂️ Restaurando filestore...")

    target = ODOO_FILESTORE / DB_NAME

    if target.exists():
        shutil.rmtree(target)

    target.mkdir(parents=True)

    for item in filestore_src.iterdir():
        dest = target / item.name
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)


# ==============================


def fix_permissions():
    print("🔐 Ajustando permisos (solo Linux)...")

    if os.name != "nt":  # no Windows
        run(f"sudo chown -R 100:101 {BASE_DIR}/docker/volumes/odoo")


# ==============================


def start_odoo():
    print("🚀 Iniciando Odoo...")
    run(f"docker start {ODOO_CONTAINER}")


# ==============================


# def rebuild_assets():
#     print("♻️ Recompilando assets...")
#     run(f"docker exec -i {ODOO_CONTAINER} odoo -u web -d {DB_NAME} --stop-after-init")


# ==============================


def main():
    if len(sys.argv) < 2:
        print("Uso: python restore_odoo.py <ruta_zip>")
        sys.exit(1)

    zip_path = Path(sys.argv[1]).resolve()

    if not zip_path.exists():
        print("❌ ZIP no existe")
        sys.exit(1)

    extract_zip(zip_path)
    dump, filestore = find_files()

    stop_odoo()
    restore_db(dump)
    restore_filestore(filestore)
    fix_permissions()
    start_odoo()
    # rebuild_assets()

    print("\n✅ Restauración completada con éxito.")


# ==============================

if __name__ == "__main__":
    main()
