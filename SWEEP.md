# SWEEP.md - TechLearnJess

## Commandes utiles

### Création de dossiers multiples (Windows PowerShell)
```powershell
mkdir dossier1, dossier2, dossier3
```

### Commandes Django essentielles
```bash
# Créer les migrations pour toutes les applications
python manage.py makemigrations core accounts courses forum chat certificates notifications payments live_sessions

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur de développement
python manage.py runserver
```

Create a virtual environment

```
python3.9 -m venv venv
```

### Activate a virtual environment

Linux/mac user 

```
source venv/bin/activate
```

Window user 

```
venv\Scripts\activate
```

### Install requirements 

```
pip install -r requirements.txt
```

### Configuration Cloudinary (Stockage des médias)

**Problème résolu** : Les images/vidéos disparaissaient après `git push` sur Render car le stockage local est éphémère.

**Solution** : Stockage externe sur Cloudinary

#### Variables d'environnement nécessaires :
```env
# Développement local
USE_CLOUDINARY=False

# Production sur Render
USE_CLOUDINARY=true
CLOUDINARY_CLOUD_NAME=votre-cloud-name
CLOUDINARY_API_KEY=votre-api-key
CLOUDINARY_API_SECRET=votre-api-secret
```

Voir `GUIDE_CLOUDINARY.md` pour les détails complets.

### Optimisation SEO - Chadrack Mbu Jess

**Référencement Google optimisé** pour toutes les variantes du nom du fondateur :

#### Mots-clés ciblés :
**Fondateur :**
- Chadrack Mbu Jess, Chadrackmbujess, Chadrack mbujess
- Chadrackmbu jess, Chadrack, Chadrack mbu, mbu jess
- mbu, mbu pioka, pioka

**Entreprise :**
- TechLearnJess, Tech LearnJess, TechLearn Jess
- Tech Learn Jess, techlearnjess

**Secteur :**
- formation RDC, cours technologie Congo, développement web Matadi

#### Fichiers SEO configurés :
- `/sitemap.xml` - Sitemap dynamique
- `/robots.txt` - Optimisé pour les moteurs de recherche
- Métadonnées complètes (Open Graph, Twitter Cards, Schema.org)
- Données structurées pour l'organisation et le fondateur

Voir `GUIDE_SEO.md` pour les détails complets et les actions à suivre.

### Structure du projet
- **Backend**: Django (Python)
- **Base de données**: SQLite3 (développement)
- **Frontend**: HTML5, TailwindCSS, JavaScript Vanilla
- **Communication temps réel**: WebSockets (Django Channels)
- **Paiement**: E-money (Orange Money, Airtel Money, M-Pesa)

### Applications Django créées
- `core` - Fonctionnalités principales
- `accounts` - Gestion des utilisateurs
- `courses` - Gestion des cours
- `forum` - Forum de discussion
- `chat` - Chat en temps réel
- `certificates` - Génération de certificats
- `notifications` - Système de notifications
- `payments` - Gestion des paiements
- `live_sessions` - Sessions live

### Structure des templates
```
templates/
├── base.html                    # Template de base ultra moderne avec Tailwind CSS
├── core/
│   ├── home.html               # Page d'accueil avec hero section et fonctionnalités
│   ├── about.html              # Page à propos avec équipe et valeurs
│   ├── dashboard.html          # Tableau de bord utilisateur personnalisé
│   └── faq.html                # Questions fréquentes avec recherche
├── accounts/
│   ├── login.html              # Connexion avec design moderne
│   ├── register.html           # Inscription avec validation
│   └── profile.html            # Profil utilisateur complet
├── courses/                    # Templates pour les cours
├── chat/                       # Templates pour le chat temps réel
├── forum/                      # Templates pour le forum
├── certificates/               # Templates pour les certificats
├── payments/                   # Templates pour les paiements
├── live_sessions/              # Templates pour les sessions live
└── notifications/              # Templates pour les notifications
```

### Design et Technologies Frontend
- **Framework CSS**: TailwindCSS (via CDN)
- **JavaScript**: Alpine.js pour l'interactivité
- **Icônes**: Font Awesome 6.4.0
- **Polices**: Inter (corps) + Poppins (titres)
- **Animations**: CSS personnalisées + Tailwind
- **Mode sombre**: Support complet avec Alpine.js
- **Responsive**: Mobile-first design
- **Effets**: Glass morphism, gradients, hover effects

### Fonctionnalités des templates
- Navigation sticky avec dropdown utilisateur
- Messages flash animés
- Barres de progression interactives
- Recherche en temps réel (FAQ)
- Animations au scroll
- Compteurs animés
- Mode sombre/clair
- Design ultra moderne et professionnel