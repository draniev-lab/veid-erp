#!/usr/bin/env bash
# ==============================================================================
# VEID Enterprise - Déploiement Automatisé sur Oracle Cloud Free Tier
# Compatible Ubuntu 22.04 / 24.04 LTS (ARM64 Ampere A1 & AMD x86_64)
# ==============================================================================

set -euo pipefail

echo "=========================================================="
echo " [VEID Enterprise] Déploiement sur Oracle Cloud Free Tier"
echo "=========================================================="

# 1. Vérification des droits root / sudo
if [ "$EUID" -ne 0 ]; then
  echo "Veuillez exécuter ce script avec sudo : sudo $0"
  exit 1
fi

# 2. Mise à jour système et dépendances
echo "-> 1/5 Mise à jour des paquets système..."
apt-get update -y && apt-get upgrade -y
apt-get install -y curl wget git ufw iptables-persistent

# 3. Configuration Spécifique Firewall Oracle Cloud
# IMPORTANT: Oracle Cloud applique des règles iptables par défaut qui bloquent le port 80/443 même si UFW est actif
echo "-> 2/5 Ouverture des ports 80 (HTTP) et 443 (HTTPS) pour Oracle Cloud..."
iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp --dport 80 -j ACCEPT
iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT 2>/dev/null || iptables -I INPUT -p tcp --dport 443 -j ACCEPT
netfilter-persistent save 2>/dev/null || true

if command -v ufw >/dev/null 2>&1; then
    ufw allow 22/tcp comment 'SSH'
    ufw allow 80/tcp comment 'HTTP'
    ufw allow 443/tcp comment 'HTTPS'
    ufw --force enable
fi

# 4. Installation Docker & Docker Compose si absents
echo "-> 3/5 Vérification de l'environnement Docker..."
if ! command -v docker >/dev/null 2>&1; then
    echo "Installation de Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
fi

# 5. Préparation de l'environnement
echo "-> 4/5 Vérification des variables d'environnement..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "Création du fichier .env depuis .env.example..."
        cp .env.example .env
        echo "ATTENTION : Pensez à éditer le fichier .env pour y inscrire votre nom de domaine !"
    fi
fi

# 6. Lancement des conteneurs de production
echo "-> 5/5 Lancement des conteneurs VEID Enterprise (Nginx + App + DB)..."
docker compose -f docker-compose.prod.yml up -d --build

echo ""
echo "=========================================================="
echo " [VEID Enterprise] Déploiement terminé avec succès !"
echo "=========================================================="
echo "Accès Web : http://$(curl -s https://api.ipify.org 2>/dev/null || echo '<IP_DU_SERVEUR>')"
echo ""
echo "NOTE ORACLE CLOUD :"
echo "Assurez-vous également d'avoir ajouté les règles d'entrée (Ingress Rules)"
echo "dans votre console Oracle Cloud : VCN > Security Lists > Default Security List"
echo "  - Port 80  (TCP, Source: 0.0.0.0/0)"
echo "  - Port 443 (TCP, Source: 0.0.0.0/0)"
