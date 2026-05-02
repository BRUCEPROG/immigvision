# 📖 ImmigVision — Documentation de Déploiement Complète

## Table des matières
1. [Structure du projet](#1-structure-du-projet)
2. [Installation locale](#2-installation-locale)
3. [Déploiement sur Render (gratuit)](#3-déploiement-sur-render-gratuit--recommandé)
4. [Déploiement sur Railway](#4-déploiement-sur-railway)
5. [Déploiement sur VPS (Ubuntu)](#5-déploiement-sur-vps-ubuntu--production)
6. [Configuration SEO & Google](#6-configuration-seo--google)
7. [Comptes et accès](#7-comptes-et-accès-par-défaut)
8. [Guide d'administration](#8-guide-dadministration)
9. [Sécurité](#9-checklist-sécurité-production)
10. [Personnalisation](#10-personnalisation)

---

## 1. Structure du projet

```
immigvision/
├── app.py                    # Application Flask principale
├── requirements.txt          # Dépendances Python
├── Procfile                  # Config Gunicorn (Heroku/Render)
├── .env.example              # Variables d'environnement (modèle)
├── .gitignore
├── immigvision.db            # Base SQLite (créée automatiquement)
├── static/
│   ├── css/style.css         # Feuille de style principale
│   └── js/main.js            # JavaScript interactif
└── templates/
    ├── base.html             # Template de base (navbar, footer)
    ├── index.html            # Page d'accueil
    ├── article.html          # Page article + paywall
    ├── category.html         # Page catégorie
    ├── search.html           # Résultats de recherche
    ├── auth/
    │   ├── login.html        # Connexion
    │   └── register.html     # Inscription
    ├── admin/
    │   ├── dashboard.html    # Tableau de bord admin
    │   ├── articles.html     # Liste des articles
    │   ├── article_form.html # Formulaire d'article
    │   └── users.html        # Gestion utilisateurs
    └── errors/
        ├── 404.html
        ├── 403.html
        └── 500.html
```

---

## 2. Installation locale

### Prérequis
- Python 3.9 ou supérieur
- pip

### Étapes

```bash
# 1. Cloner / copier le projet
cd immigvision/

# 2. Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# OU : venv\Scripts\activate    # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
# Éditez .env et changez SECRET_KEY !

# 5. Lancer le serveur de développement
python app.py
```

Le site est accessible sur : **http://localhost:5000**

---

## 3. Déploiement sur Render (Gratuit — Recommandé)

Render offre un hébergement gratuit pour Flask. **Parfait pour démarrer.**

### Étape 1 — Préparer le dépôt Git

```bash
cd immigvision/
git init
git add .
git commit -m "Initial commit ImmigVision"
```

Créez un dépôt sur GitHub (github.com) et poussez le code :

```bash
git remote add origin https://github.com/VOTRE_NOM/immigvision.git
git branch -M main
git push -u origin main
```

### Étape 2 — Créer le service sur Render

1. Allez sur **https://render.com** → Créez un compte gratuit
2. Cliquez **"New +"** → **"Web Service"**
3. Connectez votre dépôt GitHub
4. Configurez :
   - **Name** : `immigvision`
   - **Region** : `Frankfurt (EU Central)` (plus proche de l'Afrique)
   - **Branch** : `main`
   - **Runtime** : `Python 3`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn app:app --workers 2 --bind 0.0.0.0:$PORT`

### Étape 3 — Variables d'environnement sur Render

Dans l'onglet **"Environment"**, ajoutez :

| Clé | Valeur |
|-----|--------|
| `SECRET_KEY` | `votre-cle-secrete-tres-longue-et-aleatoire` |
| `DATABASE_PATH` | `/opt/render/project/src/immigvision.db` |
| `FLASK_DEBUG` | `false` |

### Étape 4 — Déployer

Cliquez **"Create Web Service"**. Render déploie automatiquement.

> ⚠️ **Limite du plan gratuit Render** : La base SQLite est sur le disque éphémère. Pour persister les données, utilisez le plan payant avec un disque persistant, ou migrez vers PostgreSQL.

### Ajouter un disque persistant (Render — Payant)

Dans les paramètres du service :
1. **"Disks"** → **"Add Disk"**
2. Mount Path : `/data`
3. Mettez `DATABASE_PATH=/data/immigvision.db` dans les variables d'env

---

## 4. Déploiement sur Railway

Railway offre 5$/mois de crédit gratuit par mois.

```bash
# 1. Installer Railway CLI
npm install -g @railway/cli
# ou : curl -fsSL https://railway.app/install.sh | sh

# 2. Se connecter
railway login

# 3. Initialiser le projet
cd immigvision/
railway init

# 4. Configurer les variables
railway variables set SECRET_KEY="votre-cle-secrete"
railway variables set FLASK_DEBUG="false"

# 5. Déployer
railway up
```

---

## 5. Déploiement sur VPS Ubuntu (Production)

Pour un **VPS Contabo, OVH, DigitalOcean** (à partir de 3-5€/mois).

### 5.1 — Préparer le serveur

```bash
# Se connecter en SSH
ssh root@VOTRE_IP

# Mettre à jour le système
apt update && apt upgrade -y

# Installer Python, Nginx, Git
apt install -y python3 python3-pip python3-venv nginx git certbot python3-certbot-nginx

# Créer un utilisateur dédié
adduser immigvision
usermod -aG sudo immigvision
su - immigvision
```

### 5.2 — Installer l'application

```bash
# Cloner le projet
cd /home/immigvision
git clone https://github.com/VOTRE_NOM/immigvision.git app
cd app

# Environnement virtuel
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Configurer .env
cp .env.example .env
nano .env
# → Modifiez SECRET_KEY avec une valeur aléatoire longue
# → DATABASE_PATH=/home/immigvision/app/immigvision.db
```

### 5.3 — Service Systemd (démarrage automatique)

```bash
sudo nano /etc/systemd/system/immigvision.service
```

```ini
[Unit]
Description=ImmigVision Flask Application
After=network.target

[Service]
User=immigvision
WorkingDirectory=/home/immigvision/app
Environment="PATH=/home/immigvision/app/venv/bin"
EnvironmentFile=/home/immigvision/app/.env
ExecStart=/home/immigvision/app/venv/bin/gunicorn \
          app:app \
          --workers 3 \
          --bind unix:/home/immigvision/app/immigvision.sock \
          --timeout 60 \
          --access-logfile /var/log/immigvision/access.log \
          --error-logfile /var/log/immigvision/error.log
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Créer le dossier de logs
sudo mkdir -p /var/log/immigvision
sudo chown immigvision:immigvision /var/log/immigvision

# Activer et démarrer
sudo systemctl daemon-reload
sudo systemctl enable immigvision
sudo systemctl start immigvision
sudo systemctl status immigvision   # Vérifier que c'est "Active"
```

### 5.4 — Configurer Nginx (reverse proxy)

```bash
sudo nano /etc/nginx/sites-available/immigvision
```

```nginx
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;

    # Fichiers statiques servis directement par Nginx (plus rapide)
    location /static/ {
        alias /home/immigvision/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        gzip_static on;
    }

    # Tout le reste → Flask via socket Unix
    location / {
        proxy_pass http://unix:/home/immigvision/app/immigvision.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60;
        proxy_connect_timeout 60;
        proxy_buffering on;
        client_max_body_size 16M;
    }

    # Sécurité
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Compression gzip
    gzip on;
    gzip_types text/css application/javascript application/json text/html;
}
```

```bash
# Activer le site
sudo ln -s /etc/nginx/sites-available/immigvision /etc/nginx/sites-enabled/
sudo nginx -t      # Tester la config
sudo systemctl reload nginx
```

### 5.5 — HTTPS avec Let's Encrypt (SSL gratuit)

```bash
# Votre domaine doit pointer vers votre IP (DNS configuré)
sudo certbot --nginx -d votre-domaine.com -d www.votre-domaine.com

# Renouvellement automatique (vérifier)
sudo certbot renew --dry-run
```

### 5.6 — Mises à jour futures

```bash
cd /home/immigvision/app
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart immigvision
```

---

## 6. Configuration SEO & Google

### 6.1 — Configurer votre domaine

Achetez un domaine sur : **Namecheap**, **OVH**, **Gandi** (~10€/an).

Configurez les DNS :
```
Type    Nom    Valeur
A       @      VOTRE_IP_VPS
A       www    VOTRE_IP_VPS
```

### 6.2 — Google Search Console

1. Allez sur **https://search.google.com/search-console/**
2. Ajoutez votre propriété : `votre-domaine.com`
3. Vérifiez via **balise HTML** : ajoutez la meta dans `base.html` :
   ```html
   <meta name="google-site-verification" content="VOTRE_CODE" />
   ```
4. Soumettez votre sitemap : `https://votre-domaine.com/sitemap.xml`

### 6.3 — Google Analytics (optionnel)

Ajoutez dans `base.html`, avant `</head>` :

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-VOTRE_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-VOTRE_ID');
</script>
```

### 6.4 — Optimisation SEO intégrée

Le site intègre déjà :
- ✅ Balises `<meta>` description et keywords
- ✅ Open Graph (Facebook, LinkedIn)
- ✅ Twitter Cards
- ✅ JSON-LD Schema.org (WebSite + Article)
- ✅ Canonical URLs
- ✅ Sitemap XML automatique (`/sitemap.xml`)
- ✅ robots.txt (`/robots.txt`)
- ✅ URLs propres avec slugs (`/article/titre-article`)
- ✅ Images lazy-loading
- ✅ Temps de lecture calculé automatiquement

---

## 7. Comptes et accès par défaut

> ⚠️ **Changez ces mots de passe immédiatement après installation !**

| Rôle | Email | Mot de passe |
|------|-------|-------------|
| Admin | `admin@immigvision.com` | `Admin@2026!` |

### Changer le mot de passe admin

Via l'interface admin → **Utilisateurs** → ou directement en Python :

```python
from app import app, execute
from werkzeug.security import generate_password_hash
with app.app_context():
    execute("UPDATE users SET password_hash=? WHERE email=?",
            [generate_password_hash("NouveauMotDePasse!"), "admin@immigvision.com"])
print("Mot de passe mis à jour !")
```

---

## 8. Guide d'administration

### Accéder au panel admin
URL : `https://votre-domaine.com/admin`

### Créer un article

1. Admin → **Nouvel article**
2. Remplissez : Titre, Contenu (éditeur riche), Catégorie
3. Ajoutez une image (URL depuis Unsplash, Pexels...)
4. Remplissez la méta-description (important pour le SEO)
5. Cochez **"Publier"** et optionnellement **"Mettre à la une"**
6. Cliquez **"Créer l'article"**

### Conseils pour les images gratuites
- **Unsplash** : https://unsplash.com (images HD gratuites)
- **Pexels** : https://pexels.com
- Copiez l'URL directe de l'image (clic droit → Copier l'adresse de l'image)

### Catégories disponibles
| Catégorie | Slug | Contenu recommandé |
|-----------|------|-------------------|
| Immigration | `/categorie/immigration` | Actualités générales |
| Visas | `/categorie/visas` | Procédures visa |
| Bourses | `/categorie/bourses` | Bourses d'études |
| Actualités | `/categorie/actualites` | Nouvelles fraîches |
| Guides | `/categorie/guides` | Tutoriels pratiques |

### Gérer les utilisateurs
- Admin → **Utilisateurs**
- Promouvoir/rétrograder un admin
- Voir les abonnés newsletter
- Exporter les emails en .txt

---

## 9. Checklist Sécurité Production

```bash
# ✅ 1. Changer la SECRET_KEY (dans .env)
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo "SECRET_KEY=$SECRET_KEY"

# ✅ 2. Désactiver le debug
FLASK_DEBUG=false

# ✅ 3. HTTPS activé (Let's Encrypt)

# ✅ 4. Changer le mot de passe admin

# ✅ 5. Sauvegardes automatiques de la DB
crontab -e
# Ajoutez :
# 0 2 * * * cp /home/immigvision/app/immigvision.db /backup/immigvision_$(date +\%Y\%m\%d).db
```

---

## 10. Personnalisation

### Changer le nom du site

Dans `app.py`, modifiez :
```python
SITE_NAME = 'ImmigVision'
SITE_TAGLINE = 'Votre portail de référence sur l\'immigration...'
```

### Modifier les couleurs

Dans `static/css/style.css`, section `:root` :
```css
:root {
  --navy:  #1A3A5C;   /* Couleur principale */
  --teal:  #00C2CB;   /* Couleur accent */
  --amber: #F5A623;   /* Couleur accentuation */
}
```

### Ajouter une catégorie

Via SQLite ou dans `init_db()` dans `app.py` :
```python
execute("INSERT INTO categories (name, slug, description, icon, color) VALUES (?,?,?,?,?)",
        ['Emploi', 'emploi', 'Offres et conseils emploi', 'fas fa-briefcase', '#8E44AD'])
```

### Modifier la limite du paywall

Dans `app.py` :
```python
PREVIEW_CHARS = 1200   # Augmentez pour montrer plus de contenu
```

### Passer à PostgreSQL (recommandé en production)

Installez `psycopg2-binary` et modifiez `get_db()` et les queries SQL.
Ou utilisez SQLAlchemy pour plus de flexibilité.

---

## Support & Ressources

- **Flask** : https://flask.palletsprojects.com
- **Render** : https://render.com/docs
- **Let's Encrypt** : https://letsencrypt.org
- **Google Search Console** : https://search.google.com/search-console
- **Unsplash API** : https://unsplash.com/developers

---

*Documentation générée pour ImmigVision — Avril 2026*
