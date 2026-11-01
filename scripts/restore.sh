#!/usr/bin/env bash
# ==============================================================================
# VEID Enterprise - Script de Restauration
# Restaure une archive créée par backup.sh
# Usage: ./scripts/restore.sh /chemin/vers/veid_backup_YYYYMMDD_HHMMSS.tar.gz
# ==============================================================================

set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <fichier_backup.tar.gz>"
    exit 1
fi

BACKUP_FILE="$1"
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Erreur: Le fichier $BACKUP_FILE n'existe pas."
    exit 1
fi

DB_CONTAINER="${DB_CONTAINER:-monerp-db}"
ODOO_CONTAINER="${ODOO_CONTAINER:-monerp-odoo}"
DB_NAME="${POSTGRES_DB:-monerp}"
DB_USER="${POSTGRES_USER:-odoo}"

TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

echo "=================================================="
echo " [VEID] Restauration depuis : $BACKUP_FILE"
echo "=================================================="

# 1. Extraction
echo "-> 1/3 Extraction de l'archive..."
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"

# 2. Restauration base de données
echo "-> 2/3 Restauration de la base de données..."
docker exec -i "$DB_CONTAINER" dropdb -U "$DB_USER" --if-exists "$DB_NAME" || true
docker exec -i "$DB_CONTAINER" createdb -U "$DB_USER" "$DB_NAME"
docker exec -i "$DB_CONTAINER" pg_restore -U "$DB_USER" -d "$DB_NAME" -v < "$TEMP_DIR/database.dump" || true

# 3. Restauration filestore
if [ -f "$TEMP_DIR/filestore.tar.gz" ]; then
    echo "-> 3/3 Restauration du filestore..."
    docker exec -i "$ODOO_CONTAINER" tar -xzf - -C /var/lib/odoo < "$TEMP_DIR/filestore.tar.gz"
fi

# 4. Redémarrage
echo "-> Redémarrage du conteneur VEID..."
docker restart "$ODOO_CONTAINER"

echo "[VEID] Restauration terminée avec succès !"
