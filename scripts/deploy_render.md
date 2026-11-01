# Guide de Déploiement VEID Enterprise sur Render.com

Ce guide explique étape par étape comment déployer **VEID Enterprise** sur [Render.com](https://render.com) en exploitant le fichier d'infrastructure `render.yaml`.

---

## 🌟 Pourquoi Render.com est idéal pour VEID

* **Certificat SSL HTTPS 100% Automatique & Gratuit** : aucun Nginx ou Certbot à configurer manuellement.
* **Base de données PostgreSQL Managée** : sauvegardes automatiques gérées par Render.
* **Déploiement Continu (CI/CD)** : chaque `git push` sur GitHub met à jour l'application automatiquement.
* **Sous-domaine gratuit fourni** : `https://veid-enterprise.onrender.com` (ou votre propre nom de domaine personnalisé comme `erp.veid.com`).

---

## 🚀 Procédure de Déploiement en 3 Étapes

### Étape 1 : Pousser votre projet sur GitHub
Si ce n'est pas déjà fait, initialisez votre dépôt Git et poussez votre code sur GitHub :

```bash
git init
git add .
git commit -m "feat: VEID Enterprise ready for Render.com"
git branch -M main
git remote add origin https://github.com/<votre-utilisateur>/veid-enterprise.git
git push -u origin main
```

---

### Étape 2 : Lancer le Blueprint sur Render.com
1. Connectez-vous sur [Render.com](https://dashboard.render.com).
2. Cliquez sur le bouton bleu **« New + »** en haut à droite, puis sélectionnez **« Blueprint »**.
3. Associez votre compte GitHub et choisissez le dépôt **`veid-enterprise`**.
4. Render détecte automatiquement le fichier `render.yaml` :
   * Il va créer la base de données PostgreSQL managée (`veid-postgres`).
   * Il va créer le service Web Docker (`veid-enterprise`).
   * Il va attacher le disque persistant (`veid-filestore`) pour conserver les documents et images.
5. Cliquez sur **« Apply »** pour démarrer la construction automatique.

---

### Étape 3 : Injection des données locales (Optionnel mais Recommandé)
Si vous souhaitez transférer votre base locale (avec le compte `veinardjosue@gmail.com`, le mot de passe `admin`, le logo VEID et les modules déjà installés) vers Render :

1. Sur votre tableau de bord Render, cliquez sur votre base **`veid-postgres`**.
2. Copiez la valeur **« External Database URL »** (commence par `postgres://odoo:...@dpg-...render.com/monerp`).
3. Sur votre machine locale, exécutez un dump et restaurez-le directement vers Render :
   ```bash
   # 1. Export local
   docker exec monerp-db pg_dump -U odoo -d monerp -F c -b > local_dump.dump

   # 2. Import vers Render
   pg_restore -d "<VOTRE_EXTERNAL_DATABASE_URL>" --clean --if-exists local_dump.dump
   ```

---

## 🌐 Configurer votre Nom de Domaine Personnalisé (ex: `erp.veid.com`)
1. Dans le tableau de bord de votre service Web sur Render, allez dans **Settings** > **Custom Domains**.
2. Cliquez sur **Add Custom Domain** et entrez `erp.veid.com`.
3. Ajoutez l'enregistrement **CNAME** indiqué par Render chez votre registraire de domaine (ex: OVH, GoDaddy, Namecheap).
4. Render valide le domaine et émet le certificat SSL HTTPS automatiquement en quelques minutes !
