#!/usr/bin/env bash
# ==============================================================================
# VEID Enterprise - Container Entrypoint
# Compatible avec Render.com, Docker local et VPS
# ==============================================================================

set -e

# Port attribué dynamiquement par Render ($PORT) ou 8069 par défaut
HTTP_PORT="${PORT:-8069}"

# Traitement de la connexion Base de Données
if [ -n "${DATABASE_URL:-}" ]; then
    echo "[VEID] Configuration automatique depuis DATABASE_URL (Render)..."
    eval $(python3 -c "
import os, urllib.parse
url = urllib.parse.urlparse(os.environ['DATABASE_URL'])
print(f'DB_HOST=\"{url.hostname}\"')
print(f'DB_PORT=\"{url.port or 5432}\"')
print(f'DB_USER=\"{url.username}\"')
print(f'DB_PASSWORD=\"{url.password}\"')
print(f'DB_NAME=\"{url.path.lstrip(\"/\")}\"')
")
else
    DB_HOST="${HOST:-${POSTGRES_HOST:-db}}"
    DB_PORT="${POSTGRES_PORT:-5432}"
    DB_USER="${USER:-${POSTGRES_USER:-odoo}}"
    DB_PASSWORD="${PASSWORD:-${POSTGRES_PASSWORD:-odoo}}"
    DB_NAME="${POSTGRES_DB:-monerp}"
fi

# Création des dossiers persistants requis
mkdir -p /var/lib/odoo/filestore
mkdir -p /var/lib/odoo/sessions

echo "=================================================="
echo " [VEID Enterprise] Démarrage du serveur"
echo " Port d'écoute : $HTTP_PORT"
echo " Base de données : $DB_USER@$DB_HOST:$DB_PORT/$DB_NAME"
echo "=================================================="

# Démarrage officiel d'Odoo / VEID
exec /opt/odoo/odoo-bin \
    -c /etc/odoo/odoo.conf \
    --http-port="$HTTP_PORT" \
    --db_host="$DB_HOST" \
    --db_port="$DB_PORT" \
    --db_user="$DB_USER" \
    --db_password="$DB_PASSWORD" \
    -d "$DB_NAME" \
    --proxy-mode \
    "$@"
