# VEID Enterprise - Solution de Gestion Intégrée & Pilotage Métier

<p align="center">
  <img src="custom_addons/monerp/monerp_core/static/src/img/veid_logo_horizontal.png" alt="VEID Enterprise Logo" width="340"/>
</p>

<p align="center">
  <strong>ERP Moderne, Modulaire et Performant pour PME, Commerçants et Grands Comptes</strong><br>
  <em>Basé sur le socle Odoo 19 &amp; PostgreSQL 16 - Déployable sur Oracle Cloud Free Tier</em>
</p>

---

## 🌟 Vue d'Ensemble

**VEID Enterprise** est une suite progicielle intégrée complète conçue pour couvrir l'ensemble des besoins de gestion d'une entreprise :
* **Commerce & Vente** : Point de Vente (POS / Caisse enregistreuse), Devis, Facturation client.
* **Stocks & Logistique** : Gestion multi-entrepôts, réapprovisionnement automatique, alertes de rupture de stock.
* **Comptabilité & Finance** : Localisation conforme **SYSCOHADA / OHADA**, devises **Franc CFA (XOF / XAF)**, TVA et retenues à la source.
* **Achats & Fournisseurs** : Demandes de prix, réceptions de marchandises, contrôle des factures.
* **Ressources Humaines** : Dossiers collaborateurs, présences, congés et gestion des équipes.
* **CRM & Relations Clients** : Pipeline d'opportunités, suivi commercial et messagerie omnicanale.
* **Modules Sectoriels Dédiés** :
  * 🌾 **Agricole** : Suivi des parcelles, campagnes, récoltes et intrants.
  * 🏗️ **BTP / Chantiers** : Suivi des chantiers, engins, matériaux et avancements.
  * 🚚 **Transport & Logistique** : Gestion de flotte, missions, carburant et chauffeurs.

---

## 📁 Architecture du Projet

```text
MonErp/
├── config/
│   └── odoo.conf                # Configuration système Odoo / VEID
├── custom_addons/
│   └── monerp/                  # Modules personnalisés VEID
│       ├── monerp_core/         # Socle, identité visuelle, logos VEID & thèmes
│       ├── monerp_sale/         # Ventes & gestion commerciale
│       ├── monerp_stock/        # Gestion des stocks & inventaires
│       ├── monerp_account/      # Facturation & comptabilité
│       ├── monerp_l10n/         # Localisation OHADA / Franc CFA (NIF, RCCM, TVA)
│       ├── monerp_purchase/     # Achats & réceptions
│       ├── monerp_hr/           # Ressources Humaines
│       ├── monerp_crm/          # Gestion de la relation client
│       ├── monerp_reporting/    # Tableaux de bord & indicateurs KPI
│       └── modules_sectoriels/  # Modules BTP, Agriculture et Transport
├── docker/
│   └── Dockerfile               # Image Docker personnalisée VEID
├── nginx/
│   └── nginx.conf               # Configuration Nginx optimisée (WebSockets, SSL, Gzip)
├── scripts/
│   ├── backup.sh                # Sauvegarde automatique (DB + filestore, rétention 7j)
│   ├── restore.sh               # Restauration complète en une commande
│   └── deploy_oracle.sh         # Script de déploiement automatique sur Oracle Cloud
├── docker-compose.yml           # Déploiement développement local
├── docker-compose.prod.yml      # Déploiement production (Nginx + SSL Certbot)
├── .env.example                 # Modèle des variables d'environnement
└── README.md                    # Documentation officielle
```

---

## 🚀 Démarrage Rapide (Développement Local)

### Prérequis
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installé et en cours d'exécution.
* Git.

### 1. Configuration des variables d'environnement
```bash
cp .env.example .env
```

### 2. Démarrage des conteneurs
```bash
docker compose up -d
```

### 3. Accès à l'application
* URL : **http://localhost:8069**
* **Identifiant par défaut** : `veinardjosue@gmail.com`
* **Mot de passe** : `admin`

---

## 🚀 Déploiement en 1 Clic sur Render.com (Recommandé)

Le projet intègre un fichier d'Infrastructure-as-Code [render.yaml](file:///e:/projet/project/MonErp/render.yaml) pour déployer **VEID Enterprise** en 1 clic :

1. Poussez votre code sur votre compte **GitHub**.
2. Rendez-vous sur votre tableau de bord [Render.com](https://dashboard.render.com).
3. Cliquez sur **New +** > **Blueprint**, puis sélectionnez votre dépôt.
4. Render configure automatiquement :
   * L'application web Docker sécurisée en **HTTPS gratuit**.
   * La base de données **PostgreSQL managée**.
   * Le **disque persistant** pour vos fichiers et images.
5. Cliquez sur **Apply** : votre ERP est en ligne !

Pour plus de détails, consultez le [Guide de Déploiement Render](file:///e:/projet/project/MonErp/scripts/deploy_render.md).

---

## ☁️ Déploiement Alternatif sur Serveur Cloud / VPS Linux (Oracle Cloud)

VEID Enterprise peut également tourner sur un serveur dédié ou VPS (ex: **Oracle Cloud Free Tier** Ubuntu 22.04 / 24.04 LTS).

### 1. Configuration des règles réseau Oracle Cloud (Console Web)
Dans la console Oracle Cloud :
1. Rendez-vous dans **Networking** > **Virtual Cloud Networks (VCN)** > Votre VCN.
2. Cliquez sur **Security Lists** > **Default Security List**.
3. Dans **Ingress Rules**, ajoutez les 2 règles suivantes :
   * **Port 80 (HTTP)** : Source `0.0.0.0/0`, Protocole `TCP`, Destination Port `80`.
   * **Port 443 (HTTPS)** : Source `0.0.0.0/0`, Protocole `TCP`, Destination Port `443`.

### 2. Déploiement automatique sur le serveur VPS
Connectez-vous en SSH à votre instance Oracle Cloud et lancez :

```bash
git clone <URL_DU_DEPOT> /opt/veid
cd /opt/veid
sudo chmod +x scripts/*.sh
sudo ./scripts/deploy_oracle.sh
```

Le script installe automatiquement Docker, configure les règles de pare-feu iptables Oracle Cloud, configure Nginx et démarre la solution.

---

## 💾 Sauvegardes & Restauration

### Sauvegarde automatique quotidienne
Le script `scripts/backup.sh` génère une archive complète horodatée (base PostgreSQL + filestore des pièces jointes) et supprime automatiquement les sauvegardes datant de plus de 7 jours :

```bash
sudo ./scripts/backup.sh
```

Pour planifier une sauvegarde automatique chaque nuit à 02h00 du matin, ajoutez cette ligne à votre crontab (`crontab -e`) :
```cron
0 2 * * * /opt/veid/scripts/backup.sh >> /var/log/veid_backup.log 2>&1
```

### Restauration d'une sauvegarde
```bash
sudo ./scripts/restore.sh /var/backups/veid/veid_backup_YYYYMMDD_HHMMSS.tar.gz
```

---

## 🔐 Sécurité & Bonnes Pratiques en Production

1. **Changez le mot de passe administrateur** dès votre première connexion en production.
2. **Ne commitez jamais le fichier `.env`** dans Git (il est déjà exclu dans `.gitignore`).
3. **Master Password** : Définissez une clé complexe pour `ADMIN_PASSWD` dans le `.env` pour verrouiller l'accès au gestionnaire de bases `/web/database/manager`.

---

## 📄 Licence & Droits
Propulsé par la technologie **VEID Enterprise** - Tous droits réservés.
Site officiel : [https://veid.com](https://veid.com)
