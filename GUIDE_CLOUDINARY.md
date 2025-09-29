# Guide de Configuration Cloudinary pour TechLearnJess

## Problème Résolu
Les images et vidéos disparaissaient après chaque `git push` sur Render car le stockage local est éphémère. Maintenant, les médias sont stockés sur Cloudinary (cloud externe).

## Configuration Cloudinary

### 1. Créer un compte Cloudinary
1. Aller sur [cloudinary.com](https://cloudinary.com)
2. Créer un compte gratuit
3. Noter vos identifiants depuis le Dashboard

### 2. Configuration des variables d'environnement

#### En développement local (.env)
```env
USE_CLOUDINARY=False
CLOUDINARY_CLOUD_NAME=votre-cloud-name
CLOUDINARY_API_KEY=votre-api-key
CLOUDINARY_API_SECRET=votre-api-secret
```

#### En production sur Render
Dans les variables d'environnement Render :
```
USE_CLOUDINARY=true
CLOUDINARY_CLOUD_NAME=votre-cloud-name
CLOUDINARY_API_KEY=votre-api-key
CLOUDINARY_API_SECRET=votre-api-secret
```

### 3. Comment ça fonctionne

- **Développement** : `USE_CLOUDINARY=False` → stockage local dans `/media/`
- **Production** : `USE_CLOUDINARY=True` → stockage sur Cloudinary

### 4. Utilisation dans les modèles
Aucun changement nécessaire dans vos modèles ! Les `ImageField` et `FileField` fonctionnent automatiquement.

```python
# Exemple - ça marche déjà !
class Course(models.Model):
    image = models.ImageField(upload_to='courses/')  # Sera sur Cloudinary en prod
    video = models.FileField(upload_to='videos/')    # Sera sur Cloudinary en prod
```

### 5. Avantages
- ✅ Images/vidéos ne disparaissent plus après déploiement
- ✅ CDN mondial pour des chargements rapides
- ✅ Optimisation automatique des images
- ✅ 25GB gratuits par mois
- ✅ Pas de changement de code nécessaire

### 6. Déploiement
1. Installer les dépendances : `pip install -r requirements.txt`
2. Configurer les variables d'environnement sur Render
3. Déployer : `git push`

Les anciens fichiers dans `/media/` devront être re-uploadés une fois.