# RAPPORT DE PROJET DE FIN D'ÉTUDES (PFE)

## Système de Gestion de Stock et de Production — Magasin Crème

---

## TABLE DES MATIÈRES

1. [Introduction & Contexte](#1-introduction--contexte)
2. [Analyse des Besoins](#2-analyse-des-besoins)
3. [Architecture Générale du Projet](#3-architecture-générale-du-projet)
4. [Technologies Utilisées](#4-technologies-utilisées)
5. [Modélisation des Données (MCD/MLD)](#5-modélisation-des-données-mcdmld)
6. [Architecture Logicielle — Vues et URLs](#6-architecture-logicielle--vues-et-urls)
7. [Formulaires et Validation](#7-formulaires-et-validation)
8. [Système d'Authentification et d'Autorisation](#8-système-dauthentification-et-dautorisation)
9. [Middleware et Sécurité](#9-middleware-et-sécurité)
10. [Logique Métier — Gestion des Lots](#10-logique-métier--gestion-des-lots)
11. [Interfaces Utilisateur](#11-interfaces-utilisateur)
12. [Tableaux de Bord et Analytiques](#12-tableaux-de-bord-et-analytiques)
13. [Tests et Déploiement](#13-tests-et-déploiement)
14. [Bilan et Perspectives](#14-bilan-et-perspectives)

---

## 1. Introduction & Contexte

### 1.1 Présentation du Projet

Ce projet consiste en la conception et le développement d'une **application web de gestion de stock et de production** destinée à une unité industrielle de fabrication de produits cosmétiques (crème). L'application, nommée **Magasin Crème**, vise à digitaliser et automatiser les processus de réception des matières premières, de transfert vers la production, et de suivi analytique de la consommation.

### 1.2 Problématique

Avant la mise en place de ce système, la gestion du stock était réalisée manuellement via des registres papier, ce qui engendrait :
- Des **erreurs de saisie** et des pertes d'informations
- Une **impossibilité de tracer** les lots en temps réel
- Un **manque de visibilité** sur les péremptions
- Une **communication inefficace** entre le magasin et la production
- L'**absence d'indicateurs de performance** pour les responsables

### 1.3 Objectifs

L'application développée répond aux objectifs suivants :

| Objectif | Description |
|----------|-------------|
| **Digitalisation** | Remplacer les processus papier par une interface web |
| **Traçabilité** | Suivre chaque lot de matière première de la réception à l'utilisation |
| **Alertes** | Notifier les responsables des lots périmés ou proches de la péremption |
| **Analytics** | Fournir des indicateurs de performance à la production |
| **Sécurité** | Contrôler l'accès selon les rôles (Magasin / Production / Admin) |
| **Ergonomie** | Interface moderne, intuitive et responsive |

---

## 2. Analyse des Besoins

### 2.1 Identification des Acteurs

L'application distingue **trois types d'utilisateurs** :

#### Magasinier (Rôle : `magasin`)
- Saisit les réceptions de matières premières
- Transfère les lots vers la production
- Consulte le stock actuel et les alertes
- Accède au tableau de bord principal

#### Opérateur de Production (Rôle : `production`)
- Enregistre les ouvertures de lots en production
- Consulte le stock disponible dans la zone production
- Accède aux analytics de performance
- Visualise l'historique de production

#### Administrateur (Rôle : `admin`)
- Accède à toutes les fonctionnalités des deux rôles
- Peut modifier et supprimer des enregistrements
- Accède aux statistiques filtrées par opérateur
- Gère les comptes utilisateurs (via Django Admin)

### 2.2 Cas d'Utilisation Principaux

```
┌─────────────────────────────────────────────────────────────┐
│                    SYSTÈME MAGASIN CRÈME                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  MAGASINIER                   PRODUCTION                      │
│  ─────────────                ─────────────                   │
│  • Créer Réception             • Créer Ouverture Production    │
│  • Lister Réceptions           • Consulter Historique         │
│  • Transférer lot              • Voir Performance Analytics    │
│  • Voir Stock Actuel           • Voir Stock Fournisseur        │
│  • Tableau de Bord             • Tableau de Bord Prod.        │
│                                                               │
│  ADMIN                                                        │
│  ─────────                                                    │
│  • Modifier / Supprimer tout                                  │
│  • Gérer comptes utilisateurs                                 │
│  • Analytics filtrés                                          │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Flux Métier Principal

```
[Fournisseur]
     │
     ▼
[Réception Matière Première]  ←── Magasinier saisit :
     │                               - Codes lots (jusqu'à 10)
     │                               - Quantités par lot (kg)
     │                               - Date d'expiration
     │                               - Fournisseur
     ▼
[Stock Magasin] ────► Alertes expiration automatiques
     │
     ▼ (Transfert)
[Sortie Stock → Production]  ←── Magasinier transfère :
     │                               - Lot sélectionné
     │                               - Quantité (kg)
     │                               - Opérateur cible
     ▼
[Stock Production / Frigo]
     │
     ▼ (Utilisation)
[Ouverture Production]       ←── Opérateur enregistre :
     │                               - N° Ordre de Fabrication (OF)
     │                               - Produit fabriqué
     │                               - Ligne de production
     │                               - Shift (P1/P2/P3)
     │                               - Quantité pièces
     ▼
[Analytics & Rapports]
```

---

## 3. Architecture Générale du Projet

### 3.1 Structure des Répertoires

```
projet_creme/
├── manage.py                          # Point d'entrée Django CLI
├── db.sqlite3                         # Base de données SQLite (~208 Ko)
│
├── projet_creme/                      # Configuration Django
│   ├── settings.py                    # Paramètres de l'application
│   ├── urls.py                        # Routage URL racine
│   ├── wsgi.py                        # Interface WSGI (déploiement)
│   └── asgi.py                        # Interface ASGI (asynchrone)
│
└── gestion_stock/                     # Application principale
    ├── models.py                      # 5 modèles de données
    ├── views.py                       # ~35 fonctions/classes de vues
    ├── urls.py                        # URLs magasin
    ├── urls_production.py             # URLs production (namespace)
    ├── forms.py                       # 3 formulaires ModelForm
    ├── decorators.py                  # Décorateurs de permission
    ├── middleware.py                  # 2 middlewares personnalisés
    ├── signals.py                     # Signaux post_save
    ├── utils.py                       # Logique métier des lots
    ├── context_processors.py          # Contexte global templates
    ├── mixins_fixed.py                # Mixins pour vues CBV
    ├── admin.py                       # Configuration Django Admin
    │
    ├── migrations/                    # 9 fichiers de migration
    │   ├── 0001_initial.py
    │   ├── 0002_auto.py
    │   ├── 0003_add_profile_type_operateur.py
    │   ├── 0004_remove_profile_role.py
    │   ├── 0005_alter_fields.py
    │   ├── 0006_alter_reception_date_reception.py
    │   ├── 0007_add_per_lot_quantite.py
    │   ├── 0008_ouverture_quantite_integer.py
    │   └── 0009_of_unique.py
    │
    ├── static/
    │   └── css/
    │       ├── saas.css               # Design system (26.8 Ko)
    │       └── production-modal.css   # Styles modaux (1.2 Ko)
    │
    └── templates/                     # 32 templates HTML
        ├── base.html
        ├── landing.html
        ├── login.html
        ├── dashboard.html
        ├── data_performance.html
        ├── stock_actuel.html
        ├── [reception_*.html × 5]
        ├── [transfert_*.html × 5]
        ├── [ouverture_*.html × 4]
        ├── [profile*.html × 4]
        └── partials/
            ├── sidebar.html
            ├── sidebar_production.html
            ├── topbar.html
            └── _action_buttons.html
```

### 3.2 Pattern Architectural : MVT (Model-View-Template)

Django suit le patron **MVT** (Model-View-Template), variante du MVC :

| Couche | Rôle | Fichiers |
|--------|------|---------|
| **Model** | Définition des données et de la logique métier | `models.py`, `utils.py` |
| **View** | Traitement des requêtes HTTP, orchestration | `views.py` |
| **Template** | Présentation HTML dynamique | `templates/*.html` |
| **URL Dispatcher** | Routage URL → View | `urls.py`, `urls_production.py` |
| **Form** | Validation des données saisies | `forms.py` |
| **Middleware** | Interception transversale des requêtes | `middleware.py` |

---

## 4. Technologies Utilisées

### 4.1 Stack Technique

| Composant | Technologie | Version | Rôle |
|-----------|-------------|---------|------|
| **Framework Backend** | Django | 6.0.2 | Framework web Python |
| **Langage** | Python | 3.x | Langage backend |
| **Base de Données** | SQLite | 3.x | Stockage persistant |
| **ORM** | Django ORM | intégré | Abstraction BDD |
| **Frontend CSS** | Bootstrap | 5.3.3 | Framework UI responsive |
| **Icônes** | Bootstrap Icons | 1.11.3 | Bibliothèque d'icônes SVG |
| **CSS Custom** | Design System | — | saas.css (26.8 Ko) |
| **Graphiques** | Chart.js | 4.4.0 | Visualisations interactives |
| **Auth** | Django Auth | intégré | Authentification native |
| **Serveur Dev** | Django Dev Server | intégré | Développement local |

### 4.2 Justification des Choix Technologiques

#### Pourquoi Django ?
- **Batteries included** : ORM, formulaires, admin, auth — tout intégré
- **Rapidité de développement** : Scaffolding rapide, conventions fortes
- **Sécurité native** : Protection CSRF, SQL injection, XSS intégrée
- **Écosystème mature** : Documentation exhaustive, communauté active
- **Python** : Langage lisible, idéal pour la logique métier complexe

#### Pourquoi SQLite ?
- Adapté pour un déploiement **interne mono-site**
- **Zéro configuration** : aucun serveur à installer
- **Suffisant** pour la charge actuelle (< 100 utilisateurs)
- Migration vers PostgreSQL possible sans changer le code ORM

#### Pourquoi Bootstrap 5 ?
- **Responsive** par défaut (grille 12 colonnes)
- **Composants riches** : modales, cartes, tables, formulaires
- **Personnalisable** via variables CSS
- Cohérence visuelle avec Bootstrap Icons

---

## 5. Modélisation des Données (MCD/MLD)

### 5.1 Diagramme Entité-Relation

```
┌─────────────┐          ┌──────────────────┐          ┌─────────────┐
│    User      │          │     Profile       │          │ Fournisseur │
│  (Django)    │──1────1──│  (Extension User) │          │             │
│              │          │                  │          │ nom         │
│ username     │          │ user (FK)        │          │ adresse     │
│ password     │          │ matricule        │          │ telephone   │
│ ...          │          │ type_operateur   │          └──────┬──────┘
└─────────────┘          │ nom              │                 │
                          │ prenom           │                 │ 1
                          └────────┬─────────┘                 │
                                   │ 1                          │ N
                                   │                    ┌───────┴──────┐
                         N         │                    │  Reception   │
                    ┌──────────────┤                    │              │
                    │              │                    │ profile (FK) │◄──┐
                    │              │                    │ fournisseur  │   │
                    │              └───────────────────►│ (FK)         │   │
                    │                                   │ lot_code1-10 │   │
                    │                                   │ lot_quantite │   │
                    │                                   │ 1-10         │   │
                    │                                   │ quantite     │   │
                    │                                   │ date_exp.    │   │
                    │                                   └──────────────┘   │
                    │                                                       │
                    │     N        ┌──────────────────────┐                │
                    ├─────────────►│ SortieStockProduction│                │
                    │              │                      │                │
                    │              │ profile (FK)         │                │
                    │              │ numero_lot  ─────────┼────────────────┘
                    │              │ quantite             │  (référence logique)
                    │              │ date_heure           │
                    │              └──────────────────────┘
                    │
                    │     N        ┌──────────────────────┐
                    └─────────────►│ OuvertureProduction  │
                                   │                      │
                                   │ profile (FK)         │
                                   │ numero_lot ──────────┼── (référence logique)
                                   │ ligne_production     │
                                   │ date_heure_ouverture │
                                   │ numero_OF (unique)   │
                                   │ nom_produit          │
                                   │ quantite (pièces)    │
                                   │ shift (P1/P2/P3)     │
                                   └──────────────────────┘
```

### 5.2 Description Détaillée des Modèles

---

#### Modèle 1 : `Profile`

Extension du modèle `User` natif de Django.

| Champ | Type | Contraintes | Description |
|-------|------|-------------|-------------|
| `id` | BigAutoField | PK, auto | Identifiant unique |
| `user` | OneToOneField(User) | CASCADE, unique | Lien vers compte Django |
| `matricule` | CharField(50) | UNIQUE, NOT NULL | Matricule opérateur |
| `type_operateur` | CharField(20) | CHOICES | Rôle : admin/magasin/production |
| `nom` | CharField(100) | blank=True | Nom de famille |
| `prenom` | CharField(100) | blank=True | Prénom |

**Choix pour `type_operateur` :**
```python
TYPE_CHOICES = [
    ('admin', 'Administrateur'),
    ('magasin', 'Magasinier'),
    ('production', 'Production'),
]
```

**Signal associé :** Création automatique d'un `Profile` à chaque création d'un `User` Django.

---

#### Modèle 2 : `Fournisseur`

Référentiel des fournisseurs de matières premières.

| Champ | Type | Contraintes | Description |
|-------|------|-------------|-------------|
| `id` | BigAutoField | PK, auto | Identifiant unique |
| `nom` | CharField(200) | NOT NULL | Raison sociale |
| `adresse` | CharField(255) | NOT NULL | Adresse postale |
| `telephone` | CharField(20) | NOT NULL | Numéro de contact |

---

#### Modèle 3 : `Reception`

Enregistrement des arrivées de matières premières au magasin.

| Champ | Type | Contraintes | Description |
|-------|------|-------------|-------------|
| `id` | BigAutoField | PK, auto | Identifiant unique |
| `profile` | ForeignKey(Profile) | CASCADE, related='receptions' | Opérateur ayant saisi |
| `fournisseur` | ForeignKey(Fournisseur) | CASCADE | Fournisseur source |
| `date_reception` | DateTimeField | default=timezone.now | Date/heure de réception |
| `date_expiration` | DateField | NOT NULL | Date de péremption du lot |
| `quantite` | DecimalField(10,3) | default=0.500 | Quantité totale (kg) |
| `lot_code1` ... `lot_code10` | CharField(50) | blank=True | Code lot N (1 à 10) |
| `lot_quantite1` ... `lot_quantite10` | DecimalField(10,3) | default=0 | Quantité lot N (kg) |

**Propriété calculée :**
```python
@property
def lot_reference(self):
    # Retourne : "LOT-<id>-01" (identifiant canonique du premier lot)
```

**Particularité importante :** Une seule réception peut contenir **jusqu'à 10 lots distincts**, chacun avec son propre code et sa propre quantité. Cette conception permet de regrouper plusieurs livraisons en une seule opération de saisie.

---

#### Modèle 4 : `SortieStockProduction`

Enregistrement des transferts du stock magasin vers la zone production.

| Champ | Type | Contraintes | Description |
|-------|------|-------------|-------------|
| `id` | BigAutoField | PK, auto | Identifiant unique |
| `profile` | ForeignKey(Profile) | CASCADE, related='sorties' | Opérateur ayant transféré |
| `date_heure` | DateTimeField | auto_now_add=True | Date/heure du transfert |
| `numero_lot` | CharField(50) | NOT NULL | Identifiant canonique du lot |
| `quantite` | DecimalField(10,3) | default=0.500 | Quantité transférée (kg) |

**Calcul du stock disponible en magasin :**
```
Dispo_magasin = Reception.lot_quantiteN - SUM(SortieStockProduction.quantite WHERE numero_lot = LOT-X-N)
```

---

#### Modèle 5 : `OuvertureProduction`

Enregistrement des démarrages de lots en production.

| Champ | Type | Contraintes | Description |
|-------|------|-------------|-------------|
| `id` | BigAutoField | PK, auto | Identifiant unique |
| `profile` | ForeignKey(Profile) | CASCADE, related='ouvertures' | Opérateur de production |
| `ligne_production` | CharField(100) | NOT NULL | Ligne de production |
| `date_heure_ouverture` | DateTimeField | NOT NULL | Date/heure de démarrage |
| `numero_lot` | CharField(50) | NOT NULL | Lot utilisé |
| `numero_ordre_fabrication` | CharField(100) | UNIQUE, NOT NULL | N° OF |
| `nom_produit` | CharField(150) | NOT NULL | Produit fabriqué |
| `quantite` | IntegerField | default=1 | Quantité produite (pièces) |
| `shift` | CharField(2) | CHOICES | Poste : P1/P2/P3 |

**Calcul du stock disponible en production :**
```
Dispo_production = SUM(SortieStockProduction.quantite) - SUM(OuvertureProduction.quantite)
```

---

### 5.3 Évolution du Schéma (Migrations)

| Migration | Date | Opération |
|-----------|------|-----------|
| 0001_initial | 03/04/2026 | Création de tous les modèles |
| 0003 | 03/04/2026 | Ajout `type_operateur`, `nom`, `prenom` à Profile |
| 0004 | 03/04/2026 | Suppression champ `role` obsolète |
| 0005 | 03/04/2026 | Passage BigAutoField + 3 choix de rôles |
| 0006 | 07/04/2026 | Changement default `date_reception` → `timezone.now` |
| **0007** | **16/04/2026** | **Ajout `lot_quantite1-10` (suivi individuel par lot)** |
| 0008 | 22/04/2026 | `OuvertureProduction.quantite` : Decimal → Integer |
| **0009** | **22/04/2026** | **Contrainte UNIQUE sur `numero_ordre_fabrication`** |
| **0010** | **05/05/2026** | **Création du modèle `LotReception` (lots normalisés)** |
| **0011** | **05/05/2026** | **Migration des lots existants vers `LotReception`** |

La migration **0007** représente l'évolution majeure du schéma : passage d'une quantité globale par réception à un suivi individuel par lot, permettant une traçabilité beaucoup plus fine.

Les migrations **0010–0011** introduisent le modèle `LotReception` qui normalise les lots (précédemment stockés dans les champs `lot_code1-10` / `lot_quantite1-10` de `Reception`) en lignes distinctes, facilitant les jointures et les calculs de disponibilité.

---

## 6. Architecture Logicielle — Vues et URLs

### 6.1 Routage URL Principal

```python
# projet_creme/urls.py (URL Racine)
urlpatterns = [
    path('',              landing,           name='landing'),
    path('login/',        login_view,        name='login'),
    path('admin/',        admin.site.urls),
    path('gestion_stock/', include('gestion_stock.urls')),
    path('gestion_stock/', include('gestion_stock.urls_production')),
]
```

### 6.2 URLs Magasin (`gestion_stock/urls.py`)

| URL | Vue | Nom | Accès |
|-----|-----|-----|-------|
| `magasin/` | `dashboard` | `dashboard` | magasin, admin |
| `reception/` | `reception_list` | `reception_list` | magasin, admin |
| `reception/new/` | `ReceptionCreateView` | `reception_new` | magasin, admin |
| `reception/<id>/` | `reception_detail` | `reception_detail` | magasin, admin |
| `reception/<id>/update/` | `ReceptionUpdateView` | `reception_update` | admin |
| `reception/<id>/delete/` | `reception_delete` | `reception_delete` | admin |
| `transfert/` | `transfert_create` | `transfert_create` | magasin, admin |
| `transfert/list/` | `transfert_list` | `transfert_list` | magasin, admin |
| `transfert/<id>/` | `transfert_detail` | `transfert_detail` | magasin, admin |
| `transfert/<id>/update/` | `transfert_update` | `transfert_update` | admin |
| `transfert/<id>/delete/` | `transfert_delete` | `transfert_delete` | admin |
| `stock/` | `stock_actuel` | `stock` | magasin, admin |
| `profile/` | `profile_list` | `profile` | magasin, admin |
| `profile/<id>/` | `profile_detail` | `profile_detail` | magasin, admin |
| `logout/` | `LogoutView` | `logout` | tous |

### 6.3 URLs Production (`gestion_stock/urls_production.py`, namespace=`production`)

| URL | Vue | Nom complet | Accès |
|-----|-----|-------------|-------|
| `production/` | `production` | `production:index` | production, admin |
| `production/data_performance/` | `data_performance` | `production:data_performance` | production, admin |
| `production/stock/` | `stock_actuel_production` | `production:stock` | production, admin |
| `production/historique/` | `historique` | `production:historique` | production, admin |
| `production/historique/<id>/` | `ouverture_detail` | `production:ouverture_detail` | production, admin |
| `production/historique/<id>/modifier/` | `ouverture_update` | — | admin |
| `production/historique/<id>/supprimer/` | `ouverture_delete` | — | admin |
| `production/nouvelle/` | `nouvelle_production` | `production:nouvelle_production` | production, admin |
| `production/ouverture/new/` | `OuvertureProductionCreateView` | — | production, admin |
| `production/ouverture/list/` | `OuvertureProductionListView` | — | production, admin |
| `production/profile/` | `profile_production` | `production:profile` | production, admin |
| `production/profile/<id>/` | `profile_production_detail` | — | production, admin |

### 6.4 Vues Importantes — Description Détaillée

#### `dashboard(request)` — Tableau de Bord Magasin
```python
@magasin_required
def dashboard(request):
    """
    Vue principale du magasin.
    
    Calculs effectués :
    - total_recu    = SUM(Reception.quantite)
    - total_envoye  = SUM(SortieStockProduction.quantite)
    - stock_dispo   = total_recu - total_envoye
    - utilisation_pct = (total_envoye / total_recu) × 100
    
    - receptions_mois = COUNT(Reception WHERE date >= 1er du mois)
    - transfers_mois  = COUNT(SortieStockProduction WHERE date >= 1er du mois)
    - trend = variation % par rapport au mois précédent
    
    - lots_expires_count  = COUNT(Reception WHERE date_exp < today)
    - lots_warning_count  = COUNT(Reception WHERE date_exp BETWEEN today AND today+7)
    - quantite_expiree    = SUM(quantite) des lots expirés
    - quantite_warning    = SUM(quantite) des lots en alerte
    
    - chart_labels / chart_rec / chart_trans : données 6 derniers mois
    
    Templates : dashboard.html
    """
```

#### `transfert_create(request)` — Transfert Stock → Production
```python
@magasin_required
def transfert_create(request):
    """
    Processus de transfert :
    
    1. Construction dynamique des choix de lots :
       Pour chaque lot avec disponible > 0 :
       - disponible = lot_quantite - SUM(sorties pour ce lot)
       - Affiche : status (⛔/⚠/✅) + code lot + disponible + date exp
    
    2. Parsing du formulaire multi-lots (JavaScript side) :
       - numero_lot_0, quantite_0
       - numero_lot_1, quantite_1
       - ...
    
    3. Validation :
       - Lot existe ? → erreur
       - Lot non expiré ? → erreur
       - quantite ≤ disponible ? → erreur
    
    4. Création en transaction atomique :
       SortieStockProduction.objects.create(
           profile=..., numero_lot=..., quantite=...
       )
    """
```

#### `data_performance(request)` — Analytics Production
```python
@production_required
@never_cache
def data_performance(request):
    """
    Moteur analytique :
    
    Filtres GET :
    - periode: all | today | 7j | 30j
    - operateur: ID opérateur (admin seulement)
    
    KPIs calculés :
    - today_total   : SUM(quantite) des ouvertures aujourd'hui
    - today_count   : COUNT des ouvertures aujourd'hui
    - period_total  : SUM(quantite) sur la période
    - period_count  : COUNT sur la période
    - top_shift     : shift avec SUM(quantite) max
    - top_product   : produit avec SUM(quantite) max
    
    Agrégations pour graphiques :
    - Par shift (P1/P2/P3) : total + count
    - Par ligne (top 8)    : total + count
    - Par produit (top 8)  : total + count
    - Par mois (6 mois)    : tendance consommation
    
    Données pour tableaux :
    - by_op : par opérateur (total, count, %)
    
    Calculateur produit :
    - Si ?produit=<id> → retourne total pour ce produit
    """
```

---

## 7. Formulaires et Validation

### 7.1 `ReceptionForm` — Saisie de Réception

```python
class ReceptionForm(forms.ModelForm):
    class Meta:
        model  = Reception
        fields = ['fournisseur', 'date_expiration', 'quantite',
                  'lot_code1', ..., 'lot_code10',
                  'lot_quantite1', ..., 'lot_quantite10']
    
    def clean_date_expiration(self):
        # Règle : la date d'expiration ne peut pas être dans le passé
        if value < date.today():
            raise ValidationError("La date d'expiration ne peut pas être passée.")
        return value
    
    def clean(self):
        # Règle 1 : Pour chaque lot avec un code, quantité > 0 obligatoire
        # Règle 2 : Au moins un lot valide requis
        # Règle 3 : La somme des quantités alimente quantite (champ legacy)
        ...
```

**Validation Visuelle :**
- Date minimum = aujourd'hui (attribut HTML `min`)
- Quantités : `step=0.001`, `min=0.001`
- Jusqu'à 10 lots ajoutables dynamiquement (JavaScript)

### 7.2 `SortieStockProductionForm` — Transfert

```python
class SortieStockProductionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Construction dynamique des choix de lots disponibles
        # Format affiché : "LOT-5-03 | Dispo: 1.250 kg | Exp: 25/04/2026 | ✅ OK"
        
        lot_choices = []
        for lot in available_lots:
            disponible = lot_total_received(lot) - lot_total_sent(lot)
            if disponible > 0:
                status = lot_expiration_info(lot)['label']
                lot_choices.append((lot_id, f"{lot_id} | Dispo: {disponible:.3f} kg | {status}"))
    
    def clean(self):
        # Règle 1 : Le lot doit exister
        # Règle 2 : Le lot ne doit pas être expiré
        # Règle 3 : quantite ≤ quantite disponible
        ...
```

### 7.3 `OuvertureProductionForm` — Ouverture Production

```python
class OuvertureProductionForm(forms.ModelForm):

    numero_lot = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtre : uniquement opérateurs de production
        self.fields['profile'].queryset = Profile.objects.filter(
            type_operateur='production'
        )

        # ── Filtrage intelligent des lots disponibles ──────────────────
        #
        # Règle métier : chaque lot physique est ouvert une seule fois.
        # Le formulaire n'affiche donc que les lots qui satisfont les
        # trois conditions suivantes :
        #
        #   1. Transféré vers la production
        #      (enregistrement SortieStockProduction existant)
        #
        #   2. Non encore consommé en production
        #      (aucun OuvertureProduction ne référence ce lot_id)
        #      → Exception : en mode édition, le lot de l'enregistrement
        #        courant reste toujours visible pour permettre sa
        #        conservation ou sa modification.
        #
        #   3. Non expiré
        #      (date_expiration ≥ aujourd'hui)

        already_used = set(
            OuvertureProduction.objects.exclude(numero_lot='')
            .values_list('numero_lot', flat=True)
        )
        # En mode édition, le lot de CET enregistrement reste visible
        current_lot = (
            self.instance.numero_lot
            if self.instance and self.instance.pk and self.instance.numero_lot
            else None
        )

        choices = [('', '--- Sélectionner un lot transféré ---')]
        for lot_id in SortieStockProduction.objects.values_list(
            'numero_lot', flat=True
        ).distinct():
            if not lot_id:
                continue
            if lot_id in already_used and lot_id != current_lot:
                continue                         # déjà consommé → masqué
            jours_restant = ...                  # calcul via LotReception
            if jours_restant is not None and jours_restant < 0:
                continue                         # expiré → masqué
            choices.append((lot_id, label))

        self.fields['numero_lot'].choices = choices

    def clean_numero_ordre_fabrication(self):
        # Règle : N° OF doit être UNIQUE (contrainte BDD + validation form)
        of = self.cleaned_data.get('numero_ordre_fabrication', '').strip()
        qs = OuvertureProduction.objects.filter(numero_ordre_fabrication=of)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError(f"L'OF « {of} » existe déjà.")
        return of
```

**Comportement du filtre selon le contexte :**

| Contexte | Lot déjà consommé | Lot expiré | Lot disponible |
|----------|:-----------------:|:----------:|:--------------:|
| Nouvelle ouverture | ❌ masqué | ❌ masqué | ✅ affiché |
| Modifier (autre lot) | ❌ masqué | ❌ masqué | ✅ affiché |
| Modifier (lot courant) | ✅ **toujours visible** | ✅ **toujours visible** | ✅ affiché |

---

## 8. Système d'Authentification et d'Autorisation

### 8.1 Processus d'Authentification

```
Requête /login/
    │
    ▼
Déjà authentifié ?
    ├── OUI → Redirection selon type_operateur :
    │         - magasin    → /gestion_stock/magasin/
    │         - production → /gestion_stock/production/data_performance/
    │         - admin      → /gestion_stock/production/data_performance/
    │
    └── NON → Afficher formulaire login
              │
              ▼ (POST matricule + mot de passe)
         authenticate(username=matricule, password=password)
              │
         Succès ? ──► login(request, user)
              │              │
              │              ▼ Redirection selon rôle
              └── Échec → Message d'erreur → Réaffichage formulaire
```

### 8.2 Couches d'Autorisation

L'autorisation est implémentée à **trois niveaux** :

#### Niveau 1 : Décorateurs de vues (Function-Based Views)

```python
@magasin_required
def dashboard(request):
    """
    Vérifie :
    1. user.is_authenticated            → sinon : redirect 'login'
    2. NOT user.is_superuser             → sinon : redirect '/admin/'
    3. hasattr(user, 'profile')          → sinon : redirect 'login'
    4. profile.type_operateur in         → sinon : erreur + redirect 'login'
       ['admin', 'magasin']
    """

@admin_required
def reception_delete(request, pk):
    """
    Même logique mais restreint à 'admin' uniquement.
    Retourne HTTP 403 si profil existe mais rôle incorrect.
    """

@production_required
def data_performance(request):
    """
    Autorise : production + admin
    Refuse : superuser, magasin, sans profil
    """
```

#### Niveau 2 : Middleware global

```python
class MagasinAccessMiddleware:
    """
    Appliqué à TOUTES les requêtes /gestion_stock/*
    
    Logique :
    - Superuser → redirect /admin/
    - Pas de profil → erreur + redirect login
    - /gestion_stock/production/* → réservé production+admin
    - Autres URLs → réservé magasin+admin
    """
```

#### Niveau 3 : Mixins pour CBV

```python
class MagasinAccessMixin(PermissionMixin):
    """Pour CreateView, UpdateView → magasin + admin"""

class AdminRequiredMixin(PermissionMixin):
    """Pour les vues de modification → admin uniquement"""

class ProductionAccessMixin(LoginRequiredMixin):
    """Pour les vues production → production + admin"""
```

### 8.3 Matrice des Permissions

| Fonctionnalité | Magasinier | Production | Admin |
|----------------|:----------:|:----------:|:-----:|
| Voir dashboard magasin | ✅ | ❌ | ✅ |
| Créer réception | ✅ | ❌ | ✅ |
| Modifier réception | ❌ | ❌ | ✅ |
| Supprimer réception | ❌ | ❌ | ✅ |
| Créer transfert | ✅ | ❌ | ✅ |
| Voir stock actuel (magasin) | ✅ | ❌ | ✅ |
| Voir dashboard production | ❌ | ✅ | ✅ |
| Créer ouverture production | ❌ | ✅ | ✅ |
| Voir analytics production | ❌ | ✅ | ✅ |
| Analytics filtrés par opérateur | ❌ | ❌ | ✅ |
| Modifier/Supprimer tout | ❌ | ❌ | ✅ |
| Django Admin | ❌ | ❌ | ✅ |

---

## 9. Middleware et Sécurité

### 9.1 `NoCacheAuthMiddleware` — Prévention du Cache

```python
class NoCacheAuthMiddleware:
    """
    Problème résolu : après logout, l'utilisateur pouvait
    revenir aux pages protégées via le bouton "Précédent"
    du navigateur (cache browser).
    
    Solution : ajout de headers HTTP no-cache sur toutes
    les pages /gestion_stock/* pour les utilisateurs connectés.
    
    Headers ajoutés :
    - Cache-Control: no-cache, no-store, must-revalidate, private, max-age=0
    - Pragma: no-cache
    - Expires: 0
    """
```

**Complément côté JavaScript (base.html) :**
```javascript
window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
        // Page chargée depuis bfcache (bouton Précédent)
        window.location.replace('/');  // Force rechargement
    }
});
```

### 9.2 `MagasinAccessMiddleware` — Contrôle d'Accès par URL

```python
class MagasinAccessMiddleware:
    """
    Couche de sécurité additionnelle indépendante des décorateurs.
    Protège toutes les routes /gestion_stock/* au niveau middleware.
    
    Avantage : même si un décorateur est oublié sur une vue,
    le middleware bloque l'accès inapproprié.
    """
```

### 9.3 Autres Mesures de Sécurité

| Mesure | Implémentation |
|--------|----------------|
| Protection CSRF | `@csrf_protect` + `{% csrf_token %}` dans tous les forms |
| Injection SQL | Django ORM (requêtes paramétrées automatiques) |
| XSS | Django templates (échappement HTML automatique) |
| Clickjacking | `XFrameOptionsMiddleware` (Django natif) |
| Session sécurisée | `SESSION_COOKIE_SAMESITE = "Lax"` |
| Pas de superuser dans l'app | Middleware bloque superuser → /admin/ |

---

## 10. Logique Métier — Gestion des Lots

### 10.1 Système d'Identification des Lots

Chaque lot est identifié par un **identifiant canonique** unique :

```
Format : LOT-<reception_id>-<lot_index>

Exemples :
  LOT-5-01   → Réception N°5, premier lot (lot_code1)
  LOT-5-02   → Réception N°5, deuxième lot (lot_code2)
  LOT-12-03  → Réception N°12, troisième lot (lot_code3)

Avantage : Traçabilité complète même si le code fournisseur change.
           L'identifiant est immuable une fois créé.
```

### 10.2 Fonctions Utilitaires (`utils.py`)

```python
# Conversion identifiant → code fournisseur
lot_id_to_code("LOT-5-03") → "ADE-2026-123"  # lot_code3 de Reception N°5

# Informations d'expiration
lot_expiration_info("LOT-5-03") → {
    'date_expiration': date(2026, 5, 25),
    'jours_restant': 33,
    'status': 'ok',         # 'ok' | 'warning' | 'expired' | 'unknown'
    'label': '✅ OK (33j)'
}

# Calcul des disponibilités
lot_total_received("LOT-5-03")              → Decimal('2.500')   # kg reçus
lot_total_sent_to_production("LOT-5-03")    → Decimal('1.000')   # kg transférés
lot_total_opened_in_production("LOT-5-03")  → Decimal('0.500')   # kg utilisés

# Disponible magasin = 2.500 - 1.000 = 1.500 kg
# Disponible production = 1.000 - 0.500 = 0.500 kg
```

### 10.3 Règles Métier sur les Lots

```
RÈGLE 1 : Traçabilité obligatoire
  Un lot transféré en production DOIT référencer un lot de réception existant.

RÈGLE 2 : Anti-expiration
  Il est INTERDIT de transférer un lot expiré (validé en formulaire + formulaire).
  
RÈGLE 3 : Cohérence des quantités
  quantite_transfert ≤ quantite_disponible_magasin
  (validé dynamiquement dans le formulaire de transfert)

RÈGLE 4 : Unicité des ordres de fabrication
  Chaque OuvertureProduction doit avoir un N° OF unique
  (contrainte BDD UNIQUE + validation Django)

RÈGLE 5 : Alertes automatiques
  Si date_expiration - aujourd'hui < 0  → EXPIRÉ (rouge)
  Si date_expiration - aujourd'hui ≤ 7  → AVERTISSEMENT (ambre)
  Sinon                                  → OK (vert)
```

---

## 11. Interfaces Utilisateur

### 11.1 Design System

L'application dispose d'un **système de design cohérent** défini dans `saas.css` (26.8 Ko) :

#### Palette de Couleurs

| Rôle | Couleur | Valeur HEX | Utilisation |
|------|---------|------------|-------------|
| Primaire Magasin | Bleu | `#2563eb` | Actions, KPIs magasin |
| Primaire Production | Ambre | `#d97706` | Actions, KPIs production |
| Succès | Vert | `#059669` | Status OK, confirmations |
| Danger | Rouge | `#dc2626` | Erreurs, périmés |
| Avertissement | Jaune | `#d97706` | Alertes, warnings |
| Texte principal | Très sombre | `#0f172a` | Titres |
| Texte secondaire | Gris | `#64748b` | Labels, metadata |
| Fond | Très clair | `#f1f5f9` | Background app |
| Card | Blanc | `#ffffff` | Cartes, panneaux |

#### Composants Réutilisables

```
.kpi-card        → Carte indicateur de performance
.kpi-grid        → Grille responsive 7 colonnes (→ 4 → 3 → 2)
.viz-card        → Carte graphique/tableau
.db-header       → Bannière d'en-tête dashboard (gradient)
.dt              → Table de données stylisée
.dt-badge        → Badge coloré dans les tables
.page-hd         → En-tête de page (titre + actions)
.form-card       → Conteneur de formulaire
.alert-strip     → Bande d'alerte colorée
.pill            → Badge inline compact
.trend-up/down   → Indicateur de tendance ▲/▼
.util-track      → Barre de progression
```

### 11.2 Architecture des Templates

```
base.html (Layout principal)
├── Sidebar fixe (240px) :
│   ├── sidebar.html        (Magasin — thème bleu)
│   └── sidebar_production.html (Production — thème ambre)
├── Topbar (60px) :
│   └── topbar.html         (Nom app + User dropdown)
└── Content (zone principale) :
    └── {% block content %}
        └── [page spécifique]
```

### 11.3 Pages Principales

#### Dashboard Magasin (`dashboard.html`)
- **Bannière gradient** : titre + date (dark navy → indigo)
- **7 KPI Cards** :
  1. Stock disponible (kg)
  2. Total reçu (kg)
  3. Taux utilisation (%)
  4. Réceptions ce mois / trend
  5. Transferts ce mois / trend
  6. Quantité expirée (kg)
  7. Quantité en alerte ≤7j (kg)
- **Graphique barres** : 6 mois de réceptions vs transferts
- **Graphique donut** : Répartition disponible/transféré
- **Tables** : 8 dernières réceptions + 8 derniers transferts
- **Notifications toast** : apparition automatique des alertes
- **Son** : notification sonore en cas de lots expirés/en alerte

#### Analytics Production (`data_performance.html`)
- Filtres période et opérateur
- KPIs production du jour et de la période
- Graphique tendance 6 mois
- Tableaux : par shift, par ligne, par produit, par opérateur
- Calculateur de consommation par produit

#### Formulaire de Réception (`reception_form.html`)
- Sélection fournisseur (dropdown)
- Saisie date d'expiration (datepicker, min=aujourd'hui)
- Ajout dynamique de lots (JavaScript, jusqu'à 10)
- Champs : code lot + quantité par lot

### 11.4 Système de Notifications

**Notifications Toast (dashboard)** :
```
┌──────────────────────────────────────┐
│ ✕  3 lots expirés               [×] │  ← Rouge, slide-in droite
│    LOT-REC-5    13/04/2026           │
│    LOT-REC-6    13/04/2026           │
│    LOT-REC-7    15/04/2026           │
└──────────────────────────────────────┘
┌──────────────────────────────────────┐
│ ⚠  4 lots expirent dans ≤ 7j   [×] │  ← Ambre, slide-in droite
│    LOT-REC-1    25/04/2026           │
│    ...                               │
└──────────────────────────────────────┘
```

**Son** (Web Audio API) :
- Lots expirés : 2 bips descendants 880Hz → 660Hz
- Avertissement : 1 bip net à 784Hz

---

## 12. Tableaux de Bord et Analytiques

### 12.1 KPIs Calculés en Temps Réel

#### Magasin (dashboard)
```
KPI                 Formule
─────────────────────────────────────────────────────────
Stock disponible  = SUM(Reception.quantite)
                  - SUM(SortieStockProduction.quantite)

Total reçu        = SUM(Reception.quantite)

Total envoyé      = SUM(SortieStockProduction.quantite)

Taux utilisation  = (total_envoye / total_recu) × 100

Réceptions/mois   = COUNT(Reception WHERE date_rec >= 1er mois)

Transferts/mois   = COUNT(SortieStock WHERE date >= 1er mois)

Trend %           = ((ce_mois - mois_precedent) / mois_precedent) × 100

Qté expirée       = SUM(quantite WHERE date_exp < today)

Qté alerte ≤7j    = SUM(quantite WHERE date_exp BETWEEN today AND today+7)
```

#### Production (data_performance)
```
KPI                    Formule (sur période filtrée)
─────────────────────────────────────────────────────────────────
Production aujourd'hui = SUM(OuvertureProduction.quantite WHERE date = today)

Production période     = SUM(OuvertureProduction.quantite WHERE date IN période)

Top shift              = MAX(SUM(quantite) GROUP BY shift)

Top produit            = MAX(SUM(quantite) GROUP BY nom_produit)

Par opérateur %        = (total_op / total_global) × 100
```

### 12.2 Graphiques Implémentés

| Graphique | Type | Données | Librairie |
|-----------|------|---------|-----------|
| Évolution mensuelle | Barres groupées + gradient | 6 derniers mois (réceptions vs transferts kg) | Chart.js 4.4 |
| Répartition stock | Donut (anneau) | Disponible vs Transféré | Chart.js 4.4 |
| Tendance production | Ligne | 6 mois consommation | Chart.js 4.4 |
| Par shift | Barres horizontales | P1/P2/P3 totaux | Chart.js 4.4 |
| Top lignes | Barres | Top 8 lignes de production | Chart.js 4.4 |
| Top produits | Barres | Top 8 produits | Chart.js 4.4 |

---

## 13. Tests et Déploiement

### 13.1 Lancement du Projet (Développement)

```bash
# Prérequis : Python 3.x, pip

# 1. Installer les dépendances
pip install django

# 2. Appliquer les migrations
python manage.py migrate

# 3. Créer un superutilisateur (admin Django)
python manage.py createsuperuser

# 4. Collecter les fichiers statiques (si nécessaire)
python manage.py collectstatic

# 5. Lancer le serveur
python manage.py runserver

# 6. Accéder à l'application
# http://127.0.0.1:8000/
```

### 13.2 Configuration Clé (`settings.py`)

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gestion_stock',        # Application principale
]

MIDDLEWARE = [
    # ... middleware Django standard ...
    'gestion_stock.middleware.NoCacheAuthMiddleware',    # Anti-cache
    'gestion_stock.middleware.MagasinAccessMiddleware',  # Contrôle d'accès
    # ...
]

TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'gestion_stock.context_processors.role_flags',  # Flags de navigation
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = 'auth.User'   # Django User natif
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "gestion_stock" / "static"]
```

### 13.3 Procédure de Création d'Opérateurs

Via **Django Admin** (`/admin/`) :
1. Créer un `User` (username = matricule, mot de passe)
2. Le signal `post_save` crée automatiquement un `Profile` associé
3. Accéder à `Profile` via l'admin → modifier `type_operateur` (admin/magasin/production) et renseigner `nom`, `prenom`

---

## 14. Bilan et Perspectives

### 14.1 Résultats Obtenus

| Objectif initial | Réalisé | Commentaire |
|------------------|---------|-------------|
| Digitalisation des réceptions | ✅ | Multi-lots, up to 10 lots/réception |
| Traçabilité complète | ✅ | Système d'ID canonique LOT-X-N |
| Alertes péremption | ✅ | Visuelles + sonores + notifications |
| Analytics production | ✅ | Shift, produit, ligne, opérateur |
| Contrôle d'accès par rôle | ✅ | 3 couches : décorateurs + middleware + mixins |
| Interface professionnelle | ✅ | Design system SaaS + dashboard BI |
| Sécurité anti-cache | ✅ | Headers + événement pageshow |

### 14.2 Chiffres du Projet

| Métrique | Valeur |
|----------|--------|
| Nombre de modèles Django | 5 |
| Nombre de vues (functions + CBV) | ~35 |
| Nombre de templates HTML | 32 |
| Nombre de formulaires | 3 |
| Nombre de migrations | 9 |
| Taille du CSS personnalisé | 26.8 Ko |
| Lignes de code Python estimées | ~2 500+ |
| Lignes de code HTML estimées | ~3 000+ |
| Rôles utilisateurs | 3 |
| Postes de travail (shifts) | 3 (P1/P2/P3) |
| Graphiques interactifs | 6 |
| Lots max par réception | 10 |

### 14.3 Difficultés Rencontrées

1. **Gestion multi-lots** : La conception initiale (1 lot = 1 réception) s'est avérée insuffisante. La migration 0007 a ajouté les champs `lot_quantite1-10`, nécessitant une refactorisation de la logique de calcul.

2. **Système d'identification des lots** : Les codes fournisseurs n'étant pas toujours uniques (même code chez différents fournisseurs), un système d'identifiant canonique `LOT-<id>-<nn>` a été conçu et implémenté dans `utils.py`.

3. **Sécurité du cache navigateur** : Le bouton "Précédent" permettait d'accéder aux pages protégées après logout. Solution combinée : headers HTTP `no-cache` + JavaScript `pageshow`.

4. **Permissions multi-couches** : Assurer une cohérence entre les décorateurs, le middleware et les mixins CBV sans duplication ni oubli.

5. **Filtrage des lots dans `OuvertureProductionForm`** : Le filtre initial comparait la quantité transférée (en **kg**, `DecimalField`) avec la quantité produite (en **pièces**, `IntegerField`), produisant des disponibilités négatives absurdes (ex. : `0.500 kg − 1000 pièces = −999.5`). Ce bug rendait la liste des lots vide après la première ouverture. La solution adoptée repose sur un filtre ensembliste : on exclut les lots déjà présents dans `OuvertureProduction`, en préservant le lot de l'enregistrement en cours d'édition.

### 14.4 Améliorations Futures

| Priorité | Amélioration | Justification |
|----------|-------------|---------------|
| 🔴 Haute | Migration vers PostgreSQL | SQLite insuffisant en production multi-utilisateurs |
| 🔴 Haute | Export CSV/PDF des rapports | Besoin métier fréquent pour archivage |
| 🟡 Moyenne | Alertes email automatiques | Notifications proactives pour les responsables |
| 🟡 Moyenne | API REST (Django REST Framework) | Intégration avec systèmes ERP tiers |
| 🟡 Moyenne | Scan codes-barres | Accélération de la saisie des lots |
| 🟢 Basse | Application mobile | Accès terrain pour les opérateurs |
| 🟢 Basse | Log d'audit complet | Conformité et traçabilité réglementaire |
| 🟢 Basse | Tableau de bord temps réel (WebSocket) | Mise à jour automatique sans rechargement |

---

## ANNEXES

### Annexe A : Identifiants de Connexion (Environnement de Test)

| Matricule | Rôle | Interface |
|-----------|------|-----------|
| `admin` (superuser Django) | Admin complet | /admin/ |
| (créés via admin) | magasin | /gestion_stock/magasin/ |
| (créés via admin) | production | /gestion_stock/production/data_performance/ |

### Annexe B : Stack de Dépendances

```
django>=6.0.2
# Frontend CDN (pas de package Python) :
# - Bootstrap 5.3.3
# - Bootstrap Icons 1.11.3
# - Chart.js 4.4.0
```

### Annexe C : Variables d'Environnement

```bash
DJANGO_SECRET_KEY=<clé-secrète>
DJANGO_DEBUG=True          # False en production
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

### Annexe D : Commandes Utiles

```bash
# Créer une migration après modification de models.py
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Shell Django interactif
python manage.py shell

# Vérifier la configuration
python manage.py check

# Lancer avec port personnalisé
python manage.py runserver 0.0.0.0:8080
```

---

*Document généré le 22/04/2026 — Projet de Fin d'Études*
*Framework : Django 6.0.2 | Base de données : SQLite | Frontend : Bootstrap 5.3.3*
