#!/usr/bin/env bash
# ==============================================================================
# VEID Enterprise - Script de Sauvegarde Automatique
# Sauvegarde la base de données PostgreSQL et le filestore (pièces jointes)
# ==============================================================================

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/var/backups/veid}"
DATE_TAG=$(date +"%Y%m%d_%H%M%S")
DB_CONTAINER="${DB_CONTAINER:-monerp-db}"
ODOO_CONTAINER="${ODOO_CONTAINER:-monerp-odoo}"
DB_NAME="${POSTGRES_DB:-monerp}"
DB_USER="${POSTGRES_USER:-odoo}"
RETENTION_DAYS=7

mkdir -p "$BACKUP_DIR"
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

echo "=================================================="
echo " [VEID] Démarrage de la sauvegarde : $DATE_TAG"
echo "=================================================="

# 1. Dump PostgreSQL
echo "-> 1/3 Export de la base de données ($DB_NAME)..."
docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" -F c -b -v > "$TEMP_DIR/database.dump"

# 2. Export Filestore Odoo
echo "-> 2/3 Export du filestore (pièces jointes & images)..."
docker exec "$ODOO_CONTAINER" tar -czf - -C /var/lib/odoo filestore > "$TEMP_DIR/filestore.tar.gz" 2>/dev/null || true

# 3. Création de l'archive finale
BACKUP_FILE="$BACKUP_DIR/veid_backup_${DATE_TAG}.tar.gz"
echo "-> 3/3 Compression de l'archive finale..."
tar -czf "$BACKUP_FILE" -C "$TEMP_DIR" database.dump filestore.tar.gz

BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "[VEID] Sauvegarde réussie : $BACKUP_FILE ($BACKUP_SIZE)"

# 4. Rotation / Nettoyage des sauvegardes de plus de 7 jours
echo "-> Nettoyage des anciennes sauvegardes (> $RETENTION_DAYS jours)..."
find "$BACKUP_DIR" -name "veid_backup_*.tar.gz" -mtime +"$RETENTION_DAYS" -exec rm -f {} \;

echo "[VEID] Terminé avec succès !"
